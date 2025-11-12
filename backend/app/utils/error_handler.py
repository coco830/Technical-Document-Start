"""
错误处理工具模块
提供错误分类、熔断机制、降级策略和监控功能
"""

import logging
import time
import traceback
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from functools import wraps
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"


class CircuitBreakerState(Enum):
    """熔断器状态"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open"  # 半开状态


class ErrorInfo:
    """错误信息封装"""
    
    def __init__(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        self.error = error
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.user_message = user_message
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": type(self.error).__name__,
            "error_message": str(self.error),
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "user_message": self.user_message,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback
        }


class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        
    def __call__(self, func: Callable) -> Callable:
        """装饰器实现"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.half_open_calls = 0
                else:
                    raise Exception("Service unavailable - circuit breaker is OPEN")
            
            try:
                result = func(*args, **kwargs)
                
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.half_open_calls += 1
                    if self.half_open_calls >= self.half_open_max_calls:
                        self._reset()
                
                return result
                
            except self.expected_exception as e:
                self._record_failure()
                raise e
                
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置熔断器"""
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _record_failure(self):
        """记录失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPENED for {func.__name__}")
    
    def _reset(self):
        """重置熔断器"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        self.half_open_calls = 0
        logger.info("Circuit breaker RESET to CLOSED")


class RetryPolicy:
    """重试策略"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def __call__(self, func: Callable) -> Callable:
        """装饰器实现"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == self.max_attempts - 1:
                        break
                    
                    delay = self._calculate_delay(attempt)
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {delay:.2f}s")
                    time.sleep(delay)
            
            raise last_exception
            
        return wrapper
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算重试延迟"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay


class FallbackHandler:
    """降级处理器"""
    
    def __init__(self):
        self.fallbacks: Dict[str, Callable] = {}
    
    def register(self, service_name: str, fallback_func: Callable):
        """注册降级函数"""
        self.fallbacks[service_name] = fallback_func
        logger.info(f"Registered fallback for {service_name}")
    
    def get_fallback(self, service_name: str) -> Optional[Callable]:
        """获取降级函数"""
        return self.fallbacks.get(service_name)
    
    def execute_fallback(self, service_name: str, *args, **kwargs):
        """执行降级函数"""
        fallback = self.get_fallback(service_name)
        if fallback:
            logger.info(f"Executing fallback for {service_name}")
            return fallback(*args, **kwargs)
        else:
            raise Exception(f"No fallback registered for {service_name}")


class ErrorMonitor:
    """错误监控器"""
    
    def __init__(self, max_errors: int = 1000):
        self.errors: List[ErrorInfo] = []
        self.max_errors = max_errors
        self.error_counts: Dict[str, int] = {}
        self.error_counts_by_category: Dict[ErrorCategory, int] = {}
        self.error_counts_by_severity: Dict[ErrorSeverity, int] = {}
    
    def record_error(self, error_info: ErrorInfo):
        """记录错误"""
        self.errors.append(error_info)
        
        # 保持错误列表大小
        if len(self.errors) > self.max_errors:
            self.errors.pop(0)
        
        # 更新计数
        error_key = f"{type(error_info.error).__name__}:{error_info.category.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.error_counts_by_category[error_info.category] = \
            self.error_counts_by_category.get(error_info.category, 0) + 1
        self.error_counts_by_severity[error_info.severity] = \
            self.error_counts_by_severity.get(error_info.severity, 0) + 1
        
        # 记录日志
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_info.severity, logging.WARNING)
        
        logger.log(
            log_level,
            f"Error recorded: {error_info.to_dict()}"
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        recent_errors = [
            error for error in self.errors
            if error.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "total_errors": len(self.errors),
            "recent_errors_24h": len(recent_errors),
            "error_counts": self.error_counts,
            "errors_by_category": {
                category.value: count
                for category, count in self.error_counts_by_category.items()
            },
            "errors_by_severity": {
                severity.value: count
                for severity, count in self.error_counts_by_severity.items()
            },
            "recent_critical_errors": [
                error.to_dict() for error in recent_errors
                if error.severity == ErrorSeverity.CRITICAL
            ]
        }


# 全局实例
error_monitor = ErrorMonitor()
fallback_handler = FallbackHandler()


def classify_error(error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
    """错误分类函数"""
    error_type = type(error).__name__
    error_message = str(error).lower()
    
    # 网络错误
    if any(keyword in error_message for keyword in [
        "connection", "timeout", "network", "dns", "socket"
    ]) or error_type in [
        "ConnectionError", "TimeoutError", "NetworkError"
    ]:
        return ErrorCategory.NETWORK, ErrorSeverity.HIGH
    
    # 数据库错误
    if any(keyword in error_message for keyword in [
        "database", "sql", "connection", "constraint", "duplicate"
    ]) or error_type in [
        "DatabaseError", "IntegrityError", "OperationalError"
    ]:
        return ErrorCategory.DATABASE, ErrorSeverity.HIGH
    
    # 认证错误
    if any(keyword in error_message for keyword in [
        "unauthorized", "authentication", "login", "credential"
    ]) or error_type in [
        "AuthenticationError", "UnauthorizedError"
    ]:
        return ErrorCategory.AUTHENTICATION, ErrorSeverity.MEDIUM
    
    # 授权错误
    if any(keyword in error_message for keyword in [
        "forbidden", "permission", "access denied", "unauthorized"
    ]) or error_type in [
        "PermissionError", "ForbiddenError"
    ]:
        return ErrorCategory.AUTHORIZATION, ErrorSeverity.MEDIUM
    
    # 验证错误
    if any(keyword in error_message for keyword in [
        "validation", "invalid", "required", "format"
    ]) or error_type in [
        "ValidationError", "ValueError", "TypeError"
    ]:
        return ErrorCategory.VALIDATION, ErrorSeverity.LOW
    
    # 外部服务错误
    if any(keyword in error_message for keyword in [
        "external", "third party", "api", "service"
    ]) or error_type in [
        "ExternalServiceError", "APIError"
    ]:
        return ErrorCategory.EXTERNAL_SERVICE, ErrorSeverity.HIGH
    
    # 超时错误
    if "timeout" in error_message or error_type in [
        "TimeoutError", "AsyncTimeoutError"
    ]:
        return ErrorCategory.TIMEOUT, ErrorSeverity.HIGH
    
    # 限流错误
    if any(keyword in error_message for keyword in [
        "rate limit", "too many requests", "quota"
    ]) or error_type in [
        "RateLimitError", "TooManyRequestsError"
    ]:
        return ErrorCategory.RATE_LIMIT, ErrorSeverity.MEDIUM
    
    # 默认为内部错误
    return ErrorCategory.INTERNAL, ErrorSeverity.MEDIUM


def get_user_friendly_message(error_info: ErrorInfo) -> str:
    """获取用户友好的错误消息"""
    if error_info.user_message:
        return error_info.user_message
    
    category_messages = {
        ErrorCategory.NETWORK: "网络连接出现问题，请检查您的网络连接后重试",
        ErrorCategory.DATABASE: "数据服务暂时不可用，请稍后重试",
        ErrorCategory.AUTHENTICATION: "身份验证失败，请重新登录",
        ErrorCategory.AUTHORIZATION: "您没有权限执行此操作",
        ErrorCategory.VALIDATION: "输入数据格式不正确，请检查后重试",
        ErrorCategory.EXTERNAL_SERVICE: "外部服务暂时不可用，请稍后重试",
        ErrorCategory.INTERNAL: "系统内部错误，请联系管理员",
        ErrorCategory.TIMEOUT: "请求超时，请稍后重试",
        ErrorCategory.RATE_LIMIT: "请求过于频繁，请稍后再试"
    }
    
    return category_messages.get(error_info.category, "未知错误，请稍后重试")


def handle_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_message: Optional[str] = None
) -> ErrorInfo:
    """统一错误处理函数"""
    category, severity = classify_error(error)
    
    error_info = ErrorInfo(
        error=error,
        category=category,
        severity=severity,
        context=context,
        user_message=user_message
    )
    
    # 记录错误
    error_monitor.record_error(error_info)
    
    return error_info


def with_error_handling(
    fallback_service: Optional[str] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    retry_policy: Optional[RetryPolicy] = None
):
    """错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # 应用重试策略
                if retry_policy:
                    return retry_policy(func)(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
                    
            except Exception as e:
                error_info = handle_error(
                    e,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # 限制长度
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                # 尝试降级处理
                if fallback_service:
                    try:
                        return fallback_handler.execute_fallback(
                            fallback_service, *args, **kwargs
                        )
                    except Exception as fallback_error:
                        logger.error(f"Fallback failed for {fallback_service}: {fallback_error}")
                
                # 重新抛出原始错误
                raise e
                
        # 应用熔断器
        if circuit_breaker:
            wrapper = circuit_breaker(wrapper)
            
        return wrapper
    return decorator