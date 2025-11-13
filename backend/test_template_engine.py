#!/usr/bin/env python3
"""
模板引擎测试脚本

用于验证template_engine模块的功能是否正常
"""

import sys
import os
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from template_engine import load_section_templates, get_section_template, get_available_chapters
    from template_engine.models import SectionTemplate
    print("✓ 模块导入成功")
except ImportError as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

def test_load_section_templates():
    """测试加载章节模板"""
    print("\n=== 测试加载章节模板 ===")
    try:
        templates = load_section_templates("2")
        print(f"✓ 成功加载 {len(templates)} 个模板")
        
        for template in templates:
            print(f"  - {template.id}: {template.title} ({template.type})")
            
        return True
    except Exception as e:
        print(f"✗ 加载失败: {e}")
        return False

def test_get_section_template():
    """测试获取特定小节模板"""
    print("\n=== 测试获取特定小节模板 ===")
    try:
        template = get_section_template("2", "2.1")
        if template:
            print(f"✓ 成功获取模板: {template.title}")
            print(f"  类型: {template.type}")
            print(f"  输入变量: {template.input_vars}")
            return True
        else:
            print("✗ 未找到模板")
            return False
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        return False

def test_get_available_chapters():
    """测试获取可用章节列表"""
    print("\n=== 测试获取可用章节列表 ===")
    try:
        chapters = get_available_chapters()
        print(f"✓ 可用章节: {chapters}")
        return True
    except Exception as e:
        print(f"✗ 获取失败: {e}")
        return False

def test_section_template_validation():
    """测试SectionTemplate数据验证"""
    print("\n=== 测试SectionTemplate数据验证 ===")
    try:
        # 测试有效数据
        valid_data = {
            "id": "1.1",
            "chapter_id": "1",
            "title": "测试章节",
            "type": "fixed",
            "input_vars": None,
            "template_text": "这是一个测试模板",
            "ai_prompt_hint": None
        }
        template = SectionTemplate(**valid_data)
        print("✓ 有效数据验证通过")
        
        # 测试无效数据
        try:
            invalid_data = {
                "id": "1.1",
                "chapter_id": "1",
                "title": "测试章节",
                "type": "invalid_type",  # 无效类型
                "input_vars": None,
                "template_text": "这是一个测试模板",
                "ai_prompt_hint": None
            }
            template = SectionTemplate(**invalid_data)
            print("✗ 无效数据验证失败（应该抛出异常）")
            return False
        except Exception:
            print("✓ 无效数据验证通过（正确抛出异常）")
            return True
            
    except Exception as e:
        print(f"✗ 验证失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试模板引擎模块...")
    
    tests = [
        test_load_section_templates,
        test_get_section_template,
        test_get_available_chapters,
        test_section_template_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！模板引擎模块工作正常。")
        sys.exit(0)
    else:
        print("✗ 部分测试失败，请检查实现。")
        sys.exit(1)