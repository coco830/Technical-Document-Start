from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.permissions import has_permission
from app.core.exceptions import PermissionException, NotFoundException
from app.models.user import User
from app.models.project import ProjectStatus, ProjectType
from app.schemas.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectWithDetails, ProjectList,
    ProjectForm, ProjectFormCreate, ProjectFormUpdate, ProjectFormWithDetails, ProjectFormList,
    ProjectStatistics
)
from app.services.project import project_service

router = APIRouter()


# 项目CRUD API端点
@router.get("/", response_model=ProjectList)
async def get_projects(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    company_id: Optional[int] = Query(None, description="按企业ID筛选"),
    status: Optional[ProjectStatus] = Query(None, description="按状态筛选"),
    project_type: Optional[ProjectType] = Query(None, alias="type", description="按类型筛选"),
    order_by: Optional[str] = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序")
) -> Any:
    """获取项目列表（支持分页、筛选、排序）"""
    # 检查权限
    if not has_permission(current_user, "project:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看项目的权限"
        )
    
    # 获取项目列表
    projects = project_service.get_projects(
        db=db,
        user_id=user_id,
        company_id=company_id,
        status=status,
        project_type=project_type,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_desc=order_desc,
        current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(projects)
    
    return {
        "projects": projects,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.post("/", response_model=Project)
async def create_project(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_in: ProjectCreate
) -> Any:
    """创建新项目"""
    # 检查权限
    if not has_permission(current_user, "project:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建项目的权限"
        )
    
    # 如果没有指定user_id，使用当前用户ID
    if not project_in.user_id:
        project_in.user_id = current_user.id
    
    # 创建项目
    project = project_service.create_project(
        db=db, project_in=project_in, current_user=current_user
    )
    
    return project


@router.get("/{project_id}", response_model=ProjectWithDetails)
async def get_project(
    project_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取单个项目详情"""
    # 检查权限
    if not has_permission(current_user, "project:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看项目的权限"
        )
    
    # 获取项目详情
    project = project_service.get_project(
        db=db, project_id=project_id, current_user=current_user
    )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_in: ProjectUpdate
) -> Any:
    """更新项目信息"""
    # 检查权限
    if not has_permission(current_user, "project:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改项目的权限"
        )
    
    # 更新项目
    project = project_service.update_project(
        db=db, project_id=project_id, project_in=project_in, current_user=current_user
    )
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除项目"""
    # 检查权限
    if not has_permission(current_user, "project:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除项目的权限"
        )
    
    # 删除项目
    project = project_service.delete_project(
        db=db, project_id=project_id, current_user=current_user
    )
    
    return {"message": f"项目 {project_id} 已成功删除"}


# 项目状态管理API端点
@router.put("/{project_id}/status", response_model=Project)
async def update_project_status(
    project_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: ProjectStatus
) -> Any:
    """更新项目状态"""
    # 检查权限
    if not has_permission(current_user, "project:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改项目状态的权限"
        )
    
    # 更新项目状态
    project = project_service.update_project_status(
        db=db, project_id=project_id, status=status, current_user=current_user
    )
    
    return project


@router.get("/statistics", response_model=ProjectStatistics)
async def get_project_statistics(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    user_id: Optional[int] = Query(None, description="按用户ID筛选统计")
) -> Any:
    """获取项目统计信息"""
    # 检查权限
    if not has_permission(current_user, "project:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看项目统计的权限"
        )
    
    # 获取项目统计信息
    statistics = project_service.get_project_statistics(
        db=db, user_id=user_id, current_user=current_user
    )
    
    return statistics


# 项目表单管理API端点
@router.get("/{project_id}/forms", response_model=ProjectFormList)
async def get_project_forms(
    project_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    form_type: Optional[str] = Query(None, description="按表单类型筛选")
) -> Any:
    """获取项目表单列表"""
    # 检查权限
    if not has_permission(current_user, "project:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看项目表单的权限"
        )
    
    # 获取项目表单列表
    forms = project_service.get_project_forms(
        db=db,
        project_id=project_id,
        form_type=form_type,
        skip=skip,
        limit=limit,
        current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(forms)
    
    return {
        "forms": forms,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.post("/{project_id}/forms", response_model=ProjectForm)
async def create_project_form(
    project_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    form_in: ProjectFormCreate
) -> Any:
    """创建项目表单"""
    # 检查权限
    if not has_permission(current_user, "project:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建项目表单的权限"
        )
    
    # 确保表单属于指定项目
    form_in.project_id = project_id
    
    # 创建项目表单
    form = project_service.create_project_form(
        db=db, form_in=form_in, current_user=current_user
    )
    
    return form


@router.put("/{project_id}/forms/{form_id}", response_model=ProjectForm)
async def update_project_form(
    project_id: int,
    form_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    form_in: ProjectFormUpdate
) -> Any:
    """更新项目表单"""
    # 检查权限
    if not has_permission(current_user, "project:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改项目表单的权限"
        )
    
    # 更新项目表单
    form = project_service.update_project_form(
        db=db, form_id=form_id, form_in=form_in, current_user=current_user
    )
    
    return form