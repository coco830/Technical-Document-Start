#!/usr/bin/env python3
"""
检查数据库中的用户
"""

import sqlite3

def check_users():
    """检查用户表"""
    conn = sqlite3.connect('yueen.db')
    cursor = conn.cursor()

    try:
        # 检查表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("用户表结构:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'DEFAULT ' + str(col[4]) if col[4] is not None else ''}")

        print("\n用户数据:")
        cursor.execute("SELECT id, name, email, is_active, is_verified FROM users")
        users = cursor.fetchall()

        if not users:
            print("  没有用户数据")
        else:
            for user in users:
                print(f"  ID: {user[0]}, 姓名: {user[1]}, 邮箱: {user[2]}, 激活: {user[3]}, 验证: {user[4]}")

    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()