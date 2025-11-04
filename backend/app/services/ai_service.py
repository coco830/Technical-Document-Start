"""
AI 服务 - 支持多种 AI 模型和重试机制
"""

import os
import time
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI 生成服务"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.default_model = os.getenv("AI_MODEL", "gpt-4")

        # 检查是否配置了 API Key
        if self.api_key:
            logger.info(f"AI 服务已启动，使用模型: {self.default_model}")
        else:
            logger.warning("未配置 OPENAI_API_KEY，将使用模拟生成")

    def _call_openai_with_retry(
        self,
        prompt: str,
        config: Dict,
        max_retries: int = 3
    ) -> str:
        """
        调用 OpenAI API（带重试机制）

        Args:
            prompt: Prompt 文本
            config: AI 配置
            max_retries: 最大重试次数

        Returns:
            生成的文本

        Raises:
            Exception: 所有重试失败后抛出异常
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai 包: pip install openai")

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"调用 OpenAI API (尝试 {attempt + 1}/{max_retries})")

                response = client.chat.completions.create(
                    model=config.get("model", self.default_model),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 2000),
                    timeout=30  # 30 秒超时
                )

                content = response.choices[0].message.content
                logger.info(f"AI 生成成功，返回 {len(content)} 字符")
                return content

            except Exception as e:
                last_error = e
                logger.warning(f"API 调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")

                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避：2, 4, 8 秒
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)

        # 所有重试都失败
        logger.error(f"AI 生成失败，已重试 {max_retries} 次: {last_error}")
        raise Exception(f"AI 生成失败: {last_error}")

    def _mock_generate(self, prompt: str, config: Dict) -> str:
        """
        模拟 AI 生成（用于测试和无 API Key 时）

        Args:
            prompt: Prompt 文本
            config: AI 配置

        Returns:
            模拟生成的文本
        """
        logger.info(f"使用模拟生成，Prompt 长度: {len(prompt)}")

        # 从 prompt 中提取章节信息
        section_title = "章节内容"
        if "生成" in prompt and "章节" in prompt:
            lines = prompt.split('\n')
            for line in lines:
                if '生成' in line and '"' in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        section_title = parts[1]
                        break

        return f"""
# {section_title}

根据您提供的企业信息和模板要求，本章节内容如下：

## 主要内容

本节详细阐述了相关要求和规范，确保符合国家标准和行业最佳实践。

### 1. 基本原则

遵循科学、规范、实用的原则，结合企业实际情况，制定切实可行的方案。

### 2. 具体要求

- 符合相关法律法规要求
- 满足行业标准和规范
- 考虑企业实际运营情况
- 注重可操作性和实用性

### 3. 实施建议

1. 建立健全管理体系
2. 明确各方职责分工
3. 加强培训和演练
4. 定期检查和完善

---

**注意**：这是模拟生成的内容。实际部署时请配置 OPENAI_API_KEY 环境变量以使用真实的 AI 模型。

**配置方法**：
```bash
# .env 文件
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选
AI_MODEL=gpt-4  # 可选
```

**Prompt 预览**（前 300 字符）：
{prompt[:300]}...
"""

    def generate(
        self,
        prompt: str,
        config: Dict,
        use_mock: Optional[bool] = None
    ) -> str:
        """
        生成 AI 内容

        Args:
            prompt: Prompt 文本
            config: AI 配置
            use_mock: 是否使用模拟生成（None 表示自动判断）

        Returns:
            生成的文本
        """
        # 自动判断是否使用模拟
        if use_mock is None:
            use_mock = not self.api_key

        if use_mock:
            return self._mock_generate(prompt, config)
        else:
            return self._call_openai_with_retry(prompt, config)

    def is_available(self) -> bool:
        """检查 AI 服务是否可用"""
        return self.api_key is not None


# 全局 AI 服务实例
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """获取 AI 服务实例（单例模式）"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
