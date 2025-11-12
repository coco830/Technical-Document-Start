#!/usr/bin/env python3
"""
测试redis和openai依赖是否正确安装
"""

def test_redis():
    """测试redis依赖"""
    try:
        import redis
        print(f"✓ Redis 导入成功，版本: {redis.__version__}")
        
        # 测试基本功能
        # 注意：这里不实际连接Redis，只测试API是否可用
        print(f"✓ Redis from_url 方法可用: {hasattr(redis, 'from_url')}")
        return True
    except ImportError as e:
        print(f"✗ Redis 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ Redis 测试失败: {e}")
        return False

def test_openai():
    """测试openai依赖"""
    try:
        import openai
        print(f"✓ OpenAI 导入成功，版本: {openai.__version__}")
        
        # 测试基本功能
        from openai import OpenAI
        print(f"✓ OpenAI 类可用: {OpenAI}")
        
        # 检查chat completions API是否可用
        print(f"✓ OpenAI chat completions API可用: {hasattr(OpenAI, 'chat')}")
        return True
    except ImportError as e:
        print(f"✗ OpenAI 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ OpenAI 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试依赖安装...")
    print("-" * 50)
    
    redis_ok = test_redis()
    print()
    openai_ok = test_openai()
    
    print("-" * 50)
    if redis_ok and openai_ok:
        print("✓ 所有依赖测试通过！")
        return 0
    else:
        print("✗ 部分依赖测试失败")
        return 1

if __name__ == "__main__":
    exit(main())