#!/usr/bin/env python3
"""
调试登录过程脚本
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import sys
sys.path.append(os.path.dirname(__file__))

# 确保所有模型都被导入
from app.database import SessionLocal
from app.models import user, project, document, comment, enterprise
from app.models.user import User
from app.utils.auth import verify_password, get_password_hash

def debug_login():
    """调试登录过程"""
    db = SessionLocal()
    
    try:
        # 查找测试用户
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not user:
            print("❌ 测试用户不存在")
            return
        
        print(f"✅ 找到测试用户: {user.name} (ID: {user.id})")
        print(f"   邮箱: {user.email}")
        print(f"   密码哈希: {user.hashed_password}")
        print(f"   激活状态: {user.is_active}")
        print(f"   验证状态: {user.is_verified}")
        
        # 检查用户对象是否有role属性
        print(f"\n🔍 检查用户属性:")
        print(f"   hasattr(user, 'role'): {hasattr(user, 'role')}")
        if hasattr(user, 'role'):
            print(f"   user.role: {user.role}")
        
        # 测试密码验证
        test_password = "123456"
        print(f"\n🔍 测试密码: {test_password}")
        
        # 直接调用验证函数
        try:
            is_valid = verify_password(test_password, user.hashed_password)
            print(f"   密码验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
        except Exception as e:
            print(f"   密码验证异常: {e}")
        
        # 模拟登录API的验证过程
        print(f"\n🔍 模拟登录API验证过程:")
        
        # 1. 查找用户（使用小写邮箱）
        user_from_api = db.query(User).filter(User.email == "test@example.com".lower()).first()
        print(f"   1. 查找用户: {'✅ 找到' if user_from_api else '❌ 未找到'}")
        
        if user_from_api:
            # 2. 验证密码
            try:
                password_valid = verify_password("123456", user_from_api.hashed_password)
                print(f"   2. 验证密码: {'✅ 成功' if password_valid else '❌ 失败'}")
            except Exception as e:
                print(f"   2. 验证密码异常: {e}")
                password_valid = False
            
            # 3. 检查账户是否激活
            try:
                is_active = user_from_api.is_active
                print(f"   3. 账户激活: {'✅ 是' if is_active else '❌ 否'}")
            except Exception as e:
                print(f"   3. 检查激活状态异常: {e}")
                is_active = False
            
            # 4. 尝试访问用户属性（可能导致错误）
            try:
                user_name = user_from_api.name
                print(f"   4. 用户姓名: {user_name}")
            except Exception as e:
                print(f"   4. 访问用户姓名异常: {e}")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_login()