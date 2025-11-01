from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.permissions import has_permission
from app.core.exceptions import PermissionException, NotFoundException, ValidationException
from app.models.user import User
from app.models.ai_generation import AIGenerationStatus
from app.schemas.ai_generation import (
    AIGeneration, AIGenerationCreate, AIGenerationUpdate, AIGenerationWithDetails, AIGenerationList,
    AIGenerationRequest, AIGenerationResponse, AIGenerationConfig,
    AIGenerationTemplate, AIGenerationTemplateList
)
from app.services.ai_generation import ai_generation_service

router = APIRouter()


# AI生成CRUD API端点
@router.get("/ai-generations", response_model=AIGenerationList)
async def get_ai_generations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    document_id: Optional[int] = Query(None, description="按文档ID筛选"),
    status: Optional[AIGenerationStatus] = Query(None, description="按状态筛选"),
    order_by: Optional[str] = Query("created_at", description="排序字段"),
    order_desc: bool = Query(True, description="是否降序")
) -> Any:
    """获取AI生成记录列表（支持分页、筛选）"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看AI生成记录的权限"
        )
    
    # 获取AI生成记录列表
    generations = ai_generation_service.get_generations(
        db=db,
        user_id=user_id,
        document_id=document_id,
        status=status,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_desc=order_desc,
        current_user=current_user
    )
    
    # 计算总数（这里简化处理，实际应该有单独的计数方法）
    total = len(generations)
    
    return {
        "generations": generations,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }


@router.post("/ai-generations", response_model=AIGeneration)
async def create_ai_generation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    generation_in: AIGenerationCreate
) -> Any:
    """创建新的AI生成记录"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有创建AI生成记录的权限"
        )
    
    # 如果没有指定user_id，使用当前用户ID
    if not generation_in.user_id:
        generation_in.user_id = current_user.id
    
    # 创建AI生成记录
    generation = ai_generation_service.create_generation(
        db=db, generation_in=generation_in, current_user=current_user
    )
    
    return generation


@router.get("/ai-generations/{generation_id}", response_model=AIGenerationWithDetails)
async def get_ai_generation(
    generation_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取单个AI生成记录详情"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看AI生成记录的权限"
        )
    
    # 获取AI生成记录详情
    generation = ai_generation_service.get_generation(
        db=db, generation_id=generation_id, current_user=current_user
    )
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI生成记录不存在"
        )
    
    return generation


@router.put("/ai-generations/{generation_id}", response_model=AIGeneration)
async def update_ai_generation(
    generation_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    generation_in: AIGenerationUpdate
) -> Any:
    """更新AI生成记录"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有修改AI生成记录的权限"
        )
    
    # 更新AI生成记录
    generation = ai_generation_service.update_generation(
        db=db, generation_id=generation_id, generation_in=generation_in, current_user=current_user
    )
    
    return generation


@router.delete("/ai-generations/{generation_id}")
async def delete_ai_generation(
    generation_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """删除AI生成记录"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有删除AI生成记录的权限"
        )
    
    # 删除AI生成记录
    generation = ai_generation_service.delete_generation(
        db=db, generation_id=generation_id, current_user=current_user
    )
    
    return {"message": f"AI生成记录 {generation_id} 已成功删除"}


# AI文案生成API端点
@router.post("/ai-generations/generate", response_model=AIGenerationResponse)
async def generate_content(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: AIGenerationRequest,
    document_id: int = Query(..., description="文档ID")
) -> Any:
    """生成AI内容"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有使用AI生成功能的权限"
        )
    
    # 生成AI内容
    response = await ai_generation_service.generate_content(
        db=db, request=request, document_id=document_id, current_user=current_user
    )
    
    return response


@router.post("/ai-generations/generate/emergency-plan", response_model=AIGenerationResponse)
async def generate_emergency_plan(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    plan_type: str = Query(..., description="预案类型"),
    company_info: Dict[str, Any],
    document_id: int = Query(..., description="文档ID")
) -> Any:
    """生成应急预案"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有使用AI生成功能的权限"
        )
    
    # 生成应急预案
    response = await ai_generation_service.generate_emergency_plan(
        db=db,
        plan_type=plan_type,
        company_info=company_info,
        document_id=document_id,
        current_user=current_user
    )
    
    return response


@router.post("/ai-generations/generate/environmental-assessment", response_model=AIGenerationResponse)
async def generate_environmental_assessment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    project_info: Dict[str, Any],
    document_id: int = Query(..., description="文档ID")
) -> Any:
    """生成环评报告"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有使用AI生成功能的权限"
        )
    
    # 生成环评报告
    response = await ai_generation_service.generate_environmental_assessment(
        db=db,
        project_info=project_info,
        document_id=document_id,
        current_user=current_user
    )
    
    return response


# 异步处理API端点
@router.get("/ai-generations/{generation_id}/status")
async def check_generation_status(
    generation_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """检查生成状态"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看AI生成状态的权限"
        )
    
    # 检查生成状态
    status_info = ai_generation_service.check_generation_status(
        db=db, generation_id=generation_id, current_user=current_user
    )
    
    return status_info


@router.post("/ai-generations/{generation_id}/process")
async def process_generation_async(
    generation_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks
) -> Any:
    """启动异步处理"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有启动AI生成处理的权限"
        )
    
    # 添加后台任务
    background_tasks.add_task(
        ai_generation_service.process_generation_async,
        db=db,
        generation_id=generation_id,
        current_user=current_user
    )
    
    return {"message": f"AI生成任务 {generation_id} 已启动异步处理"}


# 模板管理API端点
@router.get("/ai-generations/templates", response_model=AIGenerationTemplateList)
async def get_all_templates(
    *,
    current_user: User = Depends(get_current_user)
) -> Any:
    """获取所有模板"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看AI生成模板的权限"
        )
    
    # 获取所有模板
    templates = ai_generation_service.get_all_templates()
    
    return {
        "templates": templates,
        "total": len(templates),
        "page": 1,
        "size": len(templates)
    }


@router.get("/ai-generations/templates/{template_type}", response_model=AIGenerationTemplate)
async def get_template_by_type(
    template_type: str,
    *,
    current_user: User = Depends(get_current_user)
) -> Any:
    """根据类型获取模板"""
    # 检查权限
    if not has_permission(current_user, "ai:generate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有查看AI生成模板的权限"
        )
    
    # 获取模板
    try:
        template = ai_generation_service.get_template_by_type(template_type)
        return template
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )