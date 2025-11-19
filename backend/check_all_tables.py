#!/usr/bin/env python3
"""
检查数据库中所有表的脚本
"""

import sqlite3
import sys

def check_all_tables():
    try:
        # 连接数据库
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("数据库中的所有表:")
        print("-" * 40)
        
        if not tables:
            print("数据库中没有表")
        else:
            for table in tables:
                print(f"- {table[0]}")
        
        print("-" * 40)
        
        # 检查是否有 enterprise_info 表
        has_enterprise_info = any('enterprise_info' in table[0] for table in tables)
        
        if has_enterprise_info:
            print("✓ 数据库中存在 enterprise_info 表")
        else:
            print("✗ 数据库中不存在 enterprise_info 表")
            
        return has_enterprise_info
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    has_enterprise_info = check_all_tables()
    sys.exit(0 if has_enterprise_info else 1)