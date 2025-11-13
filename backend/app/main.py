from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="悦恩人机共写平台 API",
    description="环保文书AI协作创作系统后端接口",
    version="2.1.0"
)

# 初始化数据库
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from init_db import init_database
init_database()

# 从环境变量读取CORS配置
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # 从环境变量读取
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
from app.routes import auth, projects, documents, comments, ai_generate, performance, error_monitoring, admin, enterprise, debug, templates

app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(ai_generate.router, prefix="/api")
app.include_router(performance.router, prefix="/api")
app.include_router(error_monitoring.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(enterprise.router, prefix="/api")
app.include_router(debug.router, prefix="/api")
app.include_router(templates.router, prefix="/api")

# 导出路由（需要安装 reportlab, python-docx, beautifulsoup4）
try:
    from app.routes import export
    app.include_router(export.router, prefix="/api")
    print("✅ Export module loaded successfully")
except ImportError as e:
    print(f"⚠️  Export module not available: {e}")
    print("   Run: pip install reportlab python-docx beautifulsoup4")

# 配置静态文件服务（用于图片访问）
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
