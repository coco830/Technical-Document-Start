"""
用户相关的Pydantic模式定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, EmailStr, HttpUrl
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    role: UserRole = Field(UserRole.USER, description="用户角色")
    is_active: bool = Field(True, description="账户是否激活")
    is_verified: bool = Field(False, description="邮箱是否验证")


class UserCreate(UserBase):
    """创建用户模式"""
    password: str = Field(..., min_length=8, max_length=128, description="密码")


class UserUpdate(BaseModel):
    """更新用户模式"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    role: Optional[UserRole] = Field(None, description="用户角色")
    is_active: Optional[bool] = Field(None, description="账户是否激活")
    is_verified: Optional[bool] = Field(None, description="邮箱是否验证")


class UserPasswordUpdate(BaseModel):
    """更新用户密码模式"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")


class User(UserBase):
    """用户完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")


class UserWithDetails(User):
    """包含详细信息的用户模式"""
    projects_count: Optional[int] = Field(0, description="项目数量")
    documents_count: Optional[int] = Field(0, description="文档数量")
    ai_generations_count: Optional[int] = Field(0, description="AI生成次数")


class UserPublic(BaseModel):
    """用户公开信息模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    full_name: Optional[str] = Field(None, description="用户全名")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    created_at: datetime = Field(..., description="创建时间")


class UserList(BaseModel):
    """用户列表响应模式"""
    users: List[UserWithDetails] = Field(..., description="用户列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class UserLogin(BaseModel):
    """用户登录模式"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="是否记住登录状态")


class UserRegister(BaseModel):
    """用户注册模式"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="用户全名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")


class UserLoginResponse(BaseModel):
    """用户登录响应模式"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field("bearer", description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间(秒)")
    user: UserPublic = Field(..., description="用户信息")


class UserSessionBase(BaseModel):
    """用户会话基础模式"""
    device_info: Optional[str] = Field(None, description="设备信息")
    ip_address: Optional[str] = Field(None, description="IP地址")


class UserSession(UserSessionBase):
    """用户会话完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="会话ID")
    user_id: int = Field(..., description="用户ID")
    expires_at: datetime = Field(..., description="过期时间")
    created_at: datetime = Field(..., description="创建时间")


class UserSessionWithDetails(UserSession):
    """包含详细信息的用户会话模式"""
    user_name: Optional[str] = Field(None, description="用户名")
    is_active: bool = Field(..., description="是否活跃")
    is_expired: bool = Field(..., description="是否已过期")


class UserSessionList(BaseModel):
    """用户会话列表响应模式"""
    sessions: List[UserSessionWithDetails] = Field(..., description="会话列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class UserStatistics(BaseModel):
    """用户统计模式"""
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    verified_users: int = Field(..., description="已验证用户数")
    new_users_today: int = Field(..., description="今日新增用户数")
    new_users_this_week: int = Field(..., description="本周新增用户数")
    new_users_this_month: int = Field(..., description="本月新增用户数")
    users_by_role: Dict[str, int] = Field(..., description="按角色统计用户数")
    user_registration_trend: List[Dict[str, Any]] = Field(..., description="用户注册趋势")


class UserActivity(BaseModel):
    """用户活动模式"""
    id: int = Field(..., description="活动ID")
    user_id: int = Field(..., description="用户ID")
    action: str = Field(..., description="活动类型")
    resource_type: Optional[str] = Field(None, description="资源类型")
    resource_id: Optional[int] = Field(None, description="资源ID")
    description: Optional[str] = Field(None, description="活动描述")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    created_at: datetime = Field(..., description="创建时间")


class UserActivityList(BaseModel):
    """用户活动列表响应模式"""
    activities: List[UserActivity] = Field(..., description="活动列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class UserPreferences(BaseModel):
    """用户偏好设置模式"""
    theme: str = Field("light", description="主题设置")
    language: str = Field("zh-CN", description="语言设置")
    timezone: str = Field("Asia/Shanghai", description="时区设置")
    email_notifications: bool = Field(True, description="是否接收邮件通知")
    push_notifications: bool = Field(True, description="是否接收推送通知")
    auto_save: bool = Field(True, description="是否自动保存")
    default_document_format: str = Field("markdown", description="默认文档格式")
    default_export_format: str = Field("pdf", description="默认导出格式")


class UserPreferencesUpdate(BaseModel):
    """更新用户偏好设置模式"""
    theme: Optional[str] = Field(None, description="主题设置")
    language: Optional[str] = Field(None, description="语言设置")
    timezone: Optional[str] = Field(None, description="时区设置")
    email_notifications: Optional[bool] = Field(None, description="是否接收邮件通知")
    push_notifications: Optional[bool] = Field(None, description="是否接收推送通知")
    auto_save: Optional[bool] = Field(None, description="是否自动保存")
    default_document_format: Optional[str] = Field(None, description="默认文档格式")
    default_export_format: Optional[str] = Field(None, description="默认导出格式")