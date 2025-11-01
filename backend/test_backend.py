#!/usr/bin/env python3
"""测试后端导入问题"""

import sys
import traceback

def test_import(module_name, description):
    """测试导入模块"""
    print(f"\n{'='*60}")
    print(f"测试导入: {description}")
    print(f"模块: {module_name}")
    print('='*60)
    try:
        __import__(module_name)
        print(f"✅ 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试后端模块导入...")

    tests = [
        ("app.models.base", "基础模型"),
        ("app.models.user", "用户模型"),
        ("app.models.project", "项目模型"),
        ("app.models.company", "企业模型"),
        ("app.models.document", "文档模型"),
        ("app.models.ai_generation", "AI生成模型"),
        ("app.models.__init__", "模型初始化"),
    ]

    results = []
    for module_name, description in tests:
        result = test_import(module_name, description)
        results.append((module_name, description, result))

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    for module_name, description, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {description} ({module_name})")

    failed_count = sum(1 for _, _, result in results if not result)
    print(f"\n总计: {len(results)} 个模块")
    print(f"成功: {len(results) - failed_count} 个")
    print(f"失败: {failed_count} 个")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
