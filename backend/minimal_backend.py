#!/usr/bin/env python3
"""简化版后端，用于演示登录功能"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import hashlib
import hmac

# 创建FastAPI应用
app = FastAPI(
    title="悦恩人机共写平台 API (演示版)",
    description="简化版后端API，用于演示登录功能",
    version="1.0.0-demo"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟用户数据库
users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "管理员",
        "password": hash_password("admin123"),  # 密码：admin123
        "is_active": True
    },
    "test": {
        "id": 2,
        "username": "test",
        "email": "test@example.com",
        "full_name": "测试用户",
        "password": hash_password("test123"),  # 密码：test123
        "is_active": True
    }
}

# 用于演示的JWT密钥（生产环境请使用强密钥）
SECRET_KEY = "demo-secret-key-do-not-use-in-production"

def hash_password(password: str) -> str:
    """简单的密码哈希（仅用于演示）"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌（简化版）"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = to_encode.copy()
    return encoded_jwt

# 数据模型
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str
    full_name: str

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    is_active: bool

class LoginResponse(BaseModel):
    access_token: dict
    token_type: str = "bearer"
    user: User

# 路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用悦恩人机共写平台 API (演示版)",
        "version": "1.0.0-demo",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    """用户登录"""
    # 查找用户
    user = users_db.get(request.username)
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    # 创建访问令牌
    access_token = create_access_token({"sub": user["username"]})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_active": user["is_active"]
        }
    }

@app.post("/api/v1/auth/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """用户注册（简化版）"""
    # 检查用户名是否已存在
    if request.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="用户名已存在"
        )

    # 创建新用户
    new_user_id = len(users_db) + 1
    users_db[request.username] = {
        "id": new_user_id,
        "username": request.username,
        "email": request.email,
        "full_name": request.full_name,
        "password": hash_password(request.password),
        "is_active": True
    }

    # 创建访问令牌
    access_token = create_access_token({"sub": request.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user_id,
            "username": request.username,
            "email": request.email,
            "full_name": request.full_name,
            "is_active": True
        }
    }

@app.get("/api/v1/users/me")
async def get_current_user():
    """获取当前用户信息（简化版）"""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "管理员",
        "is_active": True
    }

@app.post("/api/v1/auth/logout")
async def logout():
    """用户登出"""
    return {"message": "登出成功"}

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("启动简化版后端服务器...")
    print("演示用户：")
    print("  - 用户名: admin, 密码: admin123")
    print("  - 用户名: test, 密码: test123")
    print("API文档: http://localhost:8000/docs")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
