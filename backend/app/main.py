from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="悦恩人机共写平台 API",
    description="环保文书AI协作创作系统后端接口",
    version="2.1.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Yueen AI CoWrite Platform API",
        "version": "2.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 引入路由模块
from app.routes import auth, projects

app.include_router(auth.router)
app.include_router(projects.router)
