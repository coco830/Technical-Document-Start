import time
from typing import Dict, Optional, Callable, Any
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
import json
import hashlib

from app.core.config import settings


class RateLimiter:
    """请求频率限制器"""
    
    def __init__(
        self,
        times: int = 60,  # 时间窗口（秒）
        limit: int = 100,  # 限制请求数
        key_func: Optional[Callable[[Request], str]] = None,
        redis_url: Optional[str] = None
    ):
        self.times = times
        self.limit = limit
        self.key_func = key_func or self._default_key_func
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client = None
        
        # 尝试连接Redis
        try:
            self.redis_client = redis.from_url(self.redis_url)
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            # 如果Redis不可用，使用内存存储
            self.memory_store: Dict[str, Dict[str, Any]] = {}
    
    def _default_key_func(self, request: Request) -> str:
        """默认的键生成函数，使用IP地址"""
        # 获取客户端IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # 生成路径特定的键
        path = request.url.path
        return f"rate_limit:{hashlib.md5(f"{ip}:{path}").hexdigest()}"
    
    def is_allowed(self, request: Request) -> bool:
        """检查请求是否被允许"""
        key = self.key_func(request)
        now = time.time()
        window_start = now - self.times
        
        if self.redis_client:
            return self._is_allowed_redis(key, now, window_start)
        else:
            return self._is_allowed_memory(key, now, window_start)
    
    def _is_allowed_redis(self, key: str, now: float, window_start: float) -> bool:
        """使用Redis检查请求频率"""
        try:
            # 清理过期的请求记录
            self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # 获取当前窗口内的请求数
            current_requests = self.redis_client.zcard(key)
            
            if current_requests >= self.limit:
                return False
            
            # 记录当前请求
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, self.times)
            
            return True
        except Exception as e:
            print(f"Redis error in rate limiter: {e}")
            # 如果Redis出错，允许请求
            return True
    
    def _is_allowed_memory(self, key: str, now: float, window_start: float) -> bool:
        """使用内存检查请求频率"""
        if key not in self.memory_store:
            self.memory_store[key] = {"requests": []}
        
        # 清理过期的请求记录
        self.memory_store[key]["requests"] = [
            req_time for req_time in self.memory_store[key]["requests"]
            if req_time > window_start
        ]
        
        # 检查是否超过限制
        if len(self.memory_store[key]["requests"]) >= self.limit:
            return False
        
        # 记录当前请求
        self.memory_store[key]["requests"].append(now)
        
        return True
    
    def get_retry_after(self, request: Request) -> int:
        """获取重试等待时间（秒）"""
        key = self.key_func(request)
        now = time.time()
        window_start = now - self.times
        
        if self.redis_client:
            try:
                # 获取最早的请求时间
                oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
                if oldest_request:
                    _, timestamp = oldest_request[0]
                    # 计算需要等待的时间，使最早的请求移出时间窗口
                    retry_after = int(timestamp + self.times - now)
                    return max(0, retry_after)
            except Exception:
                pass
        else:
            if key in self.memory_store and self.memory_store[key]["requests"]:
                # 获取最早的请求时间
                oldest_request = min(self.memory_store[key]["requests"])
                # 计算需要等待的时间
                retry_after = int(oldest_request + self.times - now)
                return max(0, retry_after)
        
        return self.times


class RateLimitMiddleware(BaseHTTPMiddleware):
    """请求频率限制中间件"""
    
    def __init__(
        self,
        app,
        paths: Dict[str, Dict[str, int]] = None,
        default_limit: Dict[str, int] = None,
        redis_url: Optional[str] = None
    ):
        super().__init__(app)
        self.paths = paths or {}
        self.default_limit = default_limit or {"times": 60, "limit": 100}
        self.redis_url = redis_url or settings.REDIS_URL
        self.limiters: Dict[str, RateLimiter] = {}
        
        # 为不同路径创建限制器
        for path, limit in self.paths.items():
            self.limiters[path] = RateLimiter(
                times=limit.get("times", self.default_limit["times"]),
                limit=limit.get("limit", self.default_limit["limit"]),
                key_func=lambda req: f"path:{path}:{self._get_key(req)}",
                redis_url=self.redis_url
            )
        
        # 创建默认限制器
        self.default_limiter = RateLimiter(
            times=self.default_limit["times"],
            limit=self.default_limit["limit"],
            redis_url=self.redis_url
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        path = request.url.path
        
        # 查找匹配的限制器
        limiter = None
        for pattern, rate_limiter in self.limiters.items():
            if path.startswith(pattern):
                limiter = rate_limiter
                break
        
        # 如果没有匹配的限制器，使用默认限制器
        if not limiter:
            limiter = self.default_limiter
        
        # 检查请求频率
        if not limiter.is_allowed(request):
            retry_after = limiter.get_retry_after(request)
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": True,
                    "message": "请求过于频繁，请稍后再试",
                    "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
                    "path": path,
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limiter.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # 添加速率限制头信息
        response = await call_next(request)
        
        # 获取当前窗口内的请求数
        key = limiter.key_func(request)
        now = time.time()
        window_start = now - limiter.times
        
        remaining = limiter.limit - 1  # 假设当前请求是允许的
        
        if limiter.redis_client:
            try:
                current_requests = limiter.redis_client.zcard(key)
                remaining = max(0, limiter.limit - current_requests)
            except Exception:
                pass
        
        # 添加速率限制头
        response.headers["X-RateLimit-Limit"] = str(limiter.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + limiter.times))
        
        return response
    
    def _get_key(self, request: Request) -> str:
        """获取请求的唯一标识"""
        # 获取客户端IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # 获取用户ID（如果已认证）
        user_id = getattr(request.state, "user_id", None)
        
        if user_id:
            return f"{ip}:{user_id}"
        return ip


# 创建预定义的限制器
def create_auth_limiter(redis_url: Optional[str] = None) -> RateLimiter:
    """创建认证相关的频率限制器"""
    return RateLimiter(
        times=300,  # 5分钟
        limit=5,     # 最多5次尝试
        key_func=lambda req: f"auth:{RateLimitMiddleware._get_key(None, req)}",
        redis_url=redis_url
    )


def create_api_limiter(redis_url: Optional[str] = None) -> RateLimiter:
    """创建API相关的频率限制器"""
    return RateLimiter(
        times=60,    # 1分钟
        limit=100,   # 最多100次请求
        key_func=lambda req: f"api:{RateLimitMiddleware._get_key(None, req)}",
        redis_url=redis_url
    )


def create_upload_limiter(redis_url: Optional[str] = None) -> RateLimiter:
    """创建上传相关的频率限制器"""
    return RateLimiter(
        times=3600,  # 1小时
        limit=10,    # 最多10次上传
        key_func=lambda req: f"upload:{RateLimitMiddleware._get_key(None, req)}",
        redis_url=redis_url
    )