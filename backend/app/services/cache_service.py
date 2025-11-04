"""
缓存服务 - 支持 Redis 和内存缓存自动降级
"""

import json
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

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
            logger.error(f"连接 Redis 失败: {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET 失败: {e}")
            return None

    def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """设置缓存"""
        try:
            self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET 失败: {e}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE 失败: {e}")
            return False

    def clear(self) -> bool:
        """清除所有缓存（清除当前数据库）"""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis CLEAR 失败: {e}")
            return False

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS 失败: {e}")
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
            logger.error(f"缓存获取失败: {e}")
            return None

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
            logger.error(f"缓存设置失败: {e}")
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
            logger.warning(f"Redis 不可用，降级到内存缓存: {e}")

    # 降级到内存缓存
    backend = MemoryCacheBackend()
    _cache_service = CacheService(backend)
    logger.info("缓存服务已启动，使用内存缓存后端（降级模式）")

    return _cache_service
