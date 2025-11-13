#!/usr/bin/env python3
"""
测试密码验证脚本
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

def test_password_verification():
    """测试密码验证"""
    db = SessionLocal()
    
    try:
        # 查找测试用户
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not user:
            print("❌ 测试用户不存在")
            return
        
        print(f"✅ 找到测试用户: {user.name} (ID: {user.id})")
        print(f"   邮箱: {user.email}")
        print(f"   密码哈希: {user.hashed_password[:50]}...")
        print(f"   激活状态: {user.is_active}")
        print(f"   验证状态: {user.is_verified}")
        
        # 测试密码验证
        test_password = "123456"
        print(f"\n🔍 测试密码: {test_password}")
        
        is_valid = verify_password(test_password, user.hashed_password)
        print(f"   密码验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
        
        # 如果验证失败，尝试重新生成哈希并验证
        if not is_valid:
            print("\n🔄 尝试重新生成密码哈希...")
            new_hash = get_password_hash(test_password)
            print(f"   新哈希: {new_hash[:50]}...")
            
            # 验证新哈希
            new_valid = verify_password(test_password, new_hash)
            print(f"   新哈希验证结果: {'✅ 成功' if new_valid else '❌ 失败'}")
            
            # 如果新哈希有效，更新用户密码
            if new_valid:
                print("\n💾 更新用户密码哈希...")
                user.hashed_password = new_hash
                db.commit()
                print("   ✅ 密码已更新")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_password_verification()