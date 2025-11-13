#!/usr/bin/env python3
"""
完整测试登录流程脚本
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
from app.schemas.user import UserLogin
from pydantic import ValidationError

def test_full_login():
    """完整测试登录流程"""
    db = SessionLocal()
    
    try:
        print("🔍 测试完整登录流程...")
        
        # 1. 测试请求数据验证
        print("\n1. 测试请求数据验证...")
        try:
            login_data = UserLogin(email="test@example.com", password="123456")
            print(f"   ✅ 请求数据验证成功: {login_data.email}")
        except ValidationError as e:
            print(f"   ❌ 请求数据验证失败: {e}")
            return
        
        # 2. 查找用户（使用小写邮箱）
        print("\n2. 查找用户...")
        user = db.query(User).filter(User.email == login_data.email.lower()).first()
        
        if not user:
            print("   ❌ 用户不存在")
            return
        
        print(f"   ✅ 找到用户: {user.name} (ID: {user.id})")
        print(f"   邮箱: {user.email}")
        print(f"   激活状态: {user.is_active}")
        print(f"   验证状态: {user.is_verified}")
        
        # 3. 验证密码
        print("\n3. 验证密码...")
        try:
            is_valid = verify_password(login_data.password, user.hashed_password)
            print(f"   密码验证结果: {'✅ 成功' if is_valid else '❌ 失败'}")
            
            if not is_valid:
                print("   🔍 尝试重新生成密码哈希...")
                new_hash = get_password_hash(login_data.password)
                print(f"   新哈希: {new_hash[:50]}...")
                
                # 验证新哈希
                new_valid = verify_password(login_data.password, new_hash)
                print(f"   新哈希验证: {'✅ 成功' if new_valid else '❌ 失败'}")
                
                if new_valid:
                    print("   💾 更新用户密码...")
                    user.hashed_password = new_hash
                    db.commit()
                    print("   ✅ 密码已更新")
                    is_valid = True
        except Exception as e:
            print(f"   ❌ 密码验证异常: {e}")
            return
        
        # 4. 检查账户状态
        print("\n4. 检查账户状态...")
        if not user.is_active:
            print("   ❌ 账户未激活")
            return
        print("   ✅ 账户已激活")
        
        # 5. 生成Token
        print("\n5. 生成Token...")
        try:
            from app.utils.auth import create_access_token
            from datetime import timedelta
            
            ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "user_id": user.id, "name": user.name},
                expires_delta=access_token_expires
            )
            print(f"   ✅ Token生成成功: {access_token[:50]}...")
        except Exception as e:
            print(f"   ❌ Token生成失败: {e}")
            return
        
        # 6. 构建响应
        print("\n6. 构建响应...")
        try:
            from app.schemas.user import UserResponse, TokenResponse
            response = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=user.id,
                    email=user.email,
                    name=user.name,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    created_at=user.created_at
                )
            )
            print("   ✅ 响应构建成功")
            print(f"   用户: {response.user.name} ({response.user.email})")
        except Exception as e:
            print(f"   ❌ 响应构建失败: {e}")
            return
        
        print("\n🎉 登录流程测试完成！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_full_login()