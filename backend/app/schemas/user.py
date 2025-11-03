from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional
import re

class UserBase(BaseModel):
    """用户基础模型"""
    email: str
    name: str

class UserRegister(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str
    accept_terms: bool = Field(..., description="是否接受服务条款")

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('邮箱格式不正确')
        return v.lower()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """验证密码强度"""
        if len(v) < 6:
            raise ValueError('密码长度至少6个字符')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('密码必须包含字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v

    @field_validator('accept_terms')
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        """验证是否接受条款"""
        if not v:
            raise ValueError('必须接受服务条款和隐私政策')
        return v

class UserLogin(BaseModel):
    """用户登录请求"""
    email: str
    password: str

class UserResponse(UserBase):
    """用户响应"""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    """消息响应"""
    message: str
    detail: Optional[str] = None
