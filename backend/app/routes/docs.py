"""
文档生成API路由
基于AI Section Framework的文档生成端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ..database import get_db
from ..utils.auth import get_current_user
from ..models.user import User
from ..services.document_generator import document_generator
from ..prompts.ai_sections_loader import ai_sections_loader
from pydantic import BaseModel

router = APIRouter(
    prefix="/api/docs",
    tags=["文档生成"]
)

class DocumentGenerationRequest(BaseModel):
    """文档生成请求模型"""
    enterprise_data: Dict[str, Any]
    
class SingleDocumentRequest(BaseModel):
    """单个文档生成请求模型"""
    document_type: str  # risk_assessment/emergency_plan/resource_report
    enterprise_data: Dict[str, Any]
    
class SectionGenerationRequest(BaseModel):
    """单个AI段落生成请求模型"""
    section_key: str
    enterprise_data: Dict[str, Any]

@router.post("/generate_all", response_model=Dict[str, Any])
async def generate_all_documents(
    request: DocumentGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成所有三个文档
    
    Args:
        request: 包含企业数据的请求体
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        包含三个文档内容的响应
    """
    try:
        # 调用文档生成器
        result = document_generator.generate_all_documents(
            request.enterprise_data, 
            user_id=str(current_user.id)
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "所有文档生成成功",
                "data": {
                    "risk_report": {
                        "title": "环境风险评估报告",
                        "content": result["risk_report"],
                        "word_count": len(result["risk_report"]) if result["risk_report"] else 0
                    },
                    "emergency_plan": {
                        "title": "突发环境事件应急预案",
                        "content": result["emergency_plan"],
                        "word_count": len(result["emergency_plan"]) if result["emergency_plan"] else 0
                    },
                    "resource_report": {
                        "title": "应急资源调查报告",
                        "content": result["resource_report"],
                        "word_count": len(result["resource_report"]) if result["resource_report"] else 0
                    },
                    "ai_sections_used": result["ai_sections_used"]
                }
            }
        else:
            return {
                "success": False,
                "message": "文档生成失败",
                "errors": result["errors"],
                "data": None
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成文档时发生错误: {str(e)}"
        )

@router.post("/generate_document", response_model=Dict[str, Any])
async def generate_single_document(
    request: SingleDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成单个文档
    
    Args:
        request: 包含文档类型和企业数据的请求体
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        包含单个文档内容的响应
    """
    try:
        # 验证文档类型
        valid_types = ["risk_assessment", "emergency_plan", "resource_report"]
        if request.document_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文档类型: {request.document_type}，支持的类型: {valid_types}"
            )
        
        # 调用文档生成器
        result = document_generator.generate_single_document(
            request.document_type,
            request.enterprise_data,
            user_id=str(current_user.id)
        )
        
        if result["success"]:
            # 根据文档类型确定标题
            title_map = {
                "risk_assessment": "环境风险评估报告",
                "emergency_plan": "突发环境事件应急预案",
                "resource_report": "应急资源调查报告"
            }
            
            return {
                "success": True,
                "message": f"{title_map[request.document_type]}生成成功",
                "data": {
                    "document_type": request.document_type,
                    "title": title_map[request.document_type],
                    "content": result["content"],
                    "word_count": len(result["content"]) if result["content"] else 0,
                    "ai_sections_used": result["ai_sections_used"]
                }
            }
        else:
            return {
                "success": False,
                "message": f"{request.document_type}文档生成失败",
                "errors": result["errors"],
                "data": None
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成文档时发生错误: {str(e)}"
        )

@router.post("/generate_section", response_model=Dict[str, Any])
async def generate_single_section(
    request: SectionGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成单个AI段落
    
    Args:
        request: 包含段落键名和企业数据的请求体
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        包含单个AI段落内容的响应
    """
    try:
        # 调用文档生成器
        result = document_generator.generate_single_section(
            request.section_key,
            request.enterprise_data,
            user_id=str(current_user.id)
        )
        
        if result["success"]:
            # 获取section配置信息
            section_config = ai_sections_loader.get_section_config(request.section_key)
            
            return {
                "success": True,
                "message": f"AI段落 {request.section_key} 生成成功",
                "data": {
                    "section_key": request.section_key,
                    "description": section_config.get("description", "") if section_config else "",
                    "content": result["content"],
                    "word_count": len(result["content"]) if result["content"] else 0
                }
            }
        else:
            return {
                "success": False,
                "message": f"AI段落 {request.section_key} 生成失败",
                "errors": result["errors"],
                "data": None
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成AI段落时发生错误: {str(e)}"
        )

@router.get("/sections", response_model=Dict[str, Any])
async def get_ai_sections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取所有AI段落配置信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        包含所有AI段落配置的响应
    """
    try:
        # 获取所有sections配置
        sections_config = ai_sections_loader.get_sections_config()
        
        # 组织返回数据
        sections_info = {}
        for section_key, section_config in sections_config.items():
            sections_info[section_key] = {
                "enabled": section_config.get("enabled", True),
                "document": section_config.get("document", ""),
                "description": section_config.get("description", ""),
                "version": section_config.get("version", 1),
                "model": section_config.get("model", ""),
                "fields": section_config.get("fields", [])
            }
        
        return {
            "success": True,
            "message": "获取AI段落配置成功",
            "data": {
                "sections": sections_info,
                "total_count": len(sections_info),
                "enabled_count": len([s for s in sections_config.values() if s.get("enabled", True)])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI段落配置时发生错误: {str(e)}"
        )

@router.get("/sections/{section_key}", response_model=Dict[str, Any])
async def get_ai_section(
    section_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定AI段落配置信息
    
    Args:
        section_key: AI段落键名
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        包含指定AI段落配置的响应
    """
    try:
        # 获取section配置
        section_config = ai_sections_loader.get_section_config(section_key)
        
        if section_config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI段落不存在: {section_key}"
            )
        
        return {
            "success": True,
            "message": f"获取AI段落 {section_key} 配置成功",
            "data": {
                "section_key": section_key,
                "enabled": section_config.get("enabled", True),
                "document": section_config.get("document", ""),
                "description": section_config.get("description", ""),
                "version": section_config.get("version", 1),
                "model": section_config.get("model", ""),
                "fields": section_config.get("fields", []),
                "system_prompt": section_config.get("system_prompt", ""),
                "user_template": section_config.get("user_template", "")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI段落配置时发生错误: {str(e)}"
        )