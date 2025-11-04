"""
模板加载器
负责加载和管理 AI 生成模板
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape, SandboxedEnvironment
from jinja2.exceptions import TemplateNotFound, TemplateSyntaxError
import logging

logger = logging.getLogger(__name__)


class TemplateLoader:
    """模板加载器类"""

    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化模板加载器

        Args:
            base_dir: 模板基础目录，默认为 app/prompts
        """
        if base_dir is None:
            # 获取当前文件所在目录
            current_dir = Path(__file__).parent
            self.base_dir = current_dir
        else:
            self.base_dir = Path(base_dir)

        self.templates_dir = self.base_dir / "templates"
        self.registry_path = self.base_dir / "registry.yaml"

        # 加载注册表
        self.registry = self._load_registry()

        # 初始化 Jinja2 环境（使用沙箱模式）
        self.jinja_env = SandboxedEnvironment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # 添加自定义过滤器
        self.jinja_env.filters['tojson'] = self._tojson_filter

        # 缓存已加载的模板
        self._template_cache: Dict[str, Dict] = {}

        logger.info(f"模板加载器初始化完成，基础目录: {self.base_dir}")

    def _load_registry(self) -> Dict:
        """加载模板注册表"""
        try:
            if not self.registry_path.exists():
                logger.warning(f"注册表文件不存在: {self.registry_path}")
                return {"templates": [], "global": {}}

            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f)
                logger.info(f"成功加载注册表，共 {len(registry.get('templates', []))} 个模板")
                return registry
        except Exception as e:
            logger.error(f"加载注册表失败: {e}")
            return {"templates": [], "global": {}}

    def _tojson_filter(self, value, indent=2):
        """JSON 序列化过滤器"""
        return json.dumps(value, ensure_ascii=False, indent=indent)

    def get_template_info(self, template_id: str) -> Optional[Dict]:
        """
        获取模板信息

        Args:
            template_id: 模板 ID

        Returns:
            模板信息字典，如果不存在返回 None
        """
        for template in self.registry.get("templates", []):
            if template["id"] == template_id and template.get("enabled", True):
                return template
        return None

    def list_templates(self) -> List[Dict]:
        """
        列出所有可用模板

        Returns:
            模板信息列表
        """
        return [
            {
                "id": t["id"],
                "name": t["name"],
                "description": t.get("description", ""),
                "category": t.get("category", "general"),
                "version": t.get("version", "1.0.0")
            }
            for t in self.registry.get("templates", [])
            if t.get("enabled", True)
        ]

    def load_template_schema(self, template_id: str) -> Optional[Dict]:
        """
        加载模板结构定义

        Args:
            template_id: 模板 ID

        Returns:
            模板结构字典
        """
        # 检查缓存
        if template_id in self._template_cache:
            return self._template_cache[template_id]

        template_info = self.get_template_info(template_id)
        if not template_info:
            logger.error(f"模板不存在或未启用: {template_id}")
            return None

        schema_path = self.base_dir / template_info["schema_path"]

        try:
            if not schema_path.exists():
                logger.error(f"模板文件不存在: {schema_path}")
                return None

            # 检查文件大小（防止恶意大文件）
            max_size = self.registry.get("global", {}).get("security", {}).get("max_template_size", 102400)
            if schema_path.stat().st_size > max_size:
                logger.error(f"模板文件过大: {schema_path}")
                return None

            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)

            # 缓存模板
            self._template_cache[template_id] = schema
            logger.info(f"成功加载模板: {template_id}")
            return schema

        except json.JSONDecodeError as e:
            logger.error(f"模板 JSON 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"加载模板失败: {e}")
            return None

    def render_prompt(
        self,
        template_id: str,
        section_id: str,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """
        渲染 Prompt 模板

        Args:
            template_id: 模板 ID
            section_id: 章节 ID
            data: 数据字典

        Returns:
            渲染后的 Prompt 文本
        """
        template_info = self.get_template_info(template_id)
        if not template_info:
            logger.error(f"模板不存在: {template_id}")
            return None

        # 验证数据字段（安全检查）
        allowed_vars = self.registry.get("global", {}).get("security", {}).get("allowed_variables", [])
        if allowed_vars:
            for key in data.keys():
                if key not in allowed_vars:
                    logger.warning(f"数据字段 {key} 不在白名单中，将被忽略")
                    continue

        try:
            # 加载 Jinja2 模板
            template_file = template_info["prompt_template_path"].split("/")[-1]
            jinja_template = self.jinja_env.get_template(template_file)

            # 准备渲染数据
            render_data = {
                "section_id": section_id,
                **data
            }

            # 渲染模板
            rendered = jinja_template.render(**render_data)
            logger.info(f"成功渲染 Prompt: 模板={template_id}, 章节={section_id}")
            return rendered.strip()

        except TemplateNotFound as e:
            logger.error(f"Jinja2 模板文件不存在: {e}")
            return None
        except TemplateSyntaxError as e:
            logger.error(f"Jinja2 模板语法错误: {e}")
            return None
        except Exception as e:
            logger.error(f"渲染 Prompt 失败: {e}")
            return None

    def get_ai_config(self, template_id: str) -> Dict:
        """
        获取模板的 AI 配置

        Args:
            template_id: 模板 ID

        Returns:
            AI 配置字典
        """
        template_info = self.get_template_info(template_id)
        if template_info:
            return template_info.get("ai_config", {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            })
        return {}

    def get_cache_config(self, template_id: str) -> Dict:
        """
        获取模板的缓存配置

        Args:
            template_id: 模板 ID

        Returns:
            缓存配置字典
        """
        template_info = self.get_template_info(template_id)
        if template_info:
            return template_info.get("cache", {
                "enabled": True,
                "ttl": 3600
            })
        return {"enabled": False}
