#!/usr/bin/env python3
"""
简单检查用户脚本
"""
import sqlite3
import os

def check_user():
    """检查用户"""
    # 使用项目根目录的数据库文件，与app/database.py保持一致
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'yueen.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查用户表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("用户表存在")
        
        # 获取用户信息
        cursor.execute("SELECT id, email, name, hashed_password, is_active, is_verified FROM users WHERE email = ?", ('test@example.com',))
        user = cursor.fetchone()
        
        if user:
            print(f"找到测试用户:")
            print(f"  ID: {user[0]}")
            print(f"  邮箱: {user[1]}")
            print(f"  姓名: {user[2]}")
            print(f"  密码哈希: {user[3][:50]}...")
            print(f"  激活: {user[4]}")
            print(f"  验证: {user[5]}")
        else:
            print("测试用户不存在")
    else:
        print("用户表不存在")
    
    conn.close()

if __name__ == "__main__":
    check_user()