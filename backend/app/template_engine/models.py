"""
模板引擎数据模型

定义了应急预案章节模板的数据结构，支持多种类型的模板。
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class SectionTemplate(BaseModel):
    """
    章节模板数据结构
    
    用于定义应急预案中各个章节的模板信息，支持固定内容、变量填充、AI生成和混合模式。
    """
    id: str = Field(..., description="章节ID，如 '2.1'")
    chapter_id: str = Field(..., description="所属章节ID，如 '2'")
    title: str = Field(..., description="章节标题")
    type: Literal["fixed", "variable_filled", "ai_written", "hybrid"] = Field(
        ..., 
        description="模板类型：fixed(固定内容)、variable_filled(变量填充)、ai_written(AI生成)、hybrid(混合模式)"
    )
    input_vars: Optional[List[str]] = Field(
        None, 
        description="需要的企业数据字段名列表，用于变量填充"
    )
    template_text: Optional[str] = Field(
        None, 
        description="固定模板文本或带{{变量}}的模板文本"
    )
    ai_prompt_hint: Optional[str] = Field(
        None, 
        description="给大模型的写作指令片段，用于AI生成内容"
    )
    
    class Config:
        """Pydantic配置"""
        json_encoders = {
            # 确保None值在序列化时被正确处理
        }
        schema_extra = {
            "example": {
                "id": "2.1",
                "chapter_id": "2",
                "title": "企业概况",
                "type": "ai_written",
                "input_vars": ["enterprise_name", "establish_date", "main_products"],
                "template_text": None,
                "ai_prompt_hint": "请根据提供的企业信息，编写企业概况部分，包括企业名称、成立时间、主要产品等基本信息。"
            }
        }