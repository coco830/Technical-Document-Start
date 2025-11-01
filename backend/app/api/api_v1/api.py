from fastapi import APIRouter

from app.api.api_v1.endpoints import users, projects, documents, auth, companies, ai_generation, files

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(companies.router, prefix="/companies", tags=["企业"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目"])
api_router.include_router(documents.router, prefix="/documents", tags=["文档"])
api_router.include_router(ai_generation.router, tags=["AI生成"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])