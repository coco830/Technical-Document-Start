from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, MessageResponse, UserResponse
from app.utils.auth import get_password_hash, verify_password, create_access_token, get_current_user
from datetime import timedelta
import os

router = APIRouter(prefix="/api/auth", tags=["认证"])

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册接口

    - **email**: 用户邮箱（唯一）
    - **name**: 用户姓名
    - **password**: 密码（最少6位，包含字母和数字）
    - **confirm_password**: 确认密码
    - **accept_terms**: 是否接受服务条款
    """
    # 1. 验证两次密码是否一致
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="两次输入的密码不一致"
        )

    # 2. 检查用户是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

    # 3. 密码哈希
    hashed_password = get_password_hash(user_data.password)

    # 4. 创建用户
    new_user = User(
        email=user_data.email.lower(),
        name=user_data.name,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False
    )

    # 5. 存入数据库
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败：{str(e)}"
        )

    return MessageResponse(
        message="注册成功",
        detail=f"欢迎加入悦恩平台，{new_user.name}！"
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录接口

    - **email**: 用户邮箱
    - **password**: 密码

    返回JWT访问令牌和用户信息
    """
    # 1. 查找用户
    user = db.query(User).filter(User.email == user_data.email.lower()).first()

    # 2. 验证用户是否存在
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 验证密码
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. 检查账户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员"
        )

    # 5. 生成 JWT Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "name": user.name},
        expires_delta=access_token_expires
    )

    # 6. 返回token和用户信息
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    )

@router.get("/verify", response_model=UserResponse)
async def verify_token(current_user: User = Depends(get_current_user)):
    """
    验证Token接口

    返回当前登录用户信息
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )
