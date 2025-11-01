"""
缓存服务模块
提供Redis缓存和内存缓存的统一接口
"""
import json
import pickle
import logging
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta

import redis
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """缓存服务类，支持Redis和内存缓存"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_ttl: Dict[str, float] = {}
        
        # 尝试连接Redis
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=False,  # 保持二进制数据
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis缓存服务初始化成功")
        except Exception as e:
            logger.warning(f"Redis连接失败，使用内存缓存: {str(e)}")
            self.redis_client = None
    
    def is_available(self) -> bool:
        """检查Redis是否可用"""
        return self.redis_client is not None
    
    def _serialize(self, value: Any) -> bytes:
        """序列化值"""
        try:
            # 对于简单类型，使用JSON
            if isinstance(value, (str, int, float, bool, type(None))):
                return json.dumps(value).encode('utf-8')
            # 对于复杂对象，使用pickle
            return pickle.dumps(value)
        except Exception as e:
            logger.error(f"缓存序列化失败: {str(e)}")
            raise
    
    def _deserialize(self, value: bytes) -> Any:
        """反序列化值"""
        try:
            # 尝试JSON反序列化
            return json.loads(value.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # 尝试pickle反序列化
                return pickle.loads(value)
            except Exception as e:
                logger.error(f"缓存反序列化失败: {str(e)}")
                raise
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            serialized_value = self._serialize(value)
            
            if self.redis_client:
                # 使用Redis缓存
                if ttl:
                    return self.redis_client.setex(key, ttl, serialized_value)
                else:
                    return self.redis_client.set(key, serialized_value)
            else:
                # 使用内存缓存
                self.memory_cache[key] = value
                if ttl:
                    import time
                    self.memory_cache_ttl[key] = time.time() + ttl
                return True
        except Exception as e:
            logger.error(f"设置缓存失败: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                value = self.redis_client.get(key)
                if value is not None:
                    return self._deserialize(value)
                return None
            else:
                # 使用内存缓存
                import time
                # 检查TTL
                if key in self.memory_cache_ttl and time.time() > self.memory_cache_ttl[key]:
                    self.delete(key)
                    return None
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                return bool(self.redis_client.delete(key))
            else:
                # 使用内存缓存
                self.memory_cache.pop(key, None)
                self.memory_cache_ttl.pop(key, None)
                return True
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                return bool(self.redis_client.exists(key))
            else:
                # 使用内存缓存
                import time
                # 检查TTL
                if key in self.memory_cache_ttl and time.time() > self.memory_cache_ttl[key]:
                    self.delete(key)
                    return False
                return key in self.memory_cache
        except Exception as e:
            logger.error(f"检查缓存存在性失败: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """清空所有缓存"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                return self.redis_client.flushdb()
            else:
                # 使用内存缓存
                self.memory_cache.clear()
                self.memory_cache_ttl.clear()
                return True
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存"""
        result = {}
        try:
            if self.redis_client:
                # 使用Redis缓存
                values = self.redis_client.mget(keys)
                for i, key in enumerate(keys):
                    if i < len(values) and values[i] is not None:
                        result[key] = self._deserialize(values[i])
            else:
                # 使用内存缓存
                import time
                for key in keys:
                    # 检查TTL
                    if key in self.memory_cache_ttl and time.time() > self.memory_cache_ttl[key]:
                        self.delete(key)
                        continue
                    if key in self.memory_cache:
                        result[key] = self.memory_cache[key]
            return result
        except Exception as e:
            logger.error(f"批量获取缓存失败: {str(e)}")
            return {}
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置缓存"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                pipe = self.redis_client.pipeline()
                for key, value in mapping.items():
                    serialized_value = self._serialize(value)
                    if ttl:
                        pipe.setex(key, ttl, serialized_value)
                    else:
                        pipe.set(key, serialized_value)
                pipe.execute()
                return True
            else:
                # 使用内存缓存
                import time
                for key, value in mapping.items():
                    self.memory_cache[key] = value
                    if ttl:
                        self.memory_cache_ttl[key] = time.time() + ttl
                return True
        except Exception as e:
            logger.error(f"批量设置缓存失败: {str(e)}")
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """批量删除缓存"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                return bool(self.redis_client.delete(*keys))
            else:
                # 使用内存缓存
                for key in keys:
                    self.memory_cache.pop(key, None)
                    self.memory_cache_ttl.pop(key, None)
                return True
        except Exception as e:
            logger.error(f"批量删除缓存失败: {str(e)}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """递增缓存值"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                return self.redis_client.incrby(key, amount)
            else:
                # 使用内存缓存
                current = self.memory_cache.get(key, 0)
                if not isinstance(current, int):
                    current = 0
                new_value = current + amount
                self.memory_cache[key] = new_value
                return new_value
        except Exception as e:
            logger.error(f"递增缓存值失败: {str(e)}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            if self.redis_client:
                # 使用Redis缓存
                return bool(self.redis_client.expire(key, ttl))
            else:
                # 使用内存缓存
                import time
                if key in self.memory_cache:
                    self.memory_cache_ttl[key] = time.time() + ttl
                    return True
                return False
        except Exception as e:
            logger.error(f"设置缓存过期时间失败: {str(e)}")
            return False


# 创建全局缓存服务实例
cache_service = CacheService()


def cache_result(key_prefix: str, ttl: int = 300):
    """
    缓存函数结果的装饰器
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 缓存过期时间（秒）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取结果
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            logger.debug(f"缓存设置: {cache_key}")
            
            return result
        return wrapper
    return decorator


def cache_async_result(key_prefix: str, ttl: int = 300):
    """
    缓存异步函数结果的装饰器
    
    Args:
        key_prefix: 缓存键前缀
        ttl: 缓存过期时间（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取结果
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            logger.debug(f"缓存设置: {cache_key}")
            
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern: str) -> bool:
    """
    根据模式使缓存失效
    
    Args:
        pattern: 缓存键模式
        
    Returns:
        是否成功
    """
    try:
        if cache_service.is_available():
            # 使用Redis的SCAN命令查找匹配的键
            keys = []
            for key in cache_service.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return cache_service.delete_many(keys)
            return True
        else:
            # 内存缓存不支持模式匹配
            logger.warning("内存缓存不支持模式匹配失效")
            return False
    except Exception as e:
        logger.error(f"模式匹配缓存失效失败: {str(e)}")
        return False