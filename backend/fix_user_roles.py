#!/usr/bin/env python3
"""
修复用户角色值以匹配枚举
"""

import sqlite3

def fix_user_roles():
    """修复用户角色值"""
    conn = sqlite3.connect('yueen.db')
    cursor = conn.cursor()

    try:
        # 更新用户角色值
        cursor.execute("UPDATE users SET role = 'user' WHERE role = 'user'")
        cursor.execute("UPDATE users SET role = 'admin' WHERE role = 'admin'")
        cursor.execute("UPDATE users SET role = 'moderator' WHERE role = 'moderator'")

        conn.commit()

        # 检查更新结果
        cursor.execute("SELECT id, name, email, role FROM users")
        users = cursor.fetchall()

        print("✅ 用户角色已修复:")
        for user in users:
            print(f"  ID: {user[0]}, 姓名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}")

    except Exception as e:
        print(f"❌ 修复用户角色失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_user_roles()