"""
模板引擎模块

用于加载和管理应急预案模板，支持多种类型的章节模板：
- fixed: 固定内容模板
- variable_filled: 变量填充模板
- ai_written: AI生成内容模板
- hybrid: 混合模板
"""

from .models import SectionTemplate
from .loader import load_section_templates, get_section_template

__all__ = [
    "SectionTemplate",
    "load_section_templates",
    "get_section_template"
]