from typing import Any, Dict, List, Optional
import os
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.permissions import has_permission
from app.core.exceptions import PermissionException, NotFoundException, ValidationException
from app.models.user import User
from app.models.document import DocumentFormat, DocumentStatus
from app.schemas.document import (
    Document, DocumentCreate, DocumentUpdate, DocumentWithDetails, DocumentList,
    DocumentVersion, DocumentVersionCreate, DocumentVersionWithDetails, DocumentVersionList
)
from app.schemas.document_export import (
    DocumentExportRequest, DocumentExportResponse, DocumentExportWithDetails, DocumentExportList
)
from app.schemas.ai_generation import (
    AIGenerationRequest, AIGenerationResponse
)
from app.services.document import document_service
from app.services.ai_generation import ai_generation_service

# 设置日志
logger = logging.getLogger(__name__)

router = APIRouter()


# 文档CRUD API端点
@router.get("/", response_model=DocumentList)
async def get_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    project_id: Optional[int] = Query(None, description="按项目ID筛选"),
    status: Optional[DocumentStatus] = Query(None, description="按状态筛选"),
    format: Optional[DocumentFormat] = Query(None, description="按格式筛选"),
    order_by: Optional[str] = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序")
) -> Any:
    """获取文档列表（支持分页、筛选、排序）"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看文档的权限"
        )
    
    # 获取文档列表
    documents = document_service.get_documents(
        db=db,
        project_id=project_id,
        status=status,
        format=format,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_desc=order_desc,
        current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(documents)
    
    return {
        "documents": documents,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.post("/", response_model=Document)
async def create_document(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_in: DocumentCreate
) -> Any:
    """创建新文档"""
    # 检查权限
    if not has_permission(current_user, "document:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建文档的权限"
        )
    
    # 创建文档
    document = document_service.create_document(
        db=db, document_in=document_in, current_user=current_user
    )
    
    return document


@router.get("/{document_id}", response_model=DocumentWithDetails)
async def get_document(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取单个文档详情"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看文档的权限"
        )
    
    # 获取文档详情
    document = document_service.get_document(
        db=db, document_id=document_id, current_user=current_user
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    return document


@router.put("/{document_id}", response_model=Document)
async def update_document(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    document_in: DocumentUpdate
) -> Any:
    """更新文档"""
    # 检查权限
    if not has_permission(current_user, "document:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改文档的权限"
        )
    
    # 更新文档
    document = document_service.update_document(
        db=db, document_id=document_id, document_in=document_in, current_user=current_user
    )
    
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除文档"""
    # 检查权限
    if not has_permission(current_user, "document:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除文档的权限"
        )
    
    # 删除文档
    document = document_service.delete_document(
        db=db, document_id=document_id, current_user=current_user
    )
    
    return {"message": f"文档 {document_id} 已成功删除"}


# 文档版本管理API端点
@router.get("/{document_id}/versions", response_model=DocumentVersionList)
async def get_document_versions(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """获取文档版本列表"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看文档版本的权限"
        )
    
    # 获取文档版本列表
    versions = document_service.get_document_versions(
        db=db, document_id=document_id, skip=skip, limit=limit, current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(versions)
    
    return {
        "versions": versions,
        "total": total,
        "document_id": document_id
    }


@router.get("/{document_id}/versions/{version_id}", response_model=DocumentVersionWithDetails)
async def get_document_version(
    document_id: int,
    version_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取特定版本的文档"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看文档版本的权限"
        )
    
    # 获取文档版本
    version = document_service.get_document_version(
        db=db, version_id=version_id, current_user=current_user
    )
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档版本不存在"
        )
    
    return version


@router.post("/{document_id}/versions", response_model=DocumentVersion)
async def create_document_version(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    content: str = Query(..., description="版本内容")
) -> Any:
    """创建文档版本"""
    # 检查权限
    if not has_permission(current_user, "document:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建文档版本的权限"
        )
    
    # 创建文档版本
    version = document_service.create_document_version(
        db=db, document_id=document_id, content=content, current_user=current_user
    )
    
    return version


@router.post("/{document_id}/versions/{version_id}/restore", response_model=Document)
async def restore_document_version(
    document_id: int,
    version_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """恢复文档到特定版本"""
    # 检查权限
    if not has_permission(current_user, "document:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有恢复文档版本的权限"
        )
    
    # 恢复文档版本
    document = document_service.restore_document_version(
        db=db, version_id=version_id, current_user=current_user
    )
    
    return document


# 文档状态管理API端点
@router.put("/{document_id}/status", response_model=Document)
async def update_document_status(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: DocumentStatus
) -> Any:
    """更新文档状态"""
    # 检查权限
    if not has_permission(current_user, "document:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改文档状态的权限"
        )
    
    # 更新文档状态
    document = document_service.update_document_status(
        db=db, document_id=document_id, status=status, current_user=current_user
    )
    
    return document


@router.get("/by-status", response_model=DocumentList)
async def get_documents_by_status(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: DocumentStatus = Query(..., description="文档状态"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """按状态获取文档"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看文档的权限"
        )
    
    # 获取文档列表
    documents = document_service.get_documents_by_status(
        db=db, status=status, skip=skip, limit=limit, current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(documents)
    
    return {
        "documents": documents,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


# 文档搜索和筛选API端点
@router.get("/search", response_model=DocumentList)
async def search_documents(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    query: str = Query(..., min_length=1, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """搜索文档"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有搜索文档的权限"
        )
    
    # 搜索文档
    documents = document_service.search_documents(
        db=db, query=query, skip=skip, limit=limit, current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(documents)
    
    return {
        "documents": documents,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.get("/by-project", response_model=DocumentList)
async def get_documents_by_project(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_id: int = Query(..., gt=0, description="项目ID"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """获取项目相关文档"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看项目文档的权限"
        )
    
    # 获取项目文档
    documents = document_service.get_documents_by_project(
        db=db, project_id=project_id, skip=skip, limit=limit, current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(documents)
    
    return {
        "documents": documents,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


# 文档导出API端点
@router.post("/{document_id}/export", response_model=DocumentExportResponse)
async def export_document(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    export_request: DocumentExportRequest,
    background_tasks: BackgroundTasks
) -> Any:
    """导出文档"""
    # 检查权限
    if not has_permission(current_user, "document:export"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有导出文档的权限"
        )
    
    # 导出文档
    response = document_service.export_document(
        db=db, document_id=document_id, export_request=export_request, current_user=current_user
    )
    
    return response


@router.get("/{document_id}/export-history", response_model=DocumentExportList)
async def get_export_history(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数")
) -> Any:
    """获取导出历史"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看导出历史的权限"
        )
    
    # 获取导出历史
    exports = document_service.get_export_history(
        db=db, document_id=document_id, skip=skip, limit=limit, current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(exports)
    
    return {
        "exports": exports,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


# AI辅助写作API端点
@router.post("/{document_id}/ai-generate", response_model=AIGenerationResponse)
async def ai_generate_content(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: AIGenerationRequest
) -> Any:
    """AI生成文档内容"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有使用AI生成功能的权限"
        )
    
    # AI生成内容
    response = await ai_generation_service.generate_content(
        db=db, request=request, document_id=document_id, current_user=current_user
    )
    
    return response


@router.get("/exports/{export_id}/download")
async def download_export_file(
    export_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """下载导出文件"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有下载导出文件的权限"
        )
    
    try:
        # 获取导出记录
        from app.services.document_export import document_export_service
        export = document_export_service.crud_document_export.get(db, id=export_id)
        
        if not export:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="导出记录不存在"
            )
        
        # 检查权限
        if export.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限下载此导出文件"
            )
        
        # 检查导出状态
        if not export.file_url or export.file_url.startswith("error:"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="导出文件不可用"
            )
        
        # 如果是云存储URL，直接返回下载URL
        if export.file_url.startswith(('http://', 'https://')):
            return {
                "download_url": export.file_url,
                "filename": export.file_name,
                "file_size": export.file_size
            }
        
        # 本地文件下载
        file_path = export.file_url
        
        # 如果是相对路径，转换为绝对路径
        if not Path(file_path).is_absolute():
            export_dir = os.environ.get("EXPORT_DIR", "exports")
            file_path = os.path.join(export_dir, os.path.basename(file_path))
        
        # 检查文件是否存在
        if not Path(file_path).exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="导出文件不存在"
            )
        
        # 返回文件流
        def iterfile():
            with open(file_path, mode="rb") as file_like:
                yield from file_like
        
        content_type = "application/octet-stream"
        
        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={export.file_name}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载导出文件失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载导出文件失败: {str(e)}"
        )


@router.delete("/exports/{export_id}")
async def delete_export(
    export_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除导出记录"""
    # 检查权限
    if not has_permission(current_user, "document:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除导出记录的权限"
        )
    
    try:
        # 删除导出记录
        from app.services.document_export import document_export_service
        success = document_export_service.delete_export(
            db=db, export_id=export_id, current_user=current_user
        )
        
        if success:
            return {"message": f"导出记录 {export_id} 已成功删除"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除导出记录失败"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除导出记录失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除导出记录失败: {str(e)}"
        )


@router.get("/exports/templates", response_model=List[Dict[str, Any]])
async def get_export_templates(
    *,
    format: Optional[str] = Query(None, description="导出格式"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取导出模板列表"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看导出模板的权限"
        )
    
    try:
        # 获取导出模板
        from app.services.document_export import document_export_service
        from app.schemas.document_export import ExportFormat
        
        export_format = None
        if format:
            try:
                export_format = ExportFormat(format)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不支持的导出格式: {format}"
                )
        
        templates = document_export_service.get_export_templates(export_format=export_format)
        
        # 转换为字典列表
        result = []
        for template in templates:
            result.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "format": template.format.value,
                "is_default": template.is_default,
                "is_active": template.is_active,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "updated_at": template.updated_at.isoformat() if template.updated_at else None,
                "options": template.options.dict() if template.options else {}
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取导出模板失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出模板失败: {str(e)}"
        )


@router.get("/exports/statistics", response_model=Dict[str, Any])
async def get_export_statistics(
    *,
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取导出统计"""
    # 检查权限
    if not has_permission(current_user, "document:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看导出统计的权限"
        )
    
    try:
        # 获取导出统计
        from app.services.document_export import document_export_service
        statistics = document_export_service.get_export_statistics(
            db=db, days=days, current_user=current_user
        )
        
        # 转换为字典
        result = {
            "total_exports": statistics.total_exports,
            "successful_exports": statistics.successful_exports,
            "failed_exports": statistics.failed_exports,
            "exports_by_format": statistics.exports_by_format,
            "exports_by_user": statistics.exports_by_user,
            "average_file_size": statistics.average_file_size,
            "total_file_size": statistics.total_file_size,
            "most_exported_documents": statistics.most_exported_documents,
            "storage_stats": statistics.storage_stats
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取导出统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导出统计失败: {str(e)}"
        )


@router.post("/{document_id}/ai-enhance", response_model=AIGenerationResponse)
async def ai_enhance_content(
    document_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    enhancement_type: str = Query(..., description="增强类型"),
    target_section: Optional[str] = Query(None, description="目标章节")
) -> Any:
    """AI增强文档内容"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有使用AI增强功能的权限"
        )
    
    # 获取文档信息
    document = document_service.get_document(
        db=db, document_id=document_id, current_user=current_user
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档不存在"
        )
    
    # 构建增强提示词
    if enhancement_type == "expand":
        prompt = f"请扩展以下文档内容，使其更加详细和完整：\n\n{document.content}"
    elif enhancement_type == "refine":
        prompt = f"请优化以下文档内容，改进语言表达和逻辑结构：\n\n{document.content}"
    elif enhancement_type == "summarize":
        prompt = f"请总结以下文档内容，提取关键信息：\n\n{document.content}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的增强类型"
        )
    
    # 创建AI生成请求
    ai_request = AIGenerationRequest(
        prompt=prompt,
        context=f"文档标题：{document.title}\n文档格式：{document.format.value}",
        section=target_section
    )
    
    # AI增强内容
    response = await ai_generation_service.generate_content(
        db=db, request=ai_request, document_id=document_id, current_user=current_user
    )
    
    return response