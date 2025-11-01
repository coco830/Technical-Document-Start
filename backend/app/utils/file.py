import os
import uuid
import hashlib
import logging
from typing import Optional, BinaryIO, Dict, Any, Union, List
from fastapi import UploadFile, HTTPException, status
from pathlib import Path

from app.core.config import settings


# 设置日志
logger = logging.getLogger(__name__)


class FileManager:
    """文件管理器，支持本地存储和云存储"""
    
    def __init__(self, upload_dir: str = "uploads", allowed_extensions: Optional[List[str]] = None, storage_type: Optional[str] = None):
        self.upload_dir = Path(upload_dir)
        self.allowed_extensions = allowed_extensions or settings.ALLOWED_FILE_TYPES
        self.storage_type = storage_type or settings.STORAGE_TYPE
        
        # 确保上传目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 延迟初始化云存储服务
        self._cloud_storage = None
    
    @property
    def cloud_storage(self):
        """延迟加载云存储服务"""
        if self._cloud_storage is None:
            from app.services.cloud_storage import cloud_storage_service
            self._cloud_storage = cloud_storage_service
        return self._cloud_storage
    
    def validate_file(self, file: UploadFile) -> bool:
        """验证文件"""
        # 检查文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件类型 {file_extension} 不被允许"
            )
        
        # 检查文件大小
        max_size = settings.MAX_FILE_SIZE
        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制（{max_size // (1024*1024)}MB）"
            )
        
        return True
    
    def generate_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        file_extension = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_extension}"
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """计算文件哈希值"""
        return hashlib.md5(file_content).hexdigest()
    
    async def save_file(self, file: UploadFile, prefix: str = "uploads", backup_to_cloud: bool = True) -> Dict[str, Any]:
        """保存上传的文件"""
        # 验证文件
        self.validate_file(file)
        
        # 生成唯一文件名
        filename = self.generate_filename(file.filename)
        
        # 读取文件内容
        file_content = await file.read()
        
        # 计算文件哈希
        file_hash = self.calculate_file_hash(file_content)
        
        # 根据存储类型保存文件
        if self.storage_type == "cos" and self.cloud_storage._is_available():
            # 使用云存储
            try:
                # 重置文件指针
                await file.seek(0)
                
                result = await self.cloud_storage.upload_file(
                    file=file,
                    prefix=prefix,
                    metadata={
                        'original-filename': file.filename,
                        'file-hash': file_hash,
                        'storage-type': 'cos'
                    }
                )
                
                # 如果需要备份到本地
                if backup_to_cloud:
                    local_file_path = self.upload_dir / filename
                    with open(local_file_path, "wb") as f:
                        f.write(file_content)
                    result["local_backup_path"] = str(local_file_path)
                
                logger.info(f"文件已上传到云存储: {file.filename}")
                return result
                
            except Exception as e:
                logger.error(f"云存储上传失败，回退到本地存储: {str(e)}")
                # 回退到本地存储
                return await self._save_file_locally(file, filename, file_content, file_hash, prefix)
        else:
            # 使用本地存储
            return await self._save_file_locally(file, filename, file_content, file_hash, prefix)
    
    async def _save_file_locally(self, file: UploadFile, filename: str, file_content: bytes, file_hash: str, prefix: str) -> Dict[str, Any]:
        """本地保存文件"""
        # 创建子目录
        if prefix:
            subdir = self.upload_dir / prefix
            subdir.mkdir(parents=True, exist_ok=True)
            file_path = subdir / filename
        else:
            file_path = self.upload_dir / filename
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        result = {
            "filename": filename,
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(file_content),
            "file_hash": file_hash,
            "content_type": file.content_type,
            "storage_type": "local"
        }
        
        # 如果云存储可用，异步备份
        if self.cloud_storage._is_available():
            try:
                # 异步备份到云存储
                cloud_path = f"{prefix}/{filename}"
                self.cloud_storage.upload_file_from_path(
                    local_file_path=str(file_path),
                    cloud_file_path=cloud_path,
                    metadata={
                        'original-filename': file.filename,
                        'file-hash': file_hash,
                        'storage-type': 'local_backup'
                    }
                )
                result["cloud_backup_path"] = cloud_path
                logger.info(f"文件已备份到云存储: {file.filename}")
            except Exception as e:
                logger.warning(f"备份到云存储失败: {str(e)}")
        
        return result
    
    def delete_file(self, file_path: str, delete_from_cloud: bool = True) -> bool:
        """删除文件"""
        success = True
        
        # 删除本地文件
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"本地文件已删除: {file_path}")
        except Exception as e:
            logger.error(f"删除本地文件失败: {str(e)}")
            success = False
        
        # 删除云存储文件
        if delete_from_cloud and self.cloud_storage._is_available():
            try:
                # 如果是云存储路径，直接删除
                if file_path.startswith(('uploads/', 'backups/', 'exports/')):
                    self.cloud_storage.delete_file(file_path)
                    logger.info(f"云存储文件已删除: {file_path}")
            except Exception as e:
                logger.error(f"删除云存储文件失败: {str(e)}")
                success = False
        
        return success
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        # 尝试从云存储获取
        if self.cloud_storage._is_available() and file_path.startswith(('uploads/', 'backups/', 'exports/')):
            try:
                cloud_info = self.cloud_storage.get_file_info(file_path)
                if cloud_info:
                    return cloud_info
            except Exception as e:
                logger.warning(f"从云存储获取文件信息失败: {str(e)}")
        
        # 从本地获取
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "filename": path.name,
                "file_path": str(path),
                "file_size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "storage_type": "local"
            }
        except Exception as e:
            logger.error(f"获取本地文件信息失败: {str(e)}")
            return None
    
    def sync_file_to_cloud(self, local_file_path: str, cloud_file_path: Optional[str] = None, force_upload: bool = False) -> Dict[str, Any]:
        """同步本地文件到云存储"""
        if not self.cloud_storage._is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="云存储服务不可用"
            )
        
        if not cloud_file_path:
            # 使用相对路径作为云存储路径
            local_path = Path(local_file_path)
            try:
                # 尝试获取相对于upload_dir的路径
                rel_path = local_path.relative_to(self.upload_dir)
                cloud_file_path = str(rel_path).replace('\\', '/')
            except ValueError:
                # 如果不在upload_dir下，使用文件名
                cloud_file_path = f"uploads/{local_path.name}"
        
        return self.cloud_storage.sync_file_to_cloud(local_file_path, cloud_file_path, force_upload)
    
    def backup_file_to_cloud(self, local_file_path: str, backup_prefix: str = "backups") -> Dict[str, Any]:
        """备份文件到云存储"""
        if not self.cloud_storage._is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="云存储服务不可用"
            )
        
        return self.cloud_storage.backup_file_to_cloud(local_file_path, backup_prefix)
    
    def download_file_from_cloud(self, cloud_file_path: str, local_file_path: Optional[str] = None) -> str:
        """从云存储下载文件"""
        if not self.cloud_storage._is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="云存储服务不可用"
            )
        
        if not local_file_path:
            # 使用upload_dir + 文件名作为本地路径
            filename = Path(cloud_file_path).name
            local_file_path = str(self.upload_dir / filename)
        
        success = self.cloud_storage.download_file(cloud_file_path, local_file_path)
        if success:
            return local_file_path
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="文件下载失败"
            )
    
    def generate_presigned_url(self, file_path: str, expires_in: int = 3600, method: str = "GET") -> str:
        """生成预签名URL"""
        if not self.cloud_storage._is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="云存储服务不可用"
            )
        
        return self.cloud_storage.generate_presigned_url(file_path, expires_in, method)
    
    def list_files(self, prefix: str = "", storage_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出文件"""
        files = []
        
        # 如果指定了云存储或当前存储类型是云存储
        if (storage_type == "cos" or (not storage_type and self.storage_type == "cos")) and self.cloud_storage._is_available():
            try:
                cloud_files = self.cloud_storage.list_files(prefix)
                files.extend(cloud_files)
            except Exception as e:
                logger.error(f"列出云存储文件失败: {str(e)}")
        
        # 如果指定了本地存储或当前存储类型是本地存储
        if storage_type == "local" or (not storage_type and self.storage_type == "local"):
            try:
                local_path = self.upload_dir
                if prefix:
                    local_path = local_path / prefix
                
                if local_path.exists():
                    for file_path in local_path.rglob('*'):
                        if file_path.is_file():
                            stat = file_path.stat()
                            files.append({
                                "filename": file_path.name,
                                "file_path": str(file_path),
                                "file_size": stat.st_size,
                                "last_modified": stat.st_mtime,
                                "storage_type": "local"
                            })
            except Exception as e:
                logger.error(f"列出本地文件失败: {str(e)}")
        
        return files
    
    def switch_storage_type(self, new_storage_type: str) -> bool:
        """切换存储类型"""
        if new_storage_type not in ["local", "cos"]:
            raise ValueError("存储类型必须是 'local' 或 'cos'")
        
        if new_storage_type == "cos" and not self.cloud_storage._is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="云存储服务不可用，无法切换到云存储"
            )
        
        old_type = self.storage_type
        self.storage_type = new_storage_type
        logger.info(f"存储类型已从 {old_type} 切换到 {new_storage_type}")
        return True
    
    def get_storage_status(self) -> Dict[str, Any]:
        """获取存储状态"""
        status = {
            "current_type": self.storage_type,
            "local_available": True,
            "cloud_available": self.cloud_storage._is_available(),
            "upload_dir": str(self.upload_dir)
        }
        
        if self.cloud_storage._is_available():
            cloud_config = {
                "bucket": getattr(self.cloud_storage, 'bucket', None),
                "region": getattr(self.cloud_storage, 'region', None),
                "domain": getattr(self.cloud_storage, 'domain', None)
            }
            # 将云配置信息添加到状态中
            for key, value in cloud_config.items():
                status[f"cloud_{key}"] = value
        
        return status


class FileDownloader:
    """文件下载器"""
    
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def prepare_download(self, file_path: str) -> Dict[str, Any]:
        """准备文件下载"""
        path = Path(file_path)
        
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        stat = path.stat()
        return {
            "file_path": str(path),
            "filename": path.name,
            "file_size": stat.st_size,
            "content_type": self._get_content_type(path.suffix)
        }
    
    def _get_content_type(self, extension: str) -> str:
        """根据文件扩展名获取内容类型"""
        content_types = {
            ".txt": "text/plain",
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif"
        }
        return content_types.get(extension.lower(), "application/octet-stream")


# 全局文件管理器实例
file_manager = FileManager()
file_downloader = FileDownloader()


def get_file_hash(file: BinaryIO) -> str:
    """计算文件哈希值"""
    # 重置文件指针
    file.seek(0)
    content = file.read()
    file.seek(0)
    return hashlib.md5(content).hexdigest()


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    # 移除路径分隔符和其他不安全字符
    unsafe_chars = ['/', '\\', '..', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # 限制文件名长度
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()


def is_image_file(filename: str) -> bool:
    """判断是否为图片文件"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return get_file_extension(filename) in image_extensions


def is_document_file(filename: str) -> bool:
    """判断是否为文档文件"""
    doc_extensions = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
    return get_file_extension(filename) in doc_extensions