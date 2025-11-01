"""
云存储服务层实现 - 腾讯云COS
"""
import os
import logging
import uuid
import hashlib
import time
from typing import Any, Dict, List, Optional, Union, BinaryIO, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote

from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ValidationException, ServiceException
from app.services.base import BaseService
from app.utils.file import FileManager, get_file_hash, sanitize_filename

# 设置日志
logger = logging.getLogger(__name__)


class CloudStorageService(BaseService):
    """云存储服务类，继承自BaseService"""
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.bucket = settings.TENCENT_COS_BUCKET
        self.region = settings.TENCENT_COS_REGION
        self.domain = settings.TENCENT_COS_DOMAIN
        self.scheme = settings.TENCENT_COS_SCHEME
        self.timeout = settings.TENCENT_COS_TIMEOUT
        self.retry = settings.TENCENT_COS_RETRY
        self.chunk_size = settings.TENCENT_COS_CHUNK_SIZE
        self.max_threads = settings.TENCENT_COS_MAX_THREADS
        self._init_client()
    
    def _init_client(self):
        """初始化腾讯云COS客户端"""
        try:
            if not all([settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY, self.bucket, self.region]):
                logger.warning("腾讯云COS配置不完整，云存储功能将不可用")
                return
            
            config = CosConfig(
                Region=self.region,
                SecretId=settings.TENCENT_SECRET_ID,
                SecretKey=settings.TENCENT_SECRET_KEY,
                Scheme=self.scheme,
                Timeout=self.timeout
            )
            self.client = CosS3Client(config)
            logger.info("腾讯云COS客户端初始化成功")
        except Exception as e:
            logger.error(f"初始化腾讯云COS客户端失败: {str(e)}")
            self.client = None
    
    def _is_available(self) -> bool:
        """检查云存储服务是否可用"""
        return self.client is not None
    
    def _get_object_key(self, file_path: str) -> str:
        """获取对象键"""
        # 移除开头的斜杠
        return file_path.lstrip('/')
    
    def _get_file_url(self, object_key: str) -> str:
        """获取文件访问URL"""
        if self.domain:
            return f"{self.scheme}://{self.domain}/{object_key}"
        else:
            return f"{self.scheme}://{self.bucket}.cos.{self.region}.myqcloud.com/{object_key}"
    
    def _retry_operation(self, operation, *args, **kwargs):
        """重试操作"""
        last_exception = None
        for attempt in range(self.retry):
            try:
                return operation(*args, **kwargs)
            except (CosClientError, CosServiceError) as e:
                last_exception = e
                if attempt < self.retry - 1:
                    logger.warning(f"操作失败，正在重试 ({attempt + 1}/{self.retry}): {str(e)}")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"操作失败，已达到最大重试次数: {str(e)}")
        
        raise ServiceException(f"云存储操作失败: {str(last_exception)}")
    
    def validate_file(self, file: UploadFile) -> bool:
        """验证文件"""
        # 检查文件扩展名
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_FILE_TYPES:
            raise ValidationException(
                f"文件类型 {file_extension} 不被允许"
            )
        
        # 检查文件大小
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise ValidationException(
                f"文件大小超过限制（{settings.MAX_FILE_SIZE // (1024*1024)}MB）"
            )
        
        return True
    
    def generate_file_path(self, original_filename: str, prefix: str = "uploads") -> str:
        """生成文件路径"""
        # 清理文件名
        safe_filename = sanitize_filename(original_filename)
        file_extension = Path(safe_filename).suffix
        unique_id = str(uuid.uuid4())
        
        # 按日期组织文件
        date_path = datetime.now().strftime("%Y/%m/%d")
        filename = f"{unique_id}{file_extension}"
        
        return f"{prefix}/{date_path}/{filename}"
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """计算文件哈希值"""
        return hashlib.md5(file_content).hexdigest()
    
    async def upload_file(
        self, 
        file: UploadFile, 
        prefix: str = "uploads",
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """上传文件到云存储"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        # 验证文件
        self.validate_file(file)
        
        # 生成文件路径
        file_path = self.generate_file_path(file.filename, prefix)
        object_key = self._get_object_key(file_path)
        
        # 读取文件内容
        file_content = await file.read()
        
        # 计算文件哈希
        file_hash = self.calculate_file_hash(file_content)
        
        # 准备元数据
        cos_metadata = {
            'original-filename': file.filename,
            'content-type': file.content_type or 'application/octet-stream',
            'file-size': str(len(file_content)),
            'file-hash': file_hash,
            'upload-time': datetime.now().isoformat()
        }
        
        if metadata:
            cos_metadata.update(metadata)
        
        # 上传文件
        def _upload():
            return self.client.put_object(
                Bucket=self.bucket,
                Body=file_content,
                Key=object_key,
                ContentType=file.content_type or 'application/octet-stream',
                Metadata=cos_metadata
            )
        
        try:
            self._retry_operation(_upload)
            
            # 生成访问URL
            file_url = self._get_file_url(object_key)
            
            logger.info(f"文件上传成功: {file.filename} -> {object_key}")
            
            return {
                "filename": Path(file_path).name,
                "original_filename": file.filename,
                "file_path": file_path,
                "object_key": object_key,
                "file_url": file_url,
                "file_size": len(file_content),
                "file_hash": file_hash,
                "content_type": file.content_type,
                "metadata": cos_metadata
            }
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise ServiceException(f"文件上传失败: {str(e)}")
    
    def upload_file_from_path(
        self, 
        local_file_path: str, 
        cloud_file_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """从本地路径上传文件到云存储"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        local_path = Path(local_file_path)
        if not local_path.exists():
            raise ValidationException(f"本地文件不存在: {local_file_path}")
        
        object_key = self._get_object_key(cloud_file_path)
        
        # 准备元数据
        cos_metadata = {
            'original-filename': local_path.name,
            'file-size': str(local_path.stat().st_size),
            'upload-time': datetime.now().isoformat()
        }
        
        if metadata:
            cos_metadata.update(metadata)
        
        # 上传文件
        def _upload():
            return self.client.upload_file(
                Bucket=self.bucket,
                LocalFilePath=local_file_path,
                Key=object_key,
                Metadata=cos_metadata,
                MAXThread=self.max_threads
            )
        
        try:
            self._retry_operation(_upload)
            
            # 生成访问URL
            file_url = self._get_file_url(object_key)
            
            logger.info(f"文件上传成功: {local_file_path} -> {object_key}")
            
            return {
                "filename": Path(cloud_file_path).name,
                "file_path": cloud_file_path,
                "object_key": object_key,
                "file_url": file_url,
                "file_size": local_path.stat().st_size,
                "metadata": cos_metadata
            }
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise ServiceException(f"文件上传失败: {str(e)}")
    
    def download_file(self, file_path: str, local_file_path: str) -> bool:
        """从云存储下载文件到本地"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        object_key = self._get_object_key(file_path)
        
        # 确保本地目录存在
        local_path = Path(local_file_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        def _download():
            return self.client.get_object(
                Bucket=self.bucket,
                Key=object_key
            )
        
        try:
            response = self._retry_operation(_download)
            
            # 保存文件
            with open(local_file_path, 'wb') as f:
                for chunk in response['Body'].iter_chunks(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"文件下载成功: {object_key} -> {local_file_path}")
            return True
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            raise ServiceException(f"文件下载失败: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """删除云存储中的文件"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        object_key = self._get_object_key(file_path)
        
        def _delete():
            return self.client.delete_object(
                Bucket=self.bucket,
                Key=object_key
            )
        
        try:
            self._retry_operation(_delete)
            logger.info(f"文件删除成功: {object_key}")
            return True
        except Exception as e:
            logger.error(f"文件删除失败: {str(e)}")
            raise ServiceException(f"文件删除失败: {str(e)}")
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """列出云存储中的文件"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        def _list():
            return self.client.list_objects(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
        
        try:
            response = self._retry_operation(_list)
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        "key": obj['Key'],
                        "file_path": obj['Key'],
                        "file_url": self._get_file_url(obj['Key']),
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'],
                        "etag": obj['ETag'].strip('"')
                    })
            
            return files
        except Exception as e:
            logger.error(f"文件列表获取失败: {str(e)}")
            raise ServiceException(f"文件列表获取失败: {str(e)}")
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """获取云存储文件信息"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        object_key = self._get_object_key(file_path)
        
        def _head():
            return self.client.head_object(
                Bucket=self.bucket,
                Key=object_key
            )
        
        try:
            response = self._retry_operation(_head)
            
            return {
                "key": object_key,
                "file_path": file_path,
                "file_url": self._get_file_url(object_key),
                "size": response.get('ContentLength', 0),
                "last_modified": response.get('LastModified'),
                "etag": response.get('ETag', '').strip('"'),
                "content_type": response.get('ContentType'),
                "metadata": response.get('x-cos-meta-', {})
            }
        except CosServiceError as e:
            if e.get_status_code() == 404:
                return None
            raise ServiceException(f"获取文件信息失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            raise ServiceException(f"获取文件信息失败: {str(e)}")
    
    def generate_presigned_url(
        self, 
        file_path: str, 
        expires_in: int = 3600,
        method: str = "GET"
    ) -> str:
        """生成预签名URL"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        object_key = self._get_object_key(file_path)
        expires = int(time.time()) + expires_in
        
        def _generate_url():
            if method.upper() == "GET":
                return self.client.get_presigned_url(
                    Method='GET',
                    Bucket=self.bucket,
                    Key=object_key,
                    Expires=expires
                )
            elif method.upper() == "PUT":
                return self.client.get_presigned_url(
                    Method='PUT',
                    Bucket=self.bucket,
                    Key=object_key,
                    Expires=expires
                )
            else:
                raise ValidationException(f"不支持的HTTP方法: {method}")
        
        try:
            return self._retry_operation(_generate_url)
        except Exception as e:
            logger.error(f"生成预签名URL失败: {str(e)}")
            raise ServiceException(f"生成预签名URL失败: {str(e)}")
    
    def copy_file(self, source_path: str, target_path: str) -> bool:
        """复制文件"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        source_key = self._get_object_key(source_path)
        target_key = self._get_object_key(target_path)
        
        def _copy():
            return self.client.copy_object(
                Bucket=self.bucket,
                Key=target_key,
                CopySource={
                    'Bucket': self.bucket,
                    'Key': source_key
                }
            )
        
        try:
            self._retry_operation(_copy)
            logger.info(f"文件复制成功: {source_key} -> {target_key}")
            return True
        except Exception as e:
            logger.error(f"文件复制失败: {str(e)}")
            raise ServiceException(f"文件复制失败: {str(e)}")
    
    def move_file(self, source_path: str, target_path: str) -> bool:
        """移动文件"""
        # 先复制，再删除原文件
        if self.copy_file(source_path, target_path):
            return self.delete_file(source_path)
        return False
    
    def check_file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        return self.get_file_info(file_path) is not None
    
    def get_file_hash_from_cloud(self, file_path: str) -> Optional[str]:
        """从云存储获取文件哈希值"""
        file_info = self.get_file_info(file_path)
        if file_info and 'metadata' in file_info:
            return file_info['metadata'].get('file-hash')
        return None
    
    def sync_file_to_cloud(
        self, 
        local_file_path: str, 
        cloud_file_path: str,
        force_upload: bool = False
    ) -> Dict[str, Any]:
        """同步文件到云存储"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        local_path = Path(local_file_path)
        if not local_path.exists():
            raise ValidationException(f"本地文件不存在: {local_file_path}")
        
        # 检查云端文件是否存在
        cloud_exists = self.check_file_exists(cloud_file_path)
        
        # 如果云端文件存在且不强制上传，比较哈希值
        if cloud_exists and not force_upload:
            local_hash = get_file_hash(open(local_file_path, 'rb'))
            cloud_hash = self.get_file_hash_from_cloud(cloud_file_path)
            
            if local_hash == cloud_hash:
                logger.info(f"文件已同步，跳过上传: {local_file_path}")
                return {
                    "action": "skipped",
                    "message": "文件已同步，无需上传",
                    "file_path": cloud_file_path
                }
        
        # 上传文件
        result = self.upload_file_from_path(local_file_path, cloud_file_path)
        result["action"] = "uploaded"
        return result
    
    def backup_file_to_cloud(self, local_file_path: str, backup_prefix: str = "backups") -> Dict[str, Any]:
        """备份文件到云存储"""
        local_path = Path(local_file_path)
        if not local_path.exists():
            raise ValidationException(f"本地文件不存在: {local_file_path}")
        
        # 生成备份路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{local_path.stem}_{timestamp}{local_path.suffix}"
        backup_path = f"{backup_prefix}/{backup_filename}"
        
        return self.upload_file_from_path(local_file_path, backup_path)
    
    def cleanup_old_files(self, prefix: str, days: int = 30) -> int:
        """清理旧文件"""
        if not self._is_available():
            raise ServiceException("云存储服务不可用")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        try:
            files = self.list_files(prefix)
            for file_info in files:
                last_modified = file_info.get('last_modified')
                if last_modified and last_modified.replace(tzinfo=None) < cutoff_date:
                    if self.delete_file(file_info['file_path']):
                        deleted_count += 1
            
            logger.info(f"清理完成，删除了 {deleted_count} 个旧文件")
            return deleted_count
        except Exception as e:
            logger.error(f"清理旧文件失败: {str(e)}")
            raise ServiceException(f"清理旧文件失败: {str(e)}")


# 创建全局实例
cloud_storage_service = CloudStorageService()