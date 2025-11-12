"""
缓存服务 - 支持 Redis 和内存缓存自动降级
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from ..utils.error_handler import (
    ErrorCategory, ErrorSeverity, handle_error, with_error_handling,
    CircuitBreaker, RetryPolicy, fallback_handler
)

logger = logging.getLogger(__name__)


class CacheBackend(ABC):
    """缓存后端抽象基类"""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """设置缓存"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存"""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """清除所有缓存"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass


class MemoryCacheBackend(CacheBackend):
    """内存缓存后端（降级方案）"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        logger.info("使用内存缓存后端")

    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        if key not in self._cache:
            return None

        item = self._cache[key]
        # 检查是否过期
        if datetime.now() > item["expires_at"]:
            del self._cache[key]
            return None

        return item["value"]

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """设置缓存"""
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl)
        }
        return True

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> bool:
        """清除所有缓存"""
        self._cache.clear()
        return True

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if key not in self._cache:
            return False
        # 检查是否过期
        if datetime.now() > self._cache[key]["expires_at"]:
            del self._cache[key]
            return False
        return True


class RedisCacheBackend(CacheBackend):
    """Redis 缓存后端"""

    def __init__(self, redis_url: str):
        try:
            import redis
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # 测试连接
            self.client.ping()
            logger.info(f"成功连接到 Redis: {redis_url}")
        except Exception as e:
            error_info = handle_error(
                e,
                context={"redis_url": redis_url, "operation": "redis_connection"},
                user_message="缓存服务初始化失败，将使用内存缓存"
            )
            logger.error(f"连接 Redis 失败: {error_info.to_dict()}")
            raise

    @with_error_handling(
        circuit_breaker=CircuitBreaker(failure_threshold=3, recovery_timeout=30),
        retry_policy=RetryPolicy(max_attempts=2, base_delay=0.5)
    )
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            return self.client.get(key)
        except Exception as e:
            error_info = handle_error(
                e,
                context={"key": key, "operation": "redis_get"},
                user_message="缓存读取失败"
            )
            logger.error(f"Redis GET 失败: {error_info.to_dict()}")
            return None

    @with_error_handling(
        circuit_breaker=CircuitBreaker(failure_threshold=3, recovery_timeout=30),
        retry_policy=RetryPolicy(max_attempts=2, base_delay=0.5)
    )
    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """设置缓存"""
        try:
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            error_info = handle_error(
                e,
                context={"key": key, "ttl": ttl, "operation": "redis_set"},
                user_message="缓存写入失败"
            )
            logger.error(f"Redis SET 失败: {error_info.to_dict()}")
            return False

    @with_error_handling(
        retry_policy=RetryPolicy(max_attempts=2, base_delay=0.5)
    )
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            error_info = handle_error(
                e,
                context={"key": key, "operation": "redis_delete"},
                user_message="缓存删除失败"
            )
            logger.error(f"Redis DELETE 失败: {error_info.to_dict()}")
            return False

    @with_error_handling()
    def clear(self) -> bool:
        """清除所有缓存（清除当前数据库）"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            error_info = handle_error(
                e,
                context={"operation": "redis_clear"},
                user_message="缓存清空失败"
            )
            logger.error(f"Redis CLEAR 失败: {error_info.to_dict()}")
            return False

    @with_error_handling(
        retry_policy=RetryPolicy(max_attempts=2, base_delay=0.5)
    )
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            error_info = handle_error(
                e,
                context={"key": key, "operation": "redis_exists"},
                user_message="缓存检查失败"
            )
            logger.error(f"Redis EXISTS 失败: {error_info.to_dict()}")
            return False


class CacheService:
    """缓存服务 - 统一接口"""

    def __init__(self, backend: CacheBackend):
        self.backend = backend
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }

    @with_error_handling(
        fallback_service="cache_memory_fallback"
    )
    def get(self, key: str) -> Optional[Dict]:
        """获取缓存（自动反序列化 JSON）"""
        try:
            data = self.backend.get(key)
            if data:
                self._stats["hits"] += 1
                return json.loads(data)
            else:
                self._stats["misses"] += 1
                return None
        except Exception as e:
            self._stats["errors"] += 1
            error_info = handle_error(
                e,
                context={"key": key, "operation": "cache_get"},
                user_message="缓存服务暂时不可用"
            )
            logger.error(f"缓存获取失败: {error_info.to_dict()}")
            return None

    @with_error_handling(
        fallback_service="cache_memory_fallback"
    )
    def set(self, key: str, value: Dict, ttl: int = 3600) -> bool:
        """设置缓存（自动序列化为 JSON）"""
        try:
            data = json.dumps(value, ensure_ascii=False)
            success = self.backend.set(key, data, ttl)
            if success:
                self._stats["sets"] += 1
            return success
        except Exception as e:
            self._stats["errors"] += 1
            error_info = handle_error(
                e,
                context={"key": key, "ttl": ttl, "operation": "cache_set"},
                user_message="缓存写入失败"
            )
            logger.error(f"缓存设置失败: {error_info.to_dict()}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        return self.backend.delete(key)

    def clear(self) -> bool:
        """清除所有缓存"""
        return self.backend.clear()

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.backend.exists(key)

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.2f}%"
        }


# 全局缓存服务实例
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    获取缓存服务实例（单例模式）
    自动选择可用的缓存后端
    """
    global _cache_service

    if _cache_service is not None:
        return _cache_service

    # 尝试使用 Redis
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            backend = RedisCacheBackend(redis_url)
            _cache_service = CacheService(backend)
            logger.info("缓存服务已启动，使用 Redis 后端")
            return _cache_service
        except Exception as e:
            error_info = handle_error(
                e,
                context={"redis_url": redis_url, "operation": "cache_service_init"},
                user_message="Redis 缓存不可用，已切换到内存缓存"
            )
            logger.warning(f"Redis 不可用，降级到内存缓存: {error_info.to_dict()}")

    # 降级到内存缓存
    backend = MemoryCacheBackend()
    _cache_service = CacheService(backend)
    logger.info("缓存服务已启动，使用内存缓存后端（降级模式）")

    return _cache_service


# 注册降级处理函数
def memory_cache_fallback(key: str, value: Dict = None, ttl: int = 3600, operation: str = "get") -> Any:
    """内存缓存降级处理函数"""
    memory_backend = MemoryCacheBackend()
    
    if operation == "get":
        return memory_backend.get(key)
    elif operation == "set" and value is not None:
        return memory_backend.set(key, json.dumps(value, ensure_ascii=False), ttl)
    else:
        raise ValueError(f"Unsupported fallback operation: {operation}")


# 注册降级服务
fallback_handler.register("cache_memory_fallback", memory_cache_fallback)
