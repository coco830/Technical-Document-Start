"""
模板路由
处理模板相关的API请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

from ..database import get_db
from ..models.user import User
from ..utils.auth import get_current_user
from ..prompts.template_loader import TemplateLoader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["模板管理"])

# 初始化服务
template_loader = TemplateLoader()


# Pydantic 模型定义
class TemplateInfo(BaseModel):
    """模板信息"""
    id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    category: str = Field(..., description="模板分类")
    sections: List[str] = Field(default=[], description="模板章节列表")
    usage_count: int = Field(default=0, description="使用次数")
    created_at: str = Field(..., description="创建时间")


@router.get("/", response_model=List[TemplateInfo])
async def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取模板列表
    """
    try:
        # 获取模板列表
        templates = template_loader.list_templates()

        # 转换为前端需要的格式
        template_list = []
        for template in templates:
            template_info = TemplateInfo(
                id=template.get('id', ''),
                name=template.get('name', ''),
                description=template.get('description', ''),
                category=template.get('category', ''),
                sections=template.get('sections', []),
                usage_count=template.get('usage_count', 0),
                created_at=template.get('created_at', '')
            )
            template_list.append(template_info)

        logger.info(f"用户 {current_user.id} 查询模板列表，共 {len(template_list)} 个")
        return template_list

    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模板列表失败"
        )


@router.get("/{template_id}", response_model=TemplateInfo)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个模板详情
    """
    try:
        # 获取模板详情
        template = template_loader.get_template(template_id)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )

        template_info = TemplateInfo(
            id=template.get('id', ''),
            name=template.get('name', ''),
            description=template.get('description', ''),
            category=template.get('category', ''),
            sections=template.get('sections', []),
            usage_count=template.get('usage_count', 0),
            created_at=template.get('created_at', '')
        )

        logger.info(f"用户 {current_user.id} 查询模板详情: {template_id}")
        return template_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模板详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模板详情失败"
        )


@router.post("/{template_id}/use")
async def use_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    使用模板（增加使用计数）
    """
    try:
        # 记录模板使用
        success = template_loader.increment_usage_count(template_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模板不存在"
            )

        logger.info(f"用户 {current_user.id} 使用模板: {template_id}")
        return {"success": True, "message": "模板使用记录已更新"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"记录模板使用失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="记录模板使用失败"
        )