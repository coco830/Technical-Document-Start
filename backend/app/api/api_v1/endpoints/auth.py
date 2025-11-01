from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, verify_token, get_password_hash
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister, UserLoginResponse, UserPublic, UserCreate
from app.services.user import user
from app.utils.email import send_verification_email, send_password_reset_email
from app.utils.captcha import generate_verification_code
from app.core.exceptions import AuthenticationException, ValidationException

router = APIRouter()


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: Request,
    user_login: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """用户登录"""
    # 验证用户
    authenticated_user = user.authenticate(
        db, email=user_login.username, password=user_login.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active(authenticated_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账户已被禁用"
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=authenticated_user.id, expires_delta=access_token_expires
    )
    
    # 更新最后登录时间
    authenticated_user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 记录登录日志
    # TODO: 实现登录日志记录
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserPublic.from_orm(authenticated_user)
    }


@router.post("/register", response_model=UserLoginResponse)
async def register(
    request: Request,
    user_register: UserRegister,
    db: Session = Depends(get_db)
) -> Any:
    """用户注册"""
    # 检查用户名是否已存在
    if user.get_by_username(db, username=user_register.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user.get_by_email(db, email=user_register.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 创建用户
    # 将UserRegister转换为UserCreate
    user_create = UserCreate(
        username=user_register.username,
        email=user_register.email,
        password=user_register.password,
        full_name=user_register.full_name,
        phone=user_register.phone
    )
    db_user = user.create(db, obj_in=user_create)
    
    # 发送验证邮件
    verification_code = generate_verification_code()
    # TODO: 保存验证码到数据库或Redis
    send_verification_email(user_register.email, verification_code)
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=db_user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": UserPublic.from_orm(db_user)
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """用户登出"""
    # TODO: 实现token黑名单机制
    # 记录登出日志
    return {"message": "登出成功"}


@router.get("/me", response_model=UserPublic)
async def get_current_user(
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取当前用户信息"""
    return UserPublic.from_orm(current_user)


@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """刷新访问令牌"""
    # 从请求头获取刷新令牌
    refresh_token = request.headers.get("X-Refresh-Token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少刷新令牌"
        )
    
    # 验证刷新令牌
    user_id = verify_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )
    
    # 获取用户信息
    db_user = user.get(db, id=user_id)
    if not db_user or not user.is_active(db_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用"
        )
    
    # 创建新的访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=db_user.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/verify-email")
async def verify_email(
    email: str,
    code: str,
    db: Session = Depends(get_db)
) -> Any:
    """验证邮箱"""
    # TODO: 从数据库或Redis获取验证码并验证
    # 更新用户验证状态
    db_user = user.get_by_email(db, email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # TODO: 验证验证码
    # 更新用户验证状态
    db_user.is_verified = True
    db.commit()
    
    return {"message": "邮箱验证成功"}


@router.post("/send-verification-code")
async def send_verification_code(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """发送验证码"""
    db_user = user.get_by_email(db, email=email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 生成验证码
    verification_code = generate_verification_code()
    # TODO: 保存验证码到数据库或Redis
    
    # 发送验证邮件
    send_verification_email(email, verification_code)
    
    return {"message": "验证码已发送"}


@router.post("/reset-password")
async def reset_password(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """重置密码"""
    db_user = user.get_by_email(db, email=email)
    if not db_user:
        # 为了安全，即使用户不存在也返回成功消息
        return {"message": "重置密码链接已发送到您的邮箱"}
    
    # 生成重置令牌
    reset_token = create_access_token(
        subject=db_user.id,
        expires_delta=timedelta(minutes=30)
    )
    
    # 发送重置密码邮件
    reset_url = f"{settings.SERVER_HOST}/reset-password?token={reset_token}"
    send_password_reset_email(email, reset_url)
    
    return {"message": "重置密码链接已发送到您的邮箱"}


@router.post("/confirm-reset-password")
async def confirm_reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
) -> Any:
    """确认重置密码"""
    # 验证重置令牌
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的重置令牌"
        )
    
    # 获取用户信息
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新密码
    user.update(db, db_obj=db_user, obj_in={"password": new_password})
    
    return {"message": "密码重置成功"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """修改密码"""
    # 验证当前密码
    if not user.authenticate(db, email=str(current_user.email), password=current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    user.update(db, db_obj=current_user, obj_in={"password": new_password})
    
    return {"message": "密码修改成功"}