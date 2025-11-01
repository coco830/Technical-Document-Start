"""
文件相关的Pydantic模式
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class FileUploadRequest(BaseModel):
    """文件上传请求"""
    prefix: Optional[str] = Field(default="uploads", description="文件存储前缀")
    backup_to_cloud: Optional[bool] = Field(default=True, description="是否备份到云存储")
    metadata: Optional[Dict[str, str]] = Field(default=None, description="文件元数据")


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    filename: str = Field(..., description="文件名")
    original_filename: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="文件路径")
    object_key: Optional[str] = Field(default=None, description="云存储对象键")
    file_url: Optional[str] = Field(default=None, description="文件访问URL")
    file_size: int = Field(..., description="文件大小(字节)")
    file_hash: str = Field(..., description="文件哈希值")
    content_type: Optional[str] = Field(default=None, description="文件内容类型")
    storage_type: str = Field(..., description="存储类型")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="文件元数据")
    local_backup_path: Optional[str] = Field(default=None, description="本地备份路径")
    cloud_backup_path: Optional[str] = Field(default=None, description="云备份路径")


class FileDownloadRequest(BaseModel):
    """文件下载请求"""
    file_path: str = Field(..., description="文件路径")
    local_path: Optional[str] = Field(default=None, description="本地保存路径")
    from_cloud: Optional[bool] = Field(default=None, description="是否从云存储下载")


class FileDeleteRequest(BaseModel):
    """文件删除请求"""
    file_path: str = Field(..., description="文件路径")
    delete_from_cloud: Optional[bool] = Field(default=True, description="是否从云存储删除")


class FileListRequest(BaseModel):
    """文件列表请求"""
    prefix: Optional[str] = Field(default="", description="文件前缀")
    storage_type: Optional[str] = Field(default=None, description="存储类型")
    limit: Optional[int] = Field(default=100, description="返回数量限制")


class FileInfo(BaseModel):
    """文件信息"""
    filename: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小(字节)")
    last_modified: Optional[datetime] = Field(default=None, description="最后修改时间")
    storage_type: Optional[str] = Field(default=None, description="存储类型")
    file_url: Optional[str] = Field(default=None, description="文件访问URL")
    etag: Optional[str] = Field(default=None, description="文件ETag")
    content_type: Optional[str] = Field(default=None, description="文件内容类型")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="文件元数据")


class FileListResponse(BaseModel):
    """文件列表响应"""
    files: List[FileInfo] = Field(..., description="文件列表")
    total: int = Field(..., description="文件总数")
    prefix: str = Field(..., description="查询前缀")


class FileSyncRequest(BaseModel):
    """文件同步请求"""
    local_file_path: str = Field(..., description="本地文件路径")
    cloud_file_path: Optional[str] = Field(default=None, description="云存储文件路径")
    force_upload: Optional[bool] = Field(default=False, description="是否强制上传")


class FileBackupRequest(BaseModel):
    """文件备份请求"""
    local_file_path: str = Field(..., description="本地文件路径")
    backup_prefix: Optional[str] = Field(default="backups", description="备份前缀")


class FilePresignedUrlRequest(BaseModel):
    """预签名URL请求"""
    file_path: str = Field(..., description="文件路径")
    expires_in: Optional[int] = Field(default=3600, description="过期时间(秒)")
    method: Optional[str] = Field(default="GET", description="HTTP方法")


class FileStorageSwitchRequest(BaseModel):
    """存储类型切换请求"""
    storage_type: str = Field(..., description="新的存储类型")


class FileStorageStatus(BaseModel):
    """存储状态响应"""
    current_type: str = Field(..., description="当前存储类型")
    local_available: bool = Field(..., description="本地存储是否可用")
    cloud_available: bool = Field(..., description="云存储是否可用")
    upload_dir: str = Field(..., description="上传目录")
    cloud_bucket: Optional[str] = Field(default=None, description="云存储桶名")
    cloud_region: Optional[str] = Field(default=None, description="云存储区域")
    cloud_domain: Optional[str] = Field(default=None, description="云存储域名")


class FileOperationResponse(BaseModel):
    """文件操作响应"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="操作消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="操作数据")


class FileUploadProgress(BaseModel):
    """文件上传进度"""
    file_id: str = Field(..., description="文件ID")
    filename: str = Field(..., description="文件名")
    total_size: int = Field(..., description="总大小")
    uploaded_size: int = Field(..., description="已上传大小")
    progress: float = Field(..., description="上传进度(0-100)")
    status: str = Field(..., description="上传状态")
    message: Optional[str] = Field(default=None, description="状态消息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class FileChunkUploadRequest(BaseModel):
    """文件分片上传请求"""
    file_id: str = Field(..., description="文件ID")
    chunk_index: int = Field(..., description="分片索引")
    total_chunks: int = Field(..., description="总分片数")
    chunk_data: bytes = Field(..., description="分片数据")
    chunk_hash: str = Field(..., description="分片哈希")
    file_hash: str = Field(..., description="完整文件哈希")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    content_type: Optional[str] = Field(default=None, description="文件内容类型")


class FileChunkUploadResponse(BaseModel):
    """文件分片上传响应"""
    chunk_index: int = Field(..., description="分片索引")
    uploaded: bool = Field(..., description="是否上传成功")
    message: str = Field(..., description="上传消息")
    next_chunk_index: Optional[int] = Field(default=None, description="下一个分片索引")
    upload_complete: bool = Field(default=False, description="是否上传完成")
    file_info: Optional[FileUploadResponse] = Field(default=None, description="文件信息")