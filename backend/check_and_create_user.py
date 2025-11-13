#!/usr/bin/env python3
"""
检查并创建用户脚本
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import sys
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import user, project, document, comment, enterprise
from app.models.user import User
from app.utils.auth import get_password_hash

def check_and_create_user():
    """检查并创建用户"""
    db = SessionLocal()
    
    try:
        # 检查16515600@qq.com用户
        existing_user = db.query(User).filter(User.email == '16515600@qq.com').first()
        if existing_user:
            print(f'找到用户16515600@qq.com，ID: {existing_user.id}')
            print(f'用户状态: active={existing_user.is_active}, verified={existing_user.is_verified}')
            
            # 测试密码验证
            from app.utils.auth import verify_password
            if verify_password('123456', existing_user.hashed_password):
                print('密码验证成功')
            else:
                print('密码验证失败')
        
        # 检查test@example.com用户
        test_user = db.query(User).filter(User.email == 'test@example.com').first()
        if test_user:
            print(f'测试用户test@example.com已存在，ID: {test_user.id}')
        else:
            print('测试用户test@example.com不存在，正在创建...')
            
            # 创建测试用户
            hashed_password = get_password_hash('123456')
            new_user = User(
                name='测试用户',
                email='test@example.com',
                hashed_password=hashed_password,
                is_active=True,
                is_verified=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f'✅ 测试用户创建成功:')
            print(f'   邮箱: test@example.com')
            print(f'   密码: 123456')
            print(f'   用户ID: {new_user.id}')
        
    except Exception as e:
        print(f'❌ 操作失败: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_create_user()