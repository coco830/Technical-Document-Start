"""
模板验证器
负责验证输入数据和模板安全性
"""

import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class TemplateValidator:
    """模板验证器类"""

    # 危险关键字列表（防止模板注入）
    DANGEROUS_KEYWORDS = [
        "__import__",
        "eval",
        "exec",
        "compile",
        "open",
        "file",
        "input",
        "raw_input",
        "__builtins__",
        "__globals__",
        "__code__",
        "globals",
        "locals",
        "vars",
        "dir",
        "getattr",
        "setattr",
        "delattr",
        "hasattr",
    ]

    # 允许的数据类型
    ALLOWED_TYPES = (str, int, float, bool, list, dict, type(None))

    def __init__(self):
        """初始化验证器"""
        self.errors: List[str] = []

    def validate_template_data(
        self,
        data: Dict[str, Any],
        required_fields: List[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        验证模板数据

        Args:
            data: 待验证的数据
            required_fields: 必填字段列表

        Returns:
            (是否通过, 错误列表)
        """
        self.errors = []

        # 检查必填字段
        if required_fields:
            for field in required_fields:
                if field not in data or data[field] is None:
                    self.errors.append(f"必填字段缺失: {field}")

        # 递归验证数据安全性
        self._validate_data_recursive(data, "root")

        return len(self.errors) == 0, self.errors

    def _validate_data_recursive(self, data: Any, path: str):
        """
        递归验证数据

        Args:
            data: 数据
            path: 数据路径（用于错误提示）
        """
        # 检查数据类型
        if not isinstance(data, self.ALLOWED_TYPES):
            self.errors.append(f"不允许的数据类型 {type(data)} at {path}")
            return

        # 字符串检查
        if isinstance(data, str):
            self._validate_string(data, path)

        # 字典检查
        elif isinstance(data, dict):
            for key, value in data.items():
                # 检查键名
                if not isinstance(key, str):
                    self.errors.append(f"字典键必须是字符串 at {path}.{key}")
                    continue

                # 检查键名是否包含危险字符
                if not self._is_safe_key(key):
                    self.errors.append(f"不安全的键名: {key} at {path}")
                    continue

                # 递归检查值
                self._validate_data_recursive(value, f"{path}.{key}")

        # 列表检查
        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._validate_data_recursive(item, f"{path}[{i}]")

    def _validate_string(self, text: str, path: str):
        """
        验证字符串安全性

        Args:
            text: 文本内容
            path: 数据路径
        """
        # 检查长度（防止过长的恶意字符串）
        if len(text) > 50000:  # 50KB
            self.errors.append(f"字符串过长 at {path}")

        # 检查危险关键字
        text_lower = text.lower()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword.lower() in text_lower:
                self.errors.append(f"包含危险关键字 '{keyword}' at {path}")

        # 检查可疑的模板注入模式
        suspicious_patterns = [
            r'\{\{.*__.*\}\}',  # {{__xxx__}}
            r'\{%.*import.*%\}',  # {% import xxx %}
            r'\{\{.*\[.*\].*\}\}',  # {{xxx[yyy]}}
            r'\{%.*exec.*%\}',  # {% exec xxx %}
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                self.errors.append(f"检测到可疑的模板注入模式 at {path}: {pattern}")

    def _is_safe_key(self, key: str) -> bool:
        """
        检查键名是否安全

        Args:
            key: 键名

        Returns:
            是否安全
        """
        # 只允许字母、数字、下划线、中文
        if not re.match(r'^[\w\u4e00-\u9fa5]+$', key):
            return False

        # 不允许双下划线开头
        if key.startswith('__'):
            return False

        return True

    def validate_section_id(self, section_id: str, template_schema: Dict) -> Tuple[bool, str]:
        """
        验证章节 ID 是否存在于模板中

        Args:
            section_id: 章节 ID
            template_schema: 模板结构

        Returns:
            (是否存在, 错误消息)
        """
        if not template_schema:
            return False, "模板结构为空"

        sections = template_schema.get("sections", [])
        for section in sections:
            if section.get("id") == section_id:
                return True, ""

        return False, f"章节 ID '{section_id}' 不存在于模板中"

    def sanitize_output(self, text: str) -> str:
        """
        清理输出文本

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        # 移除潜在的脚本标签
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)

        # 移除潜在的 iframe
        text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)

        # 移除潜在的事件处理器
        text = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)

        return text.strip()

    def validate_rate_limit(
        self,
        user_id: int,
        request_counts: Dict[int, int],
        max_requests: int
    ) -> Tuple[bool, str]:
        """
        简单的限流验证

        Args:
            user_id: 用户 ID
            request_counts: 请求计数字典
            max_requests: 最大请求数

        Returns:
            (是否通过, 错误消息)
        """
        current_count = request_counts.get(user_id, 0)
        if current_count >= max_requests:
            return False, f"请求过于频繁，请稍后再试"

        return True, ""
