#!/usr/bin/env python3
"""
添加用户角色列到SQLite数据库
"""
import sqlite3
import os

def add_role_column():
    """添加role列到users表"""
    db_path = os.path.join(os.path.dirname(__file__), 'yueen.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查role列是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role' not in columns:
            print("添加role列到users表...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user' NOT NULL")
            
            # 创建索引
            cursor.execute("CREATE INDEX idx_users_role ON users(role)")
            
            # 更新现有用户
            cursor.execute("UPDATE users SET role = CASE WHEN id = 1 THEN 'admin' ELSE 'user' END WHERE role IS NULL OR role = 'user'")
            
            conn.commit()
            print("✅ 成功添加role列")
        else:
            print("role列已存在")
            
    except Exception as e:
        print(f"❌ 添加role列失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_role_column()