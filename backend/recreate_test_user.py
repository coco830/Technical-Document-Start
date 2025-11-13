#!/usr/bin/env python3
"""
重新创建测试用户脚本
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

def recreate_test_user():
    """重新创建测试用户"""
    db = SessionLocal()
    
    try:
        # 删除现有测试用户
        existing_user = db.query(User).filter(User.email == 'test@example.com').first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print('删除现有测试用户')
        
        # 创建新测试用户
        hashed_password = get_password_hash('123456')
        test_user = User(
            name='测试用户',
            email='test@example.com',
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f'✅ 测试用户创建成功:')
        print(f'   邮箱: test@example.com')
        print(f'   密码: 123456')
        print(f'   用户ID: {test_user.id}')
        
    except Exception as e:
        print(f'❌ 创建测试用户失败: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_test_user()