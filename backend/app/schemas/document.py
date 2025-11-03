from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class DocumentBase(BaseModel):
    """文档基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容（HTML/JSON/Markdown）")
    content_type: str = Field(default="html", description="内容类型")
    project_id: Optional[int] = Field(None, description="所属项目ID")
    is_template: int = Field(default=0, description="是否为模板")
    doc_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        """验证内容类型"""
        allowed_types = ['html', 'json', 'markdown']
        if v not in allowed_types:
            raise ValueError(f'内容类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证文档标题"""
        if not v or not v.strip():
            raise ValueError('文档标题不能为空')
        return v.strip()

    @field_validator('is_template')
    @classmethod
    def validate_is_template(cls, v: int) -> int:
        """验证模板标志"""
        if v not in [0, 1]:
            raise ValueError('is_template 必须是 0 或 1')
        return v

class DocumentCreate(DocumentBase):
    """创建文档请求"""
    pass

class DocumentUpdate(BaseModel):
    """更新文档请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    content_type: Optional[str] = None
    project_id: Optional[int] = None
    is_template: Optional[int] = None
    doc_metadata: Optional[Dict[str, Any]] = None

    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v: Optional[str]) -> Optional[str]:
        """验证内容类型"""
        if v is not None:
            allowed_types = ['html', 'json', 'markdown']
            if v not in allowed_types:
                raise ValueError(f'内容类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @field_validator('is_template')
    @classmethod
    def validate_is_template(cls, v: Optional[int]) -> Optional[int]:
        """验证模板标志"""
        if v is not None and v not in [0, 1]:
            raise ValueError('is_template 必须是 0 或 1')
        return v

class DocumentResponse(DocumentBase):
    """文档响应"""
    id: int
    user_id: int
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """文档列表响应（分页）"""
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class DocumentAutoSave(BaseModel):
    """自动保存请求"""
    content: str = Field(..., description="文档内容")
    version: int = Field(..., description="当前版本号")

class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    detail: Optional[str] = None
