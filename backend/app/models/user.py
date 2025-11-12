from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database import Base

class UserRole(PyEnum):
    """用户角色枚举"""
    USER = "user"  # 普通用户
    ADMIN = "admin"  # 管理员
    MODERATOR = "moderator"  # 版主（可扩展）

class User(Base):
    """用户数据模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, index=True)  # 用户角色
    is_active = Column(Boolean, default=True, index=True)  # 添加索引用于过滤活跃用户
    is_verified = Column(Boolean, default=False, index=True)  # 添加索引用于过滤已验证用户
    created_at = Column(DateTime, default=datetime.utcnow, index=True)  # 添加索引用于时间排序
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    enterprise_infos = relationship("EnterpriseInfo", back_populates="user", cascade="all, delete-orphan")

    @property
    def is_admin(self) -> bool:
        """检查用户是否为管理员"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_moderator(self) -> bool:
        """检查用户是否为版主或管理员"""
        return self.role in [UserRole.MODERATOR, UserRole.ADMIN]
    
    def has_permission(self, required_role: UserRole) -> bool:
        """
        检查用户是否具有所需权限
        
        Args:
            required_role: 所需的最低角色级别
            
        Returns:
            是否具有权限
        """
        role_hierarchy = {
            UserRole.USER: 0,
            UserRole.MODERATOR: 1,
            UserRole.ADMIN: 2
        }
        
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
