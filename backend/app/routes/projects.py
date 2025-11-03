from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/projects", tags=["项目管理"])

class Project(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

@router.get("/", response_model=List[Project])
async def get_projects():
    """
    获取项目列表
    """
    # TODO: 从数据库获取项目列表
    return []

@router.post("/")
async def create_project(name: str, description: str):
    """
    创建新项目
    """
    # TODO: 实现项目创建逻辑
    return {"message": "项目创建成功", "name": name}
