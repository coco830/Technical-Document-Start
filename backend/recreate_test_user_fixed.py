#!/usr/bin/env python3
"""
重新创建测试用户脚本（修复版）
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
from app.utils.auth import get_password_hash, verify_password

def recreate_test_user():
    """重新创建测试用户"""
    db = SessionLocal()
    
    try:
        # 查找现有测试用户
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if existing_user:
            print(f"找到现有测试用户: {existing_user.name} (ID: {existing_user.id})")
            
            # 测试当前密码
            current_password = "test123456"  # 使用符合密码策略的密码（字母+数字）
            is_valid = verify_password(current_password, existing_user.hashed_password)
            print(f"当前密码验证: {'✅ 成功' if is_valid else '❌ 失败'}")
            
            # 无论是否成功，都重新生成密码哈希
            print("\n重新生成密码哈希...")
            new_hash = get_password_hash(current_password)
            print(f"新哈希: {new_hash[:50]}...")
            
            # 验证新哈希
            new_valid = verify_password(current_password, new_hash)
            print(f"新哈希验证: {'✅ 成功' if new_valid else '❌ 失败'}")
            
            if new_valid:
                # 更新用户密码
                existing_user.hashed_password = new_hash
                existing_user.is_active = True
                existing_user.is_verified = True
                db.commit()
                print("\n✅ 测试用户密码已更新")
            else:
                print("\n❌ 新哈希验证失败，不更新密码")
        else:
            print("测试用户不存在，正在创建...")
            
            # 创建新用户
            hashed_password = get_password_hash("test123456")  # 使用符合密码策略的密码
            new_user = User(
                name="测试用户",
                email="test@example.com",
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"\n✅ 测试用户创建成功:")
            print(f"   邮箱: test@example.com")
            print(f"   密码: test123456")
            print(f"   用户ID: {new_user.id}")
        
        # 最终验证
        print("\n🔍 最终验证...")
        final_user = db.query(User).filter(User.email == "test@example.com").first()
        if final_user:
            final_valid = verify_password("test123456", final_user.hashed_password)
            print(f"最终密码验证: {'✅ 成功' if final_valid else '❌ 失败'}")
            print(f"用户状态: 激活={final_user.is_active}, 验证={final_user.is_verified}")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_test_user()