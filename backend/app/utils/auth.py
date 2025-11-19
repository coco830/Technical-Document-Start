from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import os

# 从环境变量读取配置
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY环境变量未设置！请确保在.env文件中设置了安全的SECRET_KEY。"
        "生产环境必须使用强随机密钥，长度至少32个字符。"
    )

# 验证密钥长度是否足够安全
if len(SECRET_KEY) < 32:
    raise ValueError(
        f"SECRET_KEY长度不安全！当前长度: {len(SECRET_KEY)}，"
        "建议使用至少32个字符的强随机密钥。"
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # bcrypt有72字节的密码长度限制，需要截断过长的密码
    if len(plain_password.encode('utf-8')) > 72:
        # 对于过长的密码，我们取前72字节进行验证
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    # bcrypt有72字节的密码长度限制，需要截断过长的密码
    if len(password.encode('utf-8')) > 72:
        # 对于过长的密码，我们取前72字节进行哈希
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ JWT解码成功，payload: {payload}")
        return payload
    except JWTError as e:
        print(f"❌ JWT解码失败: {e}")
        print(f"❌ 使用的SECRET_KEY长度: {len(SECRET_KEY)}")
        print(f"❌ Token预览: {token[:50] if len(token) > 50 else token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(lambda: None)  # 需要从调用处传入
):
    """获取当前登录用户（JWT验证中间件）"""
    from app.database import get_db
    from app.models.user import User

    # 获取数据库会话
    if db is None:
        db = next(get_db())

    token = credentials.credentials
    print(f"🔍 验证token: {token[:20]}..." if len(token) > 20 else f"🔍 验证token: {token}")
    
    try:
        payload = decode_access_token(token)
        print(f"✅ Token解码成功: {payload}")
    except Exception as e:
        print(f"❌ Token解码失败: {e}")
        raise

    email: str = payload.get("sub")
    if email is None:
        print("❌ Token中无email信息")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"🔍 查询用户: {email}")
    # 从数据库查询用户
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"❌ 用户不存在: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        print(f"❌ 用户已被禁用: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    print(f"✅ 用户验证成功: {email}, ID: {user.id}")
    return user

def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    return current_user

def get_current_admin_user(
    current_user = Depends(get_current_active_user)
):
    """获取当前管理员用户"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user

def get_current_moderator_user(
    current_user = Depends(get_current_active_user)
):
    """获取当前版主或管理员用户"""
    if not current_user.is_moderator:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要版主或管理员权限"
        )
    return current_user

def require_role(required_role: str):
    """
    角色权限验证装饰器工厂函数
    
    Args:
        required_role: 所需的最低角色级别 ('user', 'moderator', 'admin')
    
    Returns:
        依赖装饰器
    """
    def role_checker(current_user = Depends(get_current_active_user)):
        from app.models.user import UserRole
        
        role_mapping = {
            'user': UserRole.USER,
            'moderator': UserRole.MODERATOR,
            'admin': UserRole.ADMIN
        }
        
        if required_role not in role_mapping:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="无效的角色要求"
            )
        
        if not current_user.has_permission(role_mapping[required_role]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要{required_role}或更高权限"
            )
        
        return current_user
    
    return role_checker

def require_admin(user) -> bool:
    """
    检查用户是否为管理员（向后兼容函数）
    
    Args:
        user: 用户对象
        
    Returns:
        是否为管理员
    """
    return user.is_admin if hasattr(user, 'is_admin') else False
