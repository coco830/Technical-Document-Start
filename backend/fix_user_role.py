#!/usr/bin/env python3
"""
修复用户表缺少role字段的问题
"""

import sqlite3
import os

def fix_user_role():
    """为users表添加role字段"""
    db_path = "yueen.db"

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查是否已经存在role字段
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'role' in columns:
            print("role字段已存在")
            return True

        # 添加role字段
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        print("成功添加role字段")

        # 为现有用户设置默认role
        cursor.execute("UPDATE users SET role = 'user' WHERE role IS NULL")
        print("为现有用户设置默认role")

        # 如果有用户，将第一个用户设为管理员
        cursor.execute("SELECT id FROM users ORDER BY id LIMIT 1")
        first_user = cursor.fetchone()
        if first_user:
            cursor.execute("UPDATE users SET role = 'admin' WHERE id = ?", (first_user[0],))
            print(f"将用户ID {first_user[0]} 设为管理员")

        conn.commit()
        print("数据库修复完成")
        return True

    except Exception as e:
        print(f"修复数据库时出错: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_user_role()