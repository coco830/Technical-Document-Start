"""
AI 服务 - 支持多种 AI 模型和重试机制，包含使用量统计和限制
"""

import os
import time
import json
from typing import Dict, Optional, Tuple
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class AIService:
    """AI 生成服务，支持使用量统计和限制"""

    def __init__(self):
        # API 配置
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.default_model = os.getenv("AI_MODEL", "gpt-4")
        
        # 限制配置
        self.daily_limit = int(os.getenv("AI_DAILY_LIMIT", "100"))
        self.user_daily_limit = int(os.getenv("AI_USER_DAILY_LIMIT", "10"))
        self.request_timeout = int(os.getenv("AI_REQUEST_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("AI_MAX_RETRIES", "3"))
        
        # 使用量统计（内存存储，生产环境应使用Redis或数据库）
        self._usage_stats = {
            "daily": {},  # 按日期统计 {date: {"total": count, "users": {user_id: count}}}
            "last_reset": date.today().isoformat()
        }

        # 检查是否配置了 API Key
        if self.api_key:
            logger.info(f"AI 服务已启动，使用模型: {self.default_model}")
            logger.info(f"使用限制: 全局每日 {self.daily_limit} 次，用户每日 {self.user_daily_limit} 次")
        else:
            logger.warning("未配置 OPENAI_API_KEY，将使用模拟生成")

    def _reset_daily_usage_if_needed(self):
        """如果需要，重置每日使用量统计"""
        today = date.today().isoformat()
        if self._usage_stats["last_reset"] != today:
            self._usage_stats["daily"] = {}
            self._usage_stats["last_reset"] = today
            logger.info(f"每日使用量统计已重置 ({today})")

    def _check_usage_limits(self, user_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        检查使用量限制
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            (是否允许, 拒绝原因)
        """
        self._reset_daily_usage_if_needed()
        
        today = date.today().isoformat()
        if today not in self._usage_stats["daily"]:
            self._usage_stats["daily"][today] = {"total": 0, "users": {}}
        
        daily_stats = self._usage_stats["daily"][today]
        
        # 检查全局每日限制
        if daily_stats["total"] >= self.daily_limit:
            return False, f"已达到全局每日使用限制 ({self.daily_limit} 次)"
        
        # 检查用户每日限制
        if user_id:
            user_usage = daily_stats["users"].get(str(user_id), 0)
            if user_usage >= self.user_daily_limit:
                return False, f"已达到个人每日使用限制 ({self.user_daily_limit} 次)"
        
        return True, ""

    def _record_usage(self, user_id: Optional[str] = None):
        """记录使用量"""
        today = date.today().isoformat()
        if today not in self._usage_stats["daily"]:
            self._usage_stats["daily"][today] = {"total": 0, "users": {}}
        
        daily_stats = self._usage_stats["daily"][today]
        daily_stats["total"] += 1
        
        if user_id:
            user_id_str = str(user_id)
            daily_stats["users"][user_id_str] = daily_stats["users"].get(user_id_str, 0) + 1
        
        logger.info(f"AI 使用量已记录 - 今日总计: {daily_stats['total']}, 用户: {user_id}")

    def _validate_api_key(self) -> bool:
        """验证API密钥是否有效"""
        if not self.api_key:
            return False
        
        # 简单验证API密钥格式
        if not self.api_key.startswith("sk-") or len(self.api_key) < 20:
            logger.warning("API密钥格式可能不正确")
            return False
        
        return True

    def _call_openai_with_retry(
        self,
        prompt: str,
        config: Dict,
        max_retries: Optional[int] = None
    ) -> str:
        """
        调用 OpenAI API（带重试机制）

        Args:
            prompt: Prompt 文本
            config: AI 配置
            max_retries: 最大重试次数（None 使用默认值）

        Returns:
            生成的文本

        Raises:
            Exception: 所有重试失败后抛出异常
        """
        if not self._validate_api_key():
            raise ValueError("无效的 OpenAI API 密钥")
        
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("请安装 openai 包: pip install openai")

        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.request_timeout
        )

        max_retries = max_retries or self.max_retries
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用 OpenAI API (尝试 {attempt + 1}/{max_retries})")

                response = client.chat.completions.create(
                    model=config.get("model", self.default_model),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=config.get("temperature", 0.7),
                    max_tokens=config.get("max_tokens", 2000)
                )

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("API 返回空内容")
                
                logger.info(f"AI 生成成功，返回 {len(content)} 字符")
                return content

            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # 根据错误类型进行不同处理
                if "rate_limit" in error_msg.lower() or "too many requests" in error_msg.lower():
                    logger.warning(f"API 速率限制 (尝试 {attempt + 1}/{max_retries}): {e}")
                    wait_time = 60  # 速率限制时等待更长时间
                elif "timeout" in error_msg.lower():
                    logger.warning(f"API 超时 (尝试 {attempt + 1}/{max_retries}): {e}")
                    wait_time = 5
                elif "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    logger.error(f"API 认证失败: {e}")
                    raise ValueError("API 密钥无效或已过期")
                else:
                    logger.warning(f"API 调用失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    wait_time = 2 ** attempt  # 指数退避：2, 4, 8 秒

                # 如果不是最后一次尝试，等待后重试
                if attempt < max_retries - 1:
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
        user_id: Optional[str] = None,
        use_mock: Optional[bool] = None
    ) -> str:
        """
        生成 AI 内容

        Args:
            prompt: Prompt 文本
            config: AI 配置
            user_id: 用户ID（用于使用量统计）
            use_mock: 是否使用模拟生成（None 表示自动判断）

        Returns:
            生成的文本
        """
        # 自动判断是否使用模拟
        if use_mock is None:
            use_mock = not self.api_key
        
        # 检查使用量限制（仅对真实API调用）
        if not use_mock:
            allowed, reason = self._check_usage_limits(user_id)
            if not allowed:
                logger.warning(f"AI 生成被拒绝: {reason}")
                # 如果超过限制，降级到模拟生成
                logger.info("超过使用限制，降级到模拟生成")
                use_mock = True
        
        try:
            if use_mock:
                result = self._mock_generate(prompt, config)
            else:
                result = self._call_openai_with_retry(prompt, config)
                # 只有真实API调用才记录使用量
                self._record_usage(user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"AI 生成失败: {e}")
            # 如果真实API失败，尝试降级到模拟生成
            if not use_mock:
                logger.info("真实API失败，降级到模拟生成")
                return self._mock_generate(prompt, config)
            else:
                raise

    def is_available(self) -> bool:
        """检查 AI 服务是否可用"""
        return self.api_key is not None and self._validate_api_key()

    def get_usage_stats(self) -> Dict:
        """获取使用量统计"""
        self._reset_daily_usage_if_needed()
        return {
            "daily_limit": self.daily_limit,
            "user_daily_limit": self.user_daily_limit,
            "usage": self._usage_stats["daily"]
        }

    def get_user_usage(self, user_id: str) -> Dict:
        """获取特定用户的使用量"""
        self._reset_daily_usage_if_needed()
        today = date.today().isoformat()
        
        if today not in self._usage_stats["daily"]:
            return {"today": 0, "remaining": self.user_daily_limit}
        
        user_usage = self._usage_stats["daily"][today]["users"].get(str(user_id), 0)
        return {
            "today": user_usage,
            "remaining": max(0, self.user_daily_limit - user_usage),
            "limit": self.user_daily_limit
        }


# 全局 AI 服务实例
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """获取 AI 服务实例（单例模式）"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
