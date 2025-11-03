from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
    MessageResponse
)
from app.utils.auth import get_current_user
import math

router = APIRouter(prefix="/api/projects", tags=["项目管理"])

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（标题/描述）"),
    status: Optional[str] = Query(None, description="项目状态过滤"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的项目列表（分页）

    - **page**: 页码（从1开始）
    - **page_size**: 每页显示数量（1-100）
    - **search**: 可选的搜索关键词（在标题和描述中搜索）
    - **status**: 可选的状态过滤（active/completed/archived）
    """
    # 构建基础查询
    query = db.query(Project).filter(Project.user_id == current_user.id)

    # 状态过滤
    if status:
        allowed_statuses = ['active', 'completed', 'archived']
        if status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的状态值。允许的值：{', '.join(allowed_statuses)}"
            )
        query = query.filter(Project.status == status)

    # 搜索功能
    if search:
        search_filter = or_(
            Project.title.ilike(f"%{search}%"),
            Project.description.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)

    # 获取总数
    total = query.count()

    # 计算总页数
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # 分页查询（按创建时间倒序）
    projects = query.order_by(Project.created_at.desc())\
                    .offset((page - 1) * page_size)\
                    .limit(page_size)\
                    .all()

    return ProjectListResponse(
        projects=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新项目

    - **title**: 项目标题（必填，1-200字符）
    - **description**: 项目描述（可选）
    - **status**: 项目状态（默认：active）
    """
    # 创建项目
    new_project = Project(
        title=project_data.title,
        description=project_data.description,
        status=project_data.status,
        user_id=current_user.id
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"项目创建失败：{str(e)}"
        )

    return ProjectResponse.model_validate(new_project)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个项目详情

    - **project_id**: 项目ID
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权访问"
        )

    return ProjectResponse.model_validate(project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新项目信息

    - **project_id**: 项目ID
    - **title**: 项目标题（可选）
    - **description**: 项目描述（可选）
    - **status**: 项目状态（可选）
    """
    # 查找项目
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权访问"
        )

    # 更新字段
    update_data = project_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供任何更新字段"
        )

    for field, value in update_data.items():
        setattr(project, field, value)

    try:
        db.commit()
        db.refresh(project)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"项目更新失败：{str(e)}"
        )

    return ProjectResponse.model_validate(project)

@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除项目

    - **project_id**: 项目ID
    """
    # 查找项目
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在或无权访问"
        )

    try:
        db.delete(project)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"项目删除失败：{str(e)}"
        )

    return MessageResponse(
        message="项目删除成功",
        detail=f"项目「{project.title}」已被删除"
    )
