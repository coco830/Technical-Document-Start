"""
AI 生成路由
处理 AI 模板生成请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
import hashlib
import json
from datetime import datetime, timedelta

from ..database import get_db
from ..models.user import User
from ..utils.auth import get_current_user
from ..prompts.template_loader import TemplateLoader
from ..prompts.template_validator import TemplateValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["AI生成"])

# 初始化模板加载器和验证器
template_loader = TemplateLoader()
validator = TemplateValidator()

# 简单的内存缓存（生产环境建议使用 Redis）
generation_cache: Dict[str, Dict] = {}
rate_limit_cache: Dict[int, List[datetime]] = {}


# Pydantic 模型定义
class GenerationRequest(BaseModel):
    """生成请求"""
    template_id: str = Field(..., description="模板 ID")
    section_id: str = Field(..., description="章节 ID")
    data: Dict[str, Any] = Field(..., description="企业数据")


class GenerationResponse(BaseModel):
    """生成响应"""
    success: bool
    content: Optional[str] = None
    section_title: Optional[str] = None
    cached: bool = False
    error: Optional[str] = None


class TemplateInfo(BaseModel):
    """模板信息"""
    id: str
    name: str
    description: str
    category: str
    version: str


class TemplateSchemaResponse(BaseModel):
    """模板结构响应"""
    success: bool
    schema: Optional[Dict] = None
    error: Optional[str] = None


def _generate_cache_key(template_id: str, section_id: str, data: Dict) -> str:
    """
    生成缓存键

    Args:
        template_id: 模板 ID
        section_id: 章节 ID
        data: 数据

    Returns:
        缓存键
    """
    # 将数据序列化并生成哈希
    data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
    data_hash = hashlib.md5(data_str.encode()).hexdigest()
    return f"{template_id}:{section_id}:{data_hash}"


def _check_rate_limit(user_id: int, max_requests: int = 10, window_minutes: int = 1) -> bool:
    """
    检查限流

    Args:
        user_id: 用户 ID
        max_requests: 时间窗口内最大请求数
        window_minutes: 时间窗口（分钟）

    Returns:
        是否通过
    """
    now = datetime.now()
    cutoff_time = now - timedelta(minutes=window_minutes)

    # 获取用户的请求历史
    if user_id not in rate_limit_cache:
        rate_limit_cache[user_id] = []

    # 清理过期记录
    rate_limit_cache[user_id] = [
        ts for ts in rate_limit_cache[user_id] if ts > cutoff_time
    ]

    # 检查是否超限
    if len(rate_limit_cache[user_id]) >= max_requests:
        return False

    # 记录本次请求
    rate_limit_cache[user_id].append(now)
    return True


def _mock_ai_generation(prompt: str, ai_config: Dict) -> str:
    """
    模拟 AI 生成（实际应用中替换为真实的 AI API 调用）

    Args:
        prompt: Prompt 文本
        ai_config: AI 配置

    Returns:
        生成的文本
    """
    # TODO: 集成真实的 AI API（OpenAI, Claude, 通义千问等）
    # 示例：
    # import openai
    # response = openai.ChatCompletion.create(
    #     model=ai_config.get("model", "gpt-3.5-turbo"),
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=ai_config.get("temperature", 0.7),
    #     max_tokens=ai_config.get("max_tokens", 2000)
    # )
    # return response.choices[0].message.content

    logger.info(f"模拟 AI 生成，Prompt 长度: {len(prompt)}")

    # 返回模拟内容
    return f"""
根据您提供的信息，本章节内容如下：

【这是 AI 生成的模拟内容】

本节详细阐述了相关要求和规范，确保符合国家标准和行业最佳实践。

主要内容包括：
1. 基本原则和指导思想
2. 具体实施方案和流程
3. 责任分工和协调机制
4. 监督检查和持续改进

（注：实际部署时需要接入真实的 AI 模型 API）

Prompt 预览:
{prompt[:200]}...
"""


@router.get("/templates", response_model=List[TemplateInfo])
async def list_templates(
    current_user: User = Depends(get_current_user)
):
    """
    列出所有可用模板

    Returns:
        模板列表
    """
    try:
        templates = template_loader.list_templates()
        logger.info(f"用户 {current_user.id} 查询模板列表，共 {len(templates)} 个")
        return templates
    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模板列表失败"
        )


@router.get("/templates/{template_id}/schema", response_model=TemplateSchemaResponse)
async def get_template_schema(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取模板结构

    Args:
        template_id: 模板 ID

    Returns:
        模板结构
    """
    try:
        schema = template_loader.load_template_schema(template_id)
        if not schema:
            return TemplateSchemaResponse(
                success=False,
                error=f"模板 '{template_id}' 不存在或加载失败"
            )

        logger.info(f"用户 {current_user.id} 获取模板结构: {template_id}")
        return TemplateSchemaResponse(success=True, schema=schema)

    except Exception as e:
        logger.error(f"获取模板结构失败: {e}")
        return TemplateSchemaResponse(
            success=False,
            error=str(e)
        )


@router.post("/generate", response_model=GenerationResponse)
async def generate_content(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    生成 AI 内容

    Args:
        request: 生成请求

    Returns:
        生成结果
    """
    try:
        # 1. 限流检查
        if not _check_rate_limit(current_user.id, max_requests=10, window_minutes=1):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )

        # 2. 验证输入数据
        template_info = template_loader.get_template_info(request.template_id)
        if not template_info:
            return GenerationResponse(
                success=False,
                error=f"模板 '{request.template_id}' 不存在或未启用"
            )

        # 获取必填字段
        required_fields = template_info.get("required_fields", [])
        is_valid, errors = validator.validate_template_data(request.data, required_fields)
        if not is_valid:
            return GenerationResponse(
                success=False,
                error=f"数据验证失败: {'; '.join(errors)}"
            )

        # 3. 验证章节 ID
        template_schema = template_loader.load_template_schema(request.template_id)
        is_valid_section, section_error = validator.validate_section_id(
            request.section_id,
            template_schema
        )
        if not is_valid_section:
            return GenerationResponse(
                success=False,
                error=section_error
            )

        # 获取章节标题
        section_title = None
        for section in template_schema.get("sections", []):
            if section["id"] == request.section_id:
                section_title = section["title"]
                break

        # 4. 检查缓存
        cache_config = template_loader.get_cache_config(request.template_id)
        cache_key = None
        if cache_config.get("enabled", False):
            cache_key = _generate_cache_key(
                request.template_id,
                request.section_id,
                request.data
            )

            if cache_key in generation_cache:
                cached_item = generation_cache[cache_key]
                # 检查缓存是否过期
                ttl = cache_config.get("ttl", 3600)
                if (datetime.now() - cached_item["timestamp"]).seconds < ttl:
                    logger.info(f"从缓存返回结果: {cache_key}")
                    return GenerationResponse(
                        success=True,
                        content=cached_item["content"],
                        section_title=section_title,
                        cached=True
                    )

        # 5. 渲染 Prompt
        prompt = template_loader.render_prompt(
            request.template_id,
            request.section_id,
            {**request.data, "section_title": section_title}
        )

        if not prompt:
            return GenerationResponse(
                success=False,
                error="Prompt 渲染失败"
            )

        # 6. 调用 AI 生成
        ai_config = template_loader.get_ai_config(request.template_id)
        generated_content = _mock_ai_generation(prompt, ai_config)

        # 7. 清理输出
        cleaned_content = validator.sanitize_output(generated_content)

        # 8. 缓存结果
        if cache_key and cache_config.get("enabled", False):
            generation_cache[cache_key] = {
                "content": cleaned_content,
                "timestamp": datetime.now()
            }

        logger.info(
            f"用户 {current_user.id} 成功生成内容: "
            f"模板={request.template_id}, 章节={request.section_id}"
        )

        return GenerationResponse(
            success=True,
            content=cleaned_content,
            section_title=section_title,
            cached=False
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成内容失败: {e}", exc_info=True)
        return GenerationResponse(
            success=False,
            error=f"生成失败: {str(e)}"
        )


@router.delete("/cache")
async def clear_cache(
    current_user: User = Depends(get_current_user)
):
    """
    清除缓存（仅管理员）

    Returns:
        清除结果
    """
    # TODO: 添加管理员权限检查
    generation_cache.clear()
    logger.info(f"用户 {current_user.id} 清除了生成缓存")
    return {"success": True, "message": "缓存已清除"}
