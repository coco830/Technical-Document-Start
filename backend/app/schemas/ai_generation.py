"""
AI生成相关的Pydantic模式定义
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class AIGenerationStatus(str, Enum):
    """AI生成状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AIGenerationBase(BaseModel):
    """AI生成基础模式"""
    prompt: str = Field(..., min_length=1, description="生成提示词")
    generation_config: Optional[Dict[str, Any]] = Field(None, description="生成配置")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class AIGenerationCreate(AIGenerationBase):
    """创建AI生成记录模式"""
    document_id: int = Field(..., gt=0, description="文档ID")
    user_id: int = Field(..., gt=0, description="用户ID")


class AIGenerationUpdate(BaseModel):
    """更新AI生成记录模式"""
    status: Optional[AIGenerationStatus] = Field(None, description="生成状态")
    generated_content: Optional[str] = Field(None, description="生成内容")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class AIGeneration(AIGenerationBase):
    """AI生成记录完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="生成记录ID")
    document_id: int = Field(..., description="文档ID")
    user_id: int = Field(..., description="用户ID")
    generated_content: Optional[str] = Field(None, description="生成内容")
    status: AIGenerationStatus = Field(..., description="生成状态")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class AIGenerationWithDetails(AIGeneration):
    """包含详细信息的AI生成记录模式"""
    document_title: Optional[str] = Field(None, description="文档标题")
    user_name: Optional[str] = Field(None, description="用户姓名")
    processing_time: Optional[int] = Field(None, description="处理时间(秒)")


class AIGenerationRequest(BaseModel):
    """AI生成请求模式"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="生成提示词")
    context: Optional[str] = Field(None, description="上下文内容")
    generation_config: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1
        },
        description="生成配置参数"
    )
    section: Optional[str] = Field(None, description="生成文档的章节")


class AIGenerationResponse(BaseModel):
    """AI生成响应模式"""
    id: int = Field(..., description="生成记录ID")
    status: AIGenerationStatus = Field(..., description="生成状态")
    generated_content: Optional[str] = Field(None, description="生成内容")
    message: Optional[str] = Field(None, description="状态消息")
    processing_time: Optional[int] = Field(None, description="处理时间(秒)")


class AIGenerationList(BaseModel):
    """AI生成记录列表响应模式"""
    generations: List[AIGenerationWithDetails] = Field(..., description="生成记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class AIGenerationConfig(BaseModel):
    """AI生成配置模式"""
    model: str = Field("gpt-3.5-turbo", description="使用的模型")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数，控制随机性")
    max_tokens: int = Field(2000, gt=0, le=4000, description="最大生成令牌数")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="核采样参数")
    frequency_penalty: float = Field(0.1, ge=-2.0, le=2.0, description="频率惩罚")
    presence_penalty: float = Field(0.1, ge=-2.0, le=2.0, description="存在惩罚")
    stop_sequences: Optional[List[str]] = Field(None, description="停止序列")
    system_prompt: Optional[str] = Field(None, description="系统提示词")


class AIGenerationTemplate(BaseModel):
    """AI生成模板模式"""
    id: Optional[int] = Field(None, description="模板ID")
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    prompt_template: str = Field(..., min_length=1, description="提示词模板")
    config: AIGenerationConfig = Field(..., description="默认生成配置")
    category: Optional[str] = Field(None, description="模板分类")
    is_active: bool = Field(True, description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class AIGenerationTemplateCreate(BaseModel):
    """创建AI生成模板模式"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    prompt_template: str = Field(..., min_length=1, description="提示词模板")
    config: AIGenerationConfig = Field(..., description="默认生成配置")
    category: Optional[str] = Field(None, description="模板分类")


class AIGenerationTemplateUpdate(BaseModel):
    """更新AI生成模板模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    prompt_template: Optional[str] = Field(None, min_length=1, description="提示词模板")
    config: Optional[AIGenerationConfig] = Field(None, description="默认生成配置")
    category: Optional[str] = Field(None, description="模板分类")
    is_active: Optional[bool] = Field(None, description="是否启用")


class AIGenerationTemplateList(BaseModel):
    """AI生成模板列表响应模式"""
    templates: List[AIGenerationTemplate] = Field(..., description="模板列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class AIGenerationStatusInfo(BaseModel):
    """AI生成状态信息模式"""
    generation_id: int = Field(..., description="生成记录ID")
    status: AIGenerationStatus = Field(..., description="生成状态")
    task_id: Optional[str] = Field(None, description="任务ID")
    task_status: Optional[str] = Field(None, description="任务状态")
    task_result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")