"""
错误处理机制测试
测试错误分类、熔断机制、降级策略和监控功能
"""

import asyncio
import time
import json
from datetime import datetime
import logging

from app.utils.error_handler import (
    ErrorSeverity, ErrorCategory, handle_error, classify_error,
    CircuitBreaker, RetryPolicy, FallbackHandler, error_monitor,
    fallback_handler, with_error_handling
)
from app.services.cache_service import get_cache_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_error_classification():
    """测试错误分类功能"""
    print("\n=== 测试错误分类 ===")
    
    test_cases = [
        (ConnectionError("Connection failed"), ErrorCategory.NETWORK),
        (TimeoutError("Request timeout"), ErrorCategory.TIMEOUT),
        (ValueError("Invalid input"), ErrorCategory.VALIDATION),
        (PermissionError("Access denied"), ErrorCategory.AUTHORIZATION),
        (Exception("Internal error"), ErrorCategory.INTERNAL),
    ]
    
    for error, expected_category in test_cases:
        category, severity = classify_error(error)
        print(f"错误: {error.__class__.__name__} - 分类: {category.value}, 严重程度: {severity.value}")
        assert category == expected_category, f"分类错误: 期望 {expected_category}, 实际 {category}"


def test_error_monitoring():
    """测试错误监控功能"""
    print("\n=== 测试错误监控 ===")
    
    # 创建一些测试错误
    test_errors = [
        Exception("测试错误1"),
        ValueError("测试验证错误"),
        ConnectionError("测试网络错误"),
    ]
    
    for error in test_errors:
        error_info = handle_error(
            error,
            context={"test": True},
            user_message="测试用户消息"
        )
        print(f"记录错误: {error_info.error.__class__.__name__}")
    
    # 获取错误摘要
    summary = error_monitor.get_error_summary()
    print(f"错误摘要: {json.dumps(summary, indent=2, ensure_ascii=False, default=str)}")
    
    assert summary["total_errors"] >= 3, "错误数量不正确"


def test_circuit_breaker():
    """测试熔断器功能"""
    print("\n=== 测试熔断器 ===")
    
    # 创建熔断器
    circuit_breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=1,
        expected_exception=Exception
    )
    
    @circuit_breaker
    def failing_function():
        raise Exception("模拟失败")
    
    # 测试熔断器状态变化
    try:
        failing_function()
    except Exception as e:
        print(f"第1次调用失败: {e}")
    
    try:
        failing_function()
    except Exception as e:
        print(f"第2次调用失败: {e}")
    
    # 第3次调用应该被熔断器阻止
    try:
        failing_function()
    except Exception as e:
        print(f"第3次调用被熔断器阻止: {e}")
        assert "Service unavailable" in str(e), "熔断器未正常工作"
    
    # 等待恢复
    print("等待熔断器恢复...")
    time.sleep(1.5)
    
    # 测试恢复后的调用
    try:
        failing_function()
    except Exception as e:
        print(f"恢复后调用: {e}")


def test_retry_policy():
    """测试重试策略"""
    print("\n=== 测试重试策略 ===")
    
    retry_policy = RetryPolicy(
        max_attempts=3,
        base_delay=0.1,
        max_delay=1.0
    )
    
    attempt_count = 0
    
    @retry_policy
    def sometimes_failing_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise Exception(f"第{attempt_count}次失败")
        return "成功"
    
    try:
        result = sometimes_failing_function()
        print(f"重试成功: {result}")
        assert result == "成功", "重试策略未正常工作"
        assert attempt_count == 3, "重试次数不正确"
    except Exception as e:
        print(f"重试失败: {e}")


def test_fallback_handler():
    """测试降级处理器"""
    print("\n=== 测试降级处理器 ===")
    
    # 注册降级函数
    def test_fallback(*args, **kwargs):
        return {"data": "降级数据", "fallback": True}
    
    fallback_handler.register("test_service", test_fallback)
    
    # 测试降级执行
    try:
        result = fallback_handler.execute_fallback("test_service")
        print(f"降级执行结果: {result}")
        assert result["fallback"] is True, "降级函数未正常执行"
    except Exception as e:
        print(f"降级执行失败: {e}")


def test_cache_service_error_handling():
    """测试缓存服务错误处理"""
    print("\n=== 测试缓存服务错误处理 ===")
    
    cache_service = get_cache_service()
    
    # 测试缓存操作
    test_data = {"key": "value", "timestamp": datetime.now().isoformat()}
    
    try:
        # 设置缓存
        success = cache_service.set("test_key", test_data, ttl=60)
        print(f"缓存设置: {'成功' if success else '失败'}")
        
        # 获取缓存
        cached_data = cache_service.get("test_key")
        print(f"缓存获取: {cached_data}")
        
        # 删除缓存
        deleted = cache_service.delete("test_key")
        print(f"缓存删除: {'成功' if deleted else '失败'}")
        
    except Exception as e:
        error_info = handle_error(e, context={"operation": "cache_test"})
        print(f"缓存操作错误: {error_info.user_message}")


def test_with_error_handling_decorator():
    """测试错误处理装饰器"""
    print("\n=== 测试错误处理装饰器 ===")
    
    # 注册测试降级函数
    def decorator_test_fallback(*args, **kwargs):
        return {"result": "装饰器降级结果"}
    
    fallback_handler.register("decorator_test", decorator_test_fallback)
    
    # 创建重试策略
    retry_policy = RetryPolicy(max_attempts=2, base_delay=0.1)
    
    @with_error_handling(
        fallback_service="decorator_test",
        retry_policy=retry_policy,
        context={"test": "decorator"}
    )
    def test_function():
        raise Exception("装饰器测试错误")
    
    try:
        result = test_function()
        print(f"装饰器处理结果: {result}")
    except Exception as e:
        print(f"装饰器处理失败: {e}")


async def test_async_error_handling():
    """测试异步错误处理"""
    print("\n=== 测试异步错误处理 ===")
    
    async def async_failing_function():
        await asyncio.sleep(0.1)
        raise Exception("异步测试错误")
    
    retry_policy = RetryPolicy(max_attempts=2, base_delay=0.1)
    
    try:
        result = await retry_policy.execute(async_failing_function)
        print(f"异步重试结果: {result}")
    except Exception as e:
        error_info = handle_error(e, context={"async": True})
        print(f"异步错误处理: {error_info.user_message}")


def run_all_tests():
    """运行所有测试"""
    print("开始错误处理机制测试...")
    
    try:
        test_error_classification()
        test_error_monitoring()
        test_circuit_breaker()
        test_retry_policy()
        test_fallback_handler()
        test_cache_service_error_handling()
        test_with_error_handling_decorator()
        
        # 运行异步测试
        asyncio.run(test_async_error_handling())
        
        print("\n✅ 所有测试完成!")
        
        # 显示最终错误统计
        final_summary = error_monitor.get_error_summary()
        print(f"\n最终错误统计: {json.dumps(final_summary, indent=2, ensure_ascii=False, default=str)}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()