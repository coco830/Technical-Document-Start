"""
文档相关的Pydantic模式定义
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class DocumentFormat(str, Enum):
    """文档格式枚举"""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"


class DocumentStatus(str, Enum):
    """文档状态枚举"""
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    PUBLISHED = "published"


class DocumentBase(BaseModel):
    """文档基础模式"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    format: DocumentFormat = Field(DocumentFormat.MARKDOWN, description="文档格式")
    status: DocumentStatus = Field(DocumentStatus.DRAFT, description="文档状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")


class DocumentCreate(DocumentBase):
    """创建文档模式"""
    project_id: int = Field(..., gt=0, description="所属项目ID")


class DocumentUpdate(BaseModel):
    """更新文档模式"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    format: Optional[DocumentFormat] = Field(None, description="文档格式")
    status: Optional[DocumentStatus] = Field(None, description="文档状态")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")


class Document(DocumentBase):
    """文档完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="文档ID")
    project_id: int = Field(..., description="所属项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class DocumentWithDetails(Document):
    """包含详细信息的文档模式"""
    project_name: Optional[str] = Field(None, description="项目名称")
    versions_count: Optional[int] = Field(0, description="版本数量")
    ai_generations_count: Optional[int] = Field(0, description="AI生成次数")
    exports_count: Optional[int] = Field(0, description="导出次数")


class DocumentVersionBase(BaseModel):
    """文档版本基础模式"""
    version_number: int = Field(..., gt=0, description="版本号")
    content: str = Field(..., description="版本内容")
    changes_summary: Optional[Dict[str, Any]] = Field(None, description="变更摘要")


class DocumentVersionCreate(DocumentVersionBase):
    """创建文档版本模式"""
    document_id: int = Field(..., gt=0, description="文档ID")
    created_by: int = Field(..., gt=0, description="创建者ID")


class DocumentVersion(DocumentVersionBase):
    """文档版本完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="版本ID")
    document_id: int = Field(..., description="文档ID")
    created_by: int = Field(..., description="创建者ID")
    created_at: datetime = Field(..., description="创建时间")


class DocumentVersionWithDetails(DocumentVersion):
    """包含详细信息的文档版本模式"""
    document_title: Optional[str] = Field(None, description="文档标题")
    created_by_name: Optional[str] = Field(None, description="创建者姓名")


class DocumentList(BaseModel):
    """文档列表响应模式"""
    documents: List[DocumentWithDetails] = Field(..., description="文档列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class DocumentVersionList(BaseModel):
    """文档版本列表响应模式"""
    versions: List[DocumentVersionWithDetails] = Field(..., description="版本列表")
    total: int = Field(..., description="总数量")
    document_id: int = Field(..., description="文档ID")