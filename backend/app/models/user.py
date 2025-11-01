from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from .base import BaseModel


class UserRole(PyEnum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱地址")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    full_name = Column(String(100), nullable=True, comment="用户全名")
    phone = Column(String(20), nullable=True, comment="手机号码")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, comment="用户角色")
    is_active = Column(Boolean, default=True, nullable=False, comment="账户是否激活")
    is_verified = Column(Boolean, default=False, nullable=False, comment="邮箱是否验证")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    ai_generations = relationship("AIGeneration", back_populates="user", cascade="all, delete-orphan")
    document_versions = relationship("DocumentVersion", back_populates="created_by_user", cascade="all, delete-orphan")
    document_exports = relationship("DocumentExport", back_populates="user", cascade="all, delete-orphan")


class UserSession(BaseModel):
    """用户会话模型"""
    __tablename__ = "user_sessions"
    
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    token_hash = Column(String(255), nullable=False, index=True, comment="令牌哈希值")
    device_info = Column(Text, nullable=True, comment="设备信息")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    expires_at = Column(DateTime, nullable=False, index=True, comment="过期时间")
    
    # 关系
    user = relationship("User", back_populates="user_sessions")