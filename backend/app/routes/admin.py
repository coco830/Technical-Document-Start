"""
管理员路由
处理用户管理和系统管理功能
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
import logging
from datetime import datetime

from ..database import get_db
from ..models.user import User, UserRole
from ..utils.auth import get_current_admin_user, get_password_hash, get_password_hash
from ..utils.pagination import optimize_offset_pagination, PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["管理员"])


# Pydantic 模型定义
class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    name: str = Field(..., min_length=1, max_length=100, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    role: UserRole = Field(default=UserRole.USER, description="用户角色")
    is_active: bool = Field(default=True, description="是否激活")
    is_verified: bool = Field(default=False, description="是否已验证")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")


class PasswordResetRequest(BaseModel):
    """重置密码请求"""
    password: str = Field(..., min_length=6, max_length=100, description="新密码")


class UserStats(BaseModel):
    """用户统计信息"""
    total_users: int
    active_users: int
    verified_users: int
    admin_users: int
    moderator_users: int
    regular_users: int
    new_users_this_month: int


@router.get("/users")
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名或邮箱）"),
    role: Optional[UserRole] = Query(None, description="按角色筛选"),
    is_active: Optional[bool] = Query(None, description="按激活状态筛选"),
    is_verified: Optional[bool] = Query(None, description="按验证状态筛选"),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表（仅管理员）
    
    Args:
        page: 页码
        size: 每页数量
        search: 搜索关键词
        role: 角色筛选
        is_active: 激活状态筛选
        is_verified: 验证状态筛选
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        分页的用户列表
    """
    try:
        # 构建查询
        query = db.query(User)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    User.name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
            )
        
        # 角色过滤
        if role:
            query = query.filter(User.role == role)
        
        # 激活状态过滤
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # 验证状态过滤
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        
        # 按创建时间倒序
        query = query.order_by(User.created_at.desc())
        
        # 分页
        from ..utils.pagination import PaginationParams
        pagination_params = PaginationParams(page=page, page_size=size)
        result = optimize_offset_pagination(query, pagination_params, db)
        
        logger.info(f"管理员 {current_user.id} 查询用户列表，页码: {page}, 每页: {size}")
        
        return result
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户列表失败"
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详情（仅管理员）
    
    Args:
        user_id: 用户ID
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        用户详情
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        logger.info(f"管理员 {current_user.id} 查询用户详情: {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户详情失败"
        )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    创建用户（仅管理员）
    
    Args:
        user_data: 用户数据
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        创建的用户
    """
    try:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 创建新用户
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active,
            is_verified=user_data.is_verified
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"管理员 {current_user.id} 创建用户: {new_user.id} ({new_user.email})")
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"创建用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建用户失败"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    更新用户（仅管理员）
    
    Args:
        user_id: 用户ID
        user_data: 更新数据
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        更新后的用户
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 防止管理员修改自己的角色为非管理员
        if user_id == current_user.id and user_data.role and user_data.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能将自己的角色修改为非管理员"
            )
        
        # 检查邮箱是否已被其他用户使用
        if user_data.email and user_data.email != user.email:
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被其他用户使用"
                )
        
        # 更新字段
        update_data = user_data.dict(exclude_unset=True)
        if 'password' in update_data:
            update_data['hashed_password'] = get_password_hash(update_data.pop('password'))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"管理员 {current_user.id} 更新用户: {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新用户失败"
        )


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    删除用户（仅管理员）
    
    Args:
        user_id: 用户ID
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 防止管理员删除自己
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能删除自己的账户"
            )
        
        db.delete(user)
        db.commit()
        
        logger.info(f"管理员 {current_user.id} 删除用户: {user_id}")
        return {"message": "用户已删除", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除用户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除用户失败"
        )


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    password_data: PasswordResetRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    重置用户密码（仅管理员）
    
    Args:
        user_id: 用户ID
        password_data: 新密码数据
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        重置结果
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新密码
        user.hashed_password = get_password_hash(password_data.password)
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"管理员 {current_user.id} 重置用户密码: {user_id}")
        return {"message": "密码已重置", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"重置用户密码失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置用户密码失败"
        )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息（仅管理员）
    
    Args:
        current_user: 当前管理员用户
        db: 数据库会话
        
    Returns:
        用户统计信息
    """
    try:
        # 总用户数
        total_users = db.query(User).count()
        
        # 活跃用户数
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # 已验证用户数
        verified_users = db.query(User).filter(User.is_verified == True).count()
        
        # 管理员用户数
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
        
        # 版主用户数
        moderator_users = db.query(User).filter(User.role == UserRole.MODERATOR).count()
        
        # 普通用户数
        regular_users = db.query(User).filter(User.role == UserRole.USER).count()
        
        # 本月新用户数
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = db.query(User).filter(User.created_at >= current_month_start).count()
        
        stats = UserStats(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            admin_users=admin_users,
            moderator_users=moderator_users,
            regular_users=regular_users,
            new_users_this_month=new_users_this_month
        )
        
        logger.info(f"管理员 {current_user.id} 查询用户统计信息")
        return stats
        
    except Exception as e:
        logger.error(f"获取用户统计信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户统计信息失败"
        )