from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["认证"])

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

@router.post("/register")
async def register(user: UserRegister):
    """
    用户注册接口
    """
    # TODO: 实现用户注册逻辑
    # 1. 检查用户是否已存在
    # 2. 密码哈希
    # 3. 存入数据库
    return {"message": "注册成功", "email": user.email}

@router.post("/login")
async def login(user: UserLogin):
    """
    用户登录接口
    """
    # TODO: 实现用户登录逻辑
    # 1. 验证用户凭据
    # 2. 生成 JWT Token
    # 3. 返回token

    # 临时返回示例token
    return {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example",
        "user": {
            "email": user.email,
            "name": "用户"
        }
    }
