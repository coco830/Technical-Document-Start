"""
调试路由
用于测试模板引擎和Prompt生成
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from ..template_engine.loader import get_section_template
from ..template_engine.prompt_builder import build_section_prompt
from ..template_engine.models import SectionTemplate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["调试接口"])


class GenerateSectionRequest(BaseModel):
    """生成章节请求"""
    chapter_id: str = Field(..., description="章节ID")
    section_id: str = Field(..., description="小节ID")
    enterprise_data: Dict[str, Any] = Field(..., description="企业数据")


class SectionResponse(BaseModel):
    """章节响应"""
    chapter_id: str
    section_id: str
    title: str


class GenerateSectionResponse(BaseModel):
    """生成章节响应"""
    section: SectionResponse
    prompt: str


@router.post("/generate_section", response_model=GenerateSectionResponse)
async def generate_section(request: GenerateSectionRequest):
    """
    生成章节Prompt（调试接口）
    
    Args:
        request: 生成请求
        
    Returns:
        生成的章节信息和Prompt
        
    Raises:
        HTTPException: 当找不到对应章节时返回404
    """
    try:
        # 获取章节模板
        section = get_section_template(request.chapter_id, request.section_id)
        
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"找不到章节 {request.chapter_id}.{request.section_id} 的模板"
            )
        
        # 构建Prompt
        prompt = build_section_prompt(section, request.enterprise_data)
        
        # 构建响应
        section_response = SectionResponse(
            chapter_id=section.chapter_id,
            section_id=section.id,
            title=section.title
        )
        
        logger.info(f"生成调试Prompt: 章节={request.chapter_id}.{request.section_id}")
        
        return GenerateSectionResponse(
            section=section_response,
            prompt=prompt
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成章节Prompt失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成章节Prompt失败: {str(e)}"
        )