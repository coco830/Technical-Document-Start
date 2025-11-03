from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List

class ProjectBase(BaseModel):
    """项目基础模型"""
    title: str = Field(..., min_length=1, max_length=200, description="项目标题")
    description: Optional[str] = Field(None, description="项目描述")
    status: str = Field(default="active", description="项目状态")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """验证项目状态"""
        allowed_statuses = ['active', 'completed', 'archived']
        if v not in allowed_statuses:
            raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """验证项目标题"""
        if not v or not v.strip():
            raise ValueError('项目标题不能为空')
        return v.strip()

class ProjectCreate(ProjectBase):
    """创建项目请求"""
    pass

class ProjectUpdate(BaseModel):
    """更新项目请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """验证项目状态"""
        if v is not None:
            allowed_statuses = ['active', 'completed', 'archived']
            if v not in allowed_statuses:
                raise ValueError(f'状态必须是以下之一: {", ".join(allowed_statuses)}')
        return v

class ProjectResponse(ProjectBase):
    """项目响应"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    """项目列表响应（分页）"""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    detail: Optional[str] = None
