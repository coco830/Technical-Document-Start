#!/usr/bin/env python3
"""详细诊断后端问题"""

import sys
import os
import traceback

# 设置环境
os.environ.setdefault('PYTHONPATH', '.')
sys.path.insert(0, '.')

def test_step(name, func):
    """测试单个步骤"""
    print(f"\n{'='*60}")
    print(f"步骤: {name}")
    print('='*60)
    try:
        func()
        print(f"✅ {name} - 成功")
        return True
    except Exception as e:
        print(f"❌ {name} - 失败")
        print(f"错误: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def test_passlib():
    """测试passlib"""
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("test123")
    assert len(hashed) > 0
    print(f"密码哈希测试: {hashed[:30]}...")

def test_config():
    """测试配置"""
    from app.core.config import settings
    print(f"配置加载成功")
    print(f"  - 项目名称: {settings.PROJECT_NAME}")
    print(f"  - 数据库URL: {settings.DATABASE_URL[:50]}...")

def test_security():
    """测试安全模块"""
    from app.core.security import get_password_hash, verify_password
    password = "test123"
    hashed = get_password_hash(password)
    print(f"哈希结果: {hashed[:30]}...")
    assert verify_password(password, hashed)
    print("密码验证测试通过")

def test_models_import():
    """测试模型导入"""
    print("正在导入基础模型...")
    from app.models.base import Base, BaseModel, TimestampMixin
    print("✅ 基础模型导入成功")

    print("正在导入用户模型...")
    from app.models.user import User, UserSession
    print("✅ 用户模型导入成功")

    print("正在导入其他模型...")
    from app.models import Company, Project, Document, AIGeneration
    print("✅ 其他模型导入成功")

def test_database():
    """测试数据库"""
    from app.core.database import engine, create_tables
    print(f"数据库引擎创建成功")
    print(f"  - 引擎类型: {type(engine)}")

def test_main_import():
    """测试主应用导入"""
    print("正在导入主应用...")
    from main import app
    print("✅ 主应用导入成功")

def main():
    """主函数"""
    print("="*60)
    print("悦恩人机共写平台 - 后端诊断")
    print("="*60)

    tests = [
        ("passlib密码哈希", test_passlib),
        ("配置加载", test_config),
        ("安全模块", test_security),
        ("模型导入", test_models_import),
        ("数据库", test_database),
        ("主应用", test_main_import),
    ]

    results = []
    for name, func in tests:
        result = test_step(name, func)
        results.append((name, result))

    # 总结
    print("\n" + "="*60)
    print("诊断总结")
    print("="*60)
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    failed = sum(1 for _, result in results if not result)
    print(f"\n总计: {len(results)} 项测试")
    print(f"通过: {len(results) - failed} 项")
    print(f"失败: {failed} 项")

    if failed == 0:
        print("\n🎉 所有测试通过！后端应该可以正常启动。")
    else:
        print("\n⚠️ 有测试失败，请检查上述错误。")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
