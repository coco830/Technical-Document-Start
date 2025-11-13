"""
Prompt拼接器模块

用于根据章节模板类型和企业数据构建不同类型的AI提示词。
"""

import json
from typing import Dict, List

from .models import SectionTemplate


def _format_enterprise_data(section: SectionTemplate, enterprise_data: dict) -> str:
    """
    将input_vars映射为可读文本
    
    Args:
        section: 章节模板对象
        enterprise_data: 企业数据字典
        
    Returns:
        格式化后的企业数据文本
    """
    if not section.input_vars:
        return "无企业数据需求"
    
    formatted_lines = []
    for var in section.input_vars:
        value = enterprise_data.get(var, "未提供")
        # 将下划线转换为中文友好的字段名
        field_name = var.replace("_", " ")
        formatted_lines.append(f"{field_name}：{value}")
    
    return "\n".join(formatted_lines)


def build_section_prompt(
    section: SectionTemplate,
    enterprise_data: dict,
) -> str:
    """
    根据章节模板类型和企业数据构建AI提示词
    
    Args:
        section: 章节模板对象
        enterprise_data: 企业数据字典
        
    Returns:
        构建好的提示词字符串
    """
    # 固定的系统角色说明
    system_role = "你是一名环保领域的应急预案编制专家，熟悉《突发环境事件应急预案管理办法》和《HJ941-2018》。"
    
    # 根据不同的模板类型处理
    if section.type == "fixed":
        # 固定类型直接返回模板文本
        return section.template_text or ""
    
    elif section.type == "variable_filled":
        # 变量填充类型返回占位字符串
        # 提取input_vars对应的企业数据子集
        subset_data = {}
        if section.input_vars:
            for var in section.input_vars:
                subset_data[var] = enterprise_data.get(var, "未提供")
        
        return "请根据以下结构化数据渲染固定模板或表格：" + json.dumps(subset_data, ensure_ascii=False)
    
    elif section.type in ("ai_written", "hybrid"):
        # AI生成和混合类型需要构建结构化Prompt
        prompt_parts = [system_role]
        
        # 添加任务描述
        if section.title:
            prompt_parts.append(f"\n任务描述：{section.title}")
        
        # 添加写作规则
        if section.ai_prompt_hint:
            prompt_parts.append(f"\n写作规则：{section.ai_prompt_hint}")
        
        # 添加企业数据
        enterprise_info = _format_enterprise_data(section, enterprise_data)
        prompt_parts.append(f"\n企业数据：\n{enterprise_info}")
        
        return "\n".join(prompt_parts)
    
    else:
        # 未知类型，返回空字符串
        return ""