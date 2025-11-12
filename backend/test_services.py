#!/usr/bin/env python3
"""
测试缓存服务和AI服务是否能正常工作
"""

import os
import sys

# 添加项目路径到sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cache_service():
    """测试缓存服务"""
    try:
        from app.services.cache_service import get_cache_service
        
        # 获取缓存服务实例（会自动降级到内存缓存，因为没有Redis配置）
        cache_service = get_cache_service()
        print("✓ 缓存服务实例创建成功")
        
        # 测试基本操作
        test_key = "test_key"
        test_data = {"message": "Hello, World!"}
        
        # 设置缓存
        result = cache_service.set(test_key, test_data, ttl=60)
        print(f"✓ 缓存设置成功: {result}")
        
        # 获取缓存
        cached_data = cache_service.get(test_key)
        print(f"✓ 缓存获取成功: {cached_data}")
        
        # 检查键是否存在
        exists = cache_service.exists(test_key)
        print(f"✓ 缓存存在检查: {exists}")
        
        # 获取统计信息
        stats = cache_service.get_stats()
        print(f"✓ 缓存统计: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ 缓存服务测试失败: {e}")
        return False

def test_ai_service():
    """测试AI服务"""
    try:
        from app.services.ai_service import get_ai_service
        
        # 获取AI服务实例
        ai_service = get_ai_service()
        print("✓ AI服务实例创建成功")
        
        # 检查服务是否可用（没有API key时会使用模拟模式）
        available = ai_service.is_available()
        print(f"✓ AI服务可用性检查: {available}")
        
        # 测试模拟生成（因为没有配置API key）
        test_prompt = "请生成一个测试段落"
        test_config = {"temperature": 0.7, "max_tokens": 100}
        
        result = ai_service.generate(test_prompt, test_config, use_mock=True)
        print(f"✓ AI模拟生成成功，长度: {len(result)} 字符")
        
        return True
    except Exception as e:
        print(f"✗ AI服务测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试服务...")
    print("-" * 50)
    
    cache_ok = test_cache_service()
    print()
    ai_ok = test_ai_service()
    
    print("-" * 50)
    if cache_ok and ai_ok:
        print("✓ 所有服务测试通过！")
        return 0
    else:
        print("✗ 部分服务测试失败")
        return 1

if __name__ == "__main__":
    exit(main())