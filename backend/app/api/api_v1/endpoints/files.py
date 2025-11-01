"""
文件管理API端点
"""
import logging
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.permissions import has_permission
from app.core.exceptions import PermissionException, ValidationException
from app.models.user import User
from app.schemas.file import (
    FileUploadRequest, FileUploadResponse, FileDownloadRequest, FileDeleteRequest,
    FileListRequest, FileListResponse, FileInfo, FileSyncRequest, FileBackupRequest,
    FilePresignedUrlRequest, FileStorageSwitchRequest, FileStorageStatus,
    FileOperationResponse, FileUploadProgress, FileChunkUploadRequest, FileChunkUploadResponse
)
from app.utils.file import FileManager

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

# 全局文件管理器实例
file_manager = FileManager()

# 文件上传进度存储
upload_progress: Dict[str, FileUploadProgress] = {}


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prefix: str = Form(default="uploads"),
    backup_to_cloud: bool = Form(default=True),
    current_user: User = Depends(get_current_user)
):
    """
    上传文件
    
    需要权限: file:upload
    """
    # 检查权限
    if not has_permission(current_user, "file:upload"):
        raise PermissionException("没有上传文件的权限")
    
    try:
        # 生成文件ID用于跟踪进度
        file_id = str(uuid.uuid4())
        
        # 创建进度记录
        progress = FileUploadProgress(
            file_id=file_id,
            filename=file.filename,
            total_size=file.size or 0,
            uploaded_size=0,
            progress=0.0,
            status="uploading",
            message="开始上传",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        upload_progress[file_id] = progress
        
        # 上传文件
        result = await file_manager.save_file(
            file=file,
            prefix=prefix,
            backup_to_cloud=backup_to_cloud
        )
        
        # 更新进度
        progress.uploaded_size = result["file_size"]
        progress.progress = 100.0
        progress.status = "completed"
        progress.message = "上传完成"
        progress.updated_at = datetime.now()
        
        # 添加文件ID到结果
        result["file_id"] = file_id
        
        # 后台任务：清理进度记录
        background_tasks.add_task(cleanup_upload_progress, file_id, delay=300)  # 5分钟后清理
        
        logger.info(f"用户 {current_user.id} 上传了文件: {file.filename}")
        return FileUploadResponse(**result)
        
    except Exception as e:
        # 更新进度为失败
        if 'file_id' in locals():
            progress = upload_progress.get(file_id)
            if progress:
                progress.status = "failed"
                progress.message = f"上传失败: {str(e)}"
                progress.updated_at = datetime.now()
        
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/upload/chunk", response_model=FileChunkUploadResponse)
async def upload_file_chunk(
    chunk_data: FileChunkUploadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    分片上传文件
    
    需要权限: file:upload
    """
    # 检查权限
    if not has_permission(current_user, "file:upload"):
        raise PermissionException("没有上传文件的权限")
    
    try:
        # 获取或创建进度记录
        progress = upload_progress.get(chunk_data.file_id)
        if not progress:
            # 创建新的进度记录
            progress = FileUploadProgress(
                file_id=chunk_data.file_id,
                filename=chunk_data.filename,
                total_size=chunk_data.file_size,
                uploaded_size=0,
                progress=0.0,
                status="uploading",
                message="开始分片上传",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            upload_progress[chunk_data.file_id] = progress
        
        # 验证分片数据
        # 这里可以添加分片验证逻辑
        
        # 更新进度
        chunk_size = len(chunk_data.chunk_data)
        progress.uploaded_size += chunk_size
        progress.progress = (progress.uploaded_size / progress.total_size) * 100 if progress.total_size > 0 else 0
        progress.message = f"上传分片 {chunk_data.chunk_index + 1}/{chunk_data.total_chunks}"
        progress.updated_at = datetime.now()
        
        # 检查是否上传完成
        upload_complete = (chunk_data.chunk_index + 1) >= chunk_data.total_chunks
        
        if upload_complete:
            progress.status = "completed"
            progress.message = "上传完成"
            
            # 这里可以添加合并分片的逻辑
            # 暂时返回一个模拟的文件信息
            file_info = {
                "filename": chunk_data.filename,
                "original_filename": chunk_data.filename,
                "file_path": f"uploads/{chunk_data.filename}",
                "file_size": chunk_data.file_size,
                "file_hash": chunk_data.file_hash,
                "content_type": chunk_data.content_type,
                "storage_type": "local"
            }
            
            return FileChunkUploadResponse(
                chunk_index=chunk_data.chunk_index,
                uploaded=True,
                message="分片上传成功",
                upload_complete=True,
                file_info=FileUploadResponse(**file_info)
            )
        
        return FileChunkUploadResponse(
            chunk_index=chunk_data.chunk_index,
            uploaded=True,
            message="分片上传成功",
            next_chunk_index=chunk_data.chunk_index + 1,
            upload_complete=False
        )
        
    except Exception as e:
        logger.error(f"分片上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分片上传失败: {str(e)}"
        )


@router.get("/upload/progress/{file_id}", response_model=FileUploadProgress)
async def get_upload_progress(
    file_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取文件上传进度
    
    需要权限: file:read
    """
    # 检查权限
    if not has_permission(current_user, "file:read"):
        raise PermissionException("没有查看文件上传进度的权限")
    
    progress = upload_progress.get(file_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="上传进度记录不存在"
        )
    
    return progress


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    from_cloud: Optional[bool] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """
    下载文件
    
    需要权限: file:read
    """
    # 检查权限
    if not has_permission(current_user, "file:read"):
        raise PermissionException("没有下载文件的权限")
    
    try:
        # 获取文件信息
        file_info = file_manager.get_file_info(file_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        # 如果指定了从云存储下载且云存储可用
        if from_cloud and file_manager.cloud_storage._is_available():
            # 生成预签名URL
            presigned_url = file_manager.generate_presigned_url(file_path)
            return {
                "download_url": presigned_url,
                "filename": file_info["filename"],
                "file_size": file_info["file_size"],
                "content_type": file_info.get("content_type", "application/octet-stream")
            }
        
        # 本地文件下载
        local_path = file_path
        if not file_path.startswith(('uploads/', 'backups/', 'exports/')):
            # 如果不是相对路径，尝试从云存储下载
            if file_manager.cloud_storage._is_available():
                local_path = file_manager.download_file_from_cloud(file_path)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="文件不存在且云存储不可用"
                )
        
        # 检查本地文件是否存在
        from pathlib import Path
        path = Path(local_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        # 返回文件流
        def iterfile():
            with open(path, mode="rb") as file_like:
                yield from file_like
        
        content_type = file_info.get("content_type", "application/octet-stream")
        
        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_info['filename']}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件下载失败: {str(e)}"
        )


@router.delete("/delete", response_model=FileOperationResponse)
async def delete_file(
    request: FileDeleteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    删除文件
    
    需要权限: file:delete
    """
    # 检查权限
    if not has_permission(current_user, "file:delete"):
        raise PermissionException("没有删除文件的权限")
    
    try:
        success = file_manager.delete_file(
            file_path=request.file_path,
            delete_from_cloud=request.delete_from_cloud
        )
        
        if success:
            logger.info(f"用户 {current_user.id} 删除了文件: {request.file_path}")
            return FileOperationResponse(
                success=True,
                message="文件删除成功",
                data={"file_path": request.file_path}
            )
        else:
            return FileOperationResponse(
                success=False,
                message="文件删除失败",
                data={"file_path": request.file_path}
            )
            
    except Exception as e:
        logger.error(f"文件删除失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )


@router.get("/list", response_model=FileListResponse)
async def list_files(
    prefix: str = Query(default=""),
    storage_type: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=1000),
    current_user: User = Depends(get_current_user)
):
    """
    列出文件
    
    需要权限: file:read
    """
    # 检查权限
    if not has_permission(current_user, "file:read"):
        raise PermissionException("没有查看文件列表的权限")
    
    try:
        files = file_manager.list_files(
            prefix=prefix,
            storage_type=storage_type
        )
        
        # 限制返回数量
        if limit and len(files) > limit:
            files = files[:limit]
        
        # 转换为FileInfo对象
        file_infos = []
        for file_data in files:
            file_infos.append(FileInfo(**file_data))
        
        return FileListResponse(
            files=file_infos,
            total=len(file_infos),
            prefix=prefix
        )
        
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件列表失败: {str(e)}"
        )


@router.get("/info/{file_path:path}", response_model=FileInfo)
async def get_file_info(
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取文件信息
    
    需要权限: file:read
    """
    # 检查权限
    if not has_permission(current_user, "file:read"):
        raise PermissionException("没有查看文件信息的权限")
    
    try:
        file_info = file_manager.get_file_info(file_path)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        return FileInfo(**file_info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件信息失败: {str(e)}"
        )


@router.post("/sync", response_model=FileOperationResponse)
async def sync_file_to_cloud(
    request: FileSyncRequest,
    current_user: User = Depends(get_current_user)
):
    """
    同步文件到云存储
    
    需要权限: file:write
    """
    # 检查权限
    if not has_permission(current_user, "file:write"):
        raise PermissionException("没有同步文件的权限")
    
    try:
        result = file_manager.sync_file_to_cloud(
            local_file_path=request.local_file_path,
            cloud_file_path=request.cloud_file_path,
            force_upload=request.force_upload
        )
        
        logger.info(f"用户 {current_user.id} 同步了文件: {request.local_file_path}")
        return FileOperationResponse(
            success=True,
            message="文件同步成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"文件同步失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件同步失败: {str(e)}"
        )


@router.post("/backup", response_model=FileOperationResponse)
async def backup_file_to_cloud(
    request: FileBackupRequest,
    current_user: User = Depends(get_current_user)
):
    """
    备份文件到云存储
    
    需要权限: file:write
    """
    # 检查权限
    if not has_permission(current_user, "file:write"):
        raise PermissionException("没有备份文件的权限")
    
    try:
        result = file_manager.backup_file_to_cloud(
            local_file_path=request.local_file_path,
            backup_prefix=request.backup_prefix
        )
        
        logger.info(f"用户 {current_user.id} 备份了文件: {request.local_file_path}")
        return FileOperationResponse(
            success=True,
            message="文件备份成功",
            data=result
        )
        
    except Exception as e:
        logger.error(f"文件备份失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件备份失败: {str(e)}"
        )


@router.post("/presigned-url", response_model=Dict[str, str])
async def generate_presigned_url(
    request: FilePresignedUrlRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成预签名URL
    
    需要权限: file:read
    """
    # 检查权限
    if not has_permission(current_user, "file:read"):
        raise PermissionException("没有生成预签名URL的权限")
    
    try:
        presigned_url = file_manager.generate_presigned_url(
            file_path=request.file_path,
            expires_in=request.expires_in,
            method=request.method
        )
        
        return {
            "presigned_url": presigned_url,
            "file_path": request.file_path,
            "expires_in": str(request.expires_in),
            "method": request.method
        }
        
    except Exception as e:
        logger.error(f"生成预签名URL失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成预签名URL失败: {str(e)}"
        )


@router.post("/storage/switch", response_model=FileOperationResponse)
async def switch_storage_type(
    request: FileStorageSwitchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    切换存储类型
    
    需要权限: system:admin
    """
    # 检查权限
    if not has_permission(current_user, "system:admin"):
        raise PermissionException("没有切换存储类型的权限")
    
    try:
        success = file_manager.switch_storage_type(request.storage_type)
        
        if success:
            logger.info(f"管理员 {current_user.id} 将存储类型切换为: {request.storage_type}")
            return FileOperationResponse(
                success=True,
                message=f"存储类型已切换为: {request.storage_type}",
                data={"storage_type": request.storage_type}
            )
        else:
            return FileOperationResponse(
                success=False,
                message="存储类型切换失败",
                data={"storage_type": request.storage_type}
            )
            
    except Exception as e:
        logger.error(f"切换存储类型失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换存储类型失败: {str(e)}"
        )


@router.get("/storage/status", response_model=FileStorageStatus)
async def get_storage_status(
    current_user: User = Depends(get_current_user)
):
    """
    获取存储状态
    
    需要权限: file:read
    """
    # 检查权限
    if not has_permission(current_user, "file:read"):
        raise PermissionException("没有查看存储状态的权限")
    
    try:
        status_info = file_manager.get_storage_status()
        return FileStorageStatus(**status_info)
        
    except Exception as e:
        logger.error(f"获取存储状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取存储状态失败: {str(e)}"
        )


async def cleanup_upload_progress(file_id: str, delay: int = 300):
    """清理上传进度记录"""
    await asyncio.sleep(delay)
    if file_id in upload_progress:
        del upload_progress[file_id]
        logger.info(f"清理上传进度记录: {file_id}")