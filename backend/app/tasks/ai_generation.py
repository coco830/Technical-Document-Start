"""
AI生成相关任务
"""
import logging
import time
import httpx
from typing import Dict, Any

from app.core.tasks import task, task_manager
from app.core.cache import cache_service
from app.core.config import settings

# 设置日志
logger = logging.getLogger(__name__)


@task(queue="ai_generation")
def generate_content_task(generation_id: int, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    异步生成AI内容任务
    
    Args:
        generation_id: 生成记录ID
        prompt: 提示词
        config: 生成配置
        
    Returns:
        生成结果
    """
    try:
        # 更新任务状态为处理中
        logger.info(f"开始处理AI生成任务: {generation_id}")
        
        # 检查缓存中是否有相同提示词的结果
        cache_key = f"ai_generation:{hash(prompt)}:{str(config)}"
        cached_result = cache_service.get(cache_key)
        
        if cached_result:
            logger.info(f"使用缓存结果: {generation_id}")
            return {
                "generation_id": generation_id,
                "status": "completed",
                "content": cached_result,
                "cached": True,
                "processing_time": 0
            }
        
        # 调用智谱AI API
        start_time = time.time()
        generated_content = _call_zhipu_api(prompt, config)
        processing_time = int(time.time() - start_time)
        
        # 缓存结果（缓存30分钟）
        cache_service.set(cache_key, generated_content, ttl=1800)
        
        # 返回结果
        result = {
            "generation_id": generation_id,
            "status": "completed",
            "content": generated_content,
            "cached": False,
            "processing_time": processing_time
        }
        
        logger.info(f"AI生成任务完成: {generation_id}，处理时间: {processing_time}秒")
        return result
        
    except Exception as e:
        logger.error(f"AI生成任务失败: {generation_id}，错误: {str(e)}")
        return {
            "generation_id": generation_id,
            "status": "failed",
            "error": str(e),
            "processing_time": 0
        }


@task(queue="ai_generation")
def generate_emergency_plan_task(generation_id: int, plan_type: str, company_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    异步生成应急预案任务
    
    Args:
        generation_id: 生成记录ID
        plan_type: 预案类型
        company_info: 企业信息
        
    Returns:
        生成结果
    """
    try:
        logger.info(f"开始生成应急预案: {generation_id} - {plan_type}")
        
        # 构建提示词
        prompt = _build_emergency_plan_prompt(plan_type, company_info)
        
        # 获取模板配置
        config = {
            "temperature": 0.3,
            "max_tokens": 4000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        # 调用生成任务
        result = generate_content_task(generation_id, prompt, config)
        result["plan_type"] = plan_type
        
        return result
        
    except Exception as e:
        logger.error(f"生成应急预案任务失败: {generation_id}，错误: {str(e)}")
        return {
            "generation_id": generation_id,
            "status": "failed",
            "error": str(e),
            "plan_type": plan_type
        }


@task(queue="ai_generation")
def generate_environmental_assessment_task(generation_id: int, project_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    异步生成环评报告任务
    
    Args:
        generation_id: 生成记录ID
        project_info: 项目信息
        
    Returns:
        生成结果
    """
    try:
        logger.info(f"开始生成环评报告: {generation_id}")
        
        # 构建提示词
        prompt = _build_environmental_assessment_prompt(project_info)
        
        # 获取模板配置
        config = {
            "temperature": 0.2,
            "max_tokens": 5000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        }
        
        # 调用生成任务
        result = generate_content_task(generation_id, prompt, config)
        result["assessment_type"] = "environmental"
        
        return result
        
    except Exception as e:
        logger.error(f"生成环评报告任务失败: {generation_id}，错误: {str(e)}")
        return {
            "generation_id": generation_id,
            "status": "failed",
            "error": str(e),
            "assessment_type": "environmental"
        }


def _call_zhipu_api(prompt: str, config: Dict[str, Any]) -> str:
    """
    调用智谱AI API
    
    Args:
        prompt: 提示词
        config: 配置参数
        
    Returns:
        生成的内容
    """
    if not settings.ZHIPUAI_API_KEY:
        raise ValueError("智谱AI API密钥未配置")
    
    # 构建请求参数
    messages = [{"role": "user", "content": prompt}]
    
    request_data = {
        "model": "glm-4.6",
        "messages": messages,
        "temperature": config.get("temperature", 0.7),
        "max_tokens": config.get("max_tokens", 2000),
        "top_p": config.get("top_p", 0.9),
        "frequency_penalty": config.get("frequency_penalty", 0.1),
        "presence_penalty": config.get("presence_penalty", 0.1)
    }
    
    headers = {
        "Authorization": f"Bearer {settings.ZHIPUAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 发送请求
    with httpx.Client(timeout=60.0) as client:
        try:
            response = client.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers=headers,
                json=request_data
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 提取生成的内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # 质量控制：检查内容长度和基本质量
                if len(content.strip()) < 50:
                    raise ValueError("生成的内容过短，可能质量不佳")
                
                return content
            else:
                raise ValueError("API响应格式异常")
                
        except httpx.HTTPStatusError as e:
            logger.error(f"智谱AI API请求失败: {e.response.status_code} - {e.response.text}")
            raise ValueError(f"AI服务请求失败: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"智谱AI API请求错误: {str(e)}")
            raise ValueError(f"AI服务请求错误: {str(e)}")
        except Exception as e:
            logger.error(f"调用智谱AI API时发生未知错误: {str(e)}")
            raise ValueError(f"AI服务错误: {str(e)}")


def _build_emergency_plan_prompt(plan_type: str, company_info: Dict[str, Any]) -> str:
    """
    构建应急预案提示词
    
    Args:
        plan_type: 预案类型
        company_info: 企业信息
        
    Returns:
        提示词
    """
    return f"""
请根据以下信息生成一份详细的{plan_type}应急预案：

企业信息：
- 企业名称：{company_info.get("name", "")}
- 企业类型：{company_info.get("type", "")}
- 企业规模：{company_info.get("size", "")}
- 所在地区：{company_info.get("location", "")}

预案要求：
- 预案类型：{plan_type}
- 适用范围：{company_info.get("scope", "")}
- 风险等级：{company_info.get("risk_level", "")}

请生成包含以下内容的完整预案：
1. 总则（目的、依据、适用范围、工作原则）
2. 组织机构与职责
3. 风险评估与预防措施
4. 监测与预警
5. 应急响应程序
6. 后期处置
7. 应急保障
8. 培训与演练
9. 附则与附件

请确保内容专业、详细，符合国家相关法规标准。
    """.strip()


def _build_environmental_assessment_prompt(project_info: Dict[str, Any]) -> str:
    """
    构建环评报告提示词
    
    Args:
        project_info: 项目信息
        
    Returns:
        提示词
    """
    return f"""
请根据以下项目信息生成环境影响评价报告：

项目基本信息：
- 项目名称：{project_info.get("name", "")}
- 建设单位：{project_info.get("company_name", "")}
- 项目地点：{project_info.get("location", "")}
- 项目性质：{project_info.get("type", "")}
- 投资规模：{project_info.get("investment", "")}
- 占地面积：{project_info.get("area", "")}

环境特征：
- 所在区域环境功能：{project_info.get("environment_function", "")}
- 主要环境敏感点：{project_info.get("sensitive_points", "")}
- 周边环境状况：{project_info.get("surrounding_environment", "")}

请生成包含以下内容的完整环评报告：
1. 总则（项目由来、评价依据、评价标准、评价等级）
2. 建设项目概况
3. 工程分析
4. 区域环境现状
5. 环境影响预测与评价
6. 环境保护措施
7. 环境风险评价
8. 环境经济损益分析
9. 环境管理与监测计划
10. 公众参与
11. 结论与建议

请确保内容科学、客观，符合国家环评技术导则要求。
    """.strip()


# 任务管理函数
def submit_generation_task(generation_id: int, prompt: str, config: Dict[str, Any]) -> str:
    """
    提交AI生成任务
    
    Args:
        generation_id: 生成记录ID
        prompt: 提示词
        config: 生成配置
        
    Returns:
        任务ID
    """
    result = task_manager.send_task(
        "app.tasks.ai_generation.generate_content_task",
        args=(generation_id, prompt, config),
        queue="ai_generation"
    )
    return result.id


def submit_emergency_plan_task(generation_id: int, plan_type: str, company_info: Dict[str, Any]) -> str:
    """
    提交应急预案生成任务
    
    Args:
        generation_id: 生成记录ID
        plan_type: 预案类型
        company_info: 企业信息
        
    Returns:
        任务ID
    """
    result = task_manager.send_task(
        "app.tasks.ai_generation.generate_emergency_plan_task",
        args=(generation_id, plan_type, company_info),
        queue="ai_generation"
    )
    return result.id


def submit_environmental_assessment_task(generation_id: int, project_info: Dict[str, Any]) -> str:
    """
    提交环评报告生成任务
    
    Args:
        generation_id: 生成记录ID
        project_info: 项目信息
        
    Returns:
        任务ID
    """
    result = task_manager.send_task(
        "app.tasks.ai_generation.generate_environmental_assessment_task",
        args=(generation_id, project_info),
        queue="ai_generation"
    )
    return result.id