"""
模板加载器

负责从YAML文件中加载章节模板配置，并将其转换为SectionTemplate对象。
"""

import os
import yaml
from typing import List, Optional
from pathlib import Path

from .models import SectionTemplate


def load_section_templates(chapter_id: str) -> List[SectionTemplate]:
    """
    从YAML文件加载指定章节的所有模板
    
    Args:
        chapter_id: 章节ID，如 "2"
        
    Returns:
        List[SectionTemplate]: 章节模板列表
        
    Raises:
        FileNotFoundError: 当模板文件不存在时
        yaml.YAMLError: 当YAML文件格式错误时
        ValueError: 当模板数据验证失败时
    """
    # 构建模板文件路径
    template_dir = Path(__file__).parent.parent.parent.parent / "config" / "templates" / "emergency_plan"
    template_file = template_dir / f"{chapter_id}.yaml"
    
    # 检查文件是否存在
    if not template_file.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_file}")
    
    try:
        # 读取并解析YAML文件
        with open(template_file, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f)
        
        if not template_data:
            return []
        
        # 将YAML数据转换为SectionTemplate对象
        templates = []
        for item in template_data:
            # 处理字段名映射（YAML中使用驼峰命名，Python中使用下划线）
            template_dict = {
                "id": item.get("id"),
                "chapter_id": chapter_id,
                "title": item.get("title"),
                "type": item.get("type"),
                "input_vars": item.get("inputVars"),
                "template_text": item.get("templateText"),
                "ai_prompt_hint": item.get("aiPromptHint")
            }
            
            # 创建SectionTemplate实例
            template = SectionTemplate(**template_dict)
            templates.append(template)
        
        return templates
        
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML文件解析错误: {e}")
    except Exception as e:
        raise ValueError(f"模板数据验证失败: {e}")


def get_section_template(chapter_id: str, section_id: str) -> Optional[SectionTemplate]:
    """
    获取指定章节的特定小节模板
    
    Args:
        chapter_id: 章节ID，如 "2"
        section_id: 小节ID，如 "2.1"
        
    Returns:
        Optional[SectionTemplate]: 找到的模板，如果不存在则返回None
    """
    try:
        # 加载章节所有模板
        templates = load_section_templates(chapter_id)
        
        # 查找匹配的小节模板
        for template in templates:
            if template.id == section_id:
                return template
        
        return None
        
    except FileNotFoundError:
        # 如果模板文件不存在，返回None
        return None
    except Exception:
        # 其他错误也返回None，避免影响主流程
        return None


def get_available_chapters() -> List[str]:
    """
    获取所有可用的章节ID列表
    
    Returns:
        List[str]: 可用的章节ID列表
    """
    template_dir = Path(__file__).parent.parent.parent.parent / "config" / "templates" / "emergency_plan"
    
    if not template_dir.exists():
        return []
    
    chapter_ids = []
    for file_path in template_dir.glob("*.yaml"):
        # 获取文件名（不含扩展名）作为章节ID
        chapter_id = file_path.stem
        chapter_ids.append(chapter_id)
    
    return sorted(chapter_ids)