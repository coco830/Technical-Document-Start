"""
AI 服务测试脚本
测试 OpenAI API 集成、使用量统计和降级策略
"""

import os
import sys
import logging
from datetime import date

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ai_service import AIService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_ai_service():
    """测试 AI 服务功能"""
    print("=" * 60)
    print("AI 服务测试开始")
    print("=" * 60)
    
    # 创建 AI 服务实例
    ai_service = AIService()
    
    # 测试 1: 检查服务可用性
    print("\n1. 检查服务可用性:")
    is_available = ai_service.is_available()
    print(f"   AI 服务可用: {is_available}")
    print(f"   API 密钥状态: {'已配置' if ai_service.api_key else '未配置'}")
    print(f"   使用模型: {ai_service.default_model}")
    
    # 测试 2: 测试使用量限制
    print("\n2. 测试使用量限制:")
    user_id = "test_user_123"
    
    # 检查初始使用量
    user_usage = ai_service.get_user_usage(user_id)
    print(f"   用户初始使用量: {user_usage}")
    
    # 测试 3: 测试内容生成
    print("\n3. 测试内容生成:")
    test_prompt = "请生成一个关于企业安全生产管理的章节内容"
    test_config = {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        # 测试真实 API（如果可用）
        if is_available:
            print("   尝试使用真实 API 生成...")
            result = ai_service.generate(test_prompt, test_config, user_id=user_id)
            print(f"   生成成功，内容长度: {len(result)} 字符")
            print(f"   内容预览: {result[:200]}...")
        else:
            print("   API 不可用，使用模拟生成...")
            result = ai_service.generate(test_prompt, test_config, user_id=user_id)
            print(f"   模拟生成成功，内容长度: {len(result)} 字符")
            print(f"   内容预览: {result[:200]}...")
    except Exception as e:
        print(f"   生成失败: {e}")
    
    # 测试 4: 检查使用量统计
    print("\n4. 检查使用量统计:")
    updated_usage = ai_service.get_user_usage(user_id)
    print(f"   更新后用户使用量: {updated_usage}")
    
    global_stats = ai_service.get_usage_stats()
    print(f"   全局使用量统计: {global_stats}")
    
    # 测试 5: 测试使用量限制
    print("\n5. 测试使用量限制:")
    # 临时设置低限制进行测试
    original_limit = ai_service.user_daily_limit
    ai_service.user_daily_limit = 2
    
    # 重置使用量统计
    ai_service._usage_stats["daily"] = {}
    ai_service._usage_stats["last_reset"] = date.today().isoformat()
    
    # 连续生成直到触发限制
    for i in range(3):
        try:
            print(f"   第 {i+1} 次生成尝试...")
            result = ai_service.generate(test_prompt, test_config, user_id=user_id)
            print(f"   生成成功，是否模拟: {'是' if '模拟生成' in result else '否'}")
        except Exception as e:
            print(f"   生成失败: {e}")
    
    # 恢复原始限制
    ai_service.user_daily_limit = original_limit
    
    # 测试 6: 测试 API 密钥验证
    print("\n6. 测试 API 密钥验证:")
    # 临时设置无效密钥
    original_key = ai_service.api_key
    ai_service.api_key = "invalid-key"
    
    is_valid = ai_service._validate_api_key()
    print(f"   无效密钥验证结果: {is_valid}")
    
    # 恢复原始密钥
    ai_service.api_key = original_key
    
    print("\n" + "=" * 60)
    print("AI 服务测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_ai_service()