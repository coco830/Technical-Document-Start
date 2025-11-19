#!/usr/bin/env python3
"""
检查企业信息表结构的脚本
"""

import sqlite3
import sys

def check_table_structure():
    try:
        # 连接数据库
        conn = sqlite3.connect('yueen.db')
        cursor = conn.cursor()
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(enterprise_info)")
        columns = cursor.fetchall()
        
        print("企业信息表(enterprise_info)的字段结构:")
        print("-" * 60)
        print(f"{'字段名':<25} {'类型':<15} {'非空':<5} {'默认值':<10} {'主键':<5}")
        print("-" * 60)
        
        has_env_officer = False
        for col in columns:
            cid, name, type_name, not_null, default_val, pk = col
            if name == 'env_officer':
                has_env_officer = True
            print(f"{name:<25} {type_name:<15} {'YES' if not_null else 'NO':<5} {str(default_val):<10} {'YES' if pk else 'NO':<5}")
        
        print("-" * 60)
        print(f"总共找到 {len(columns)} 个字段")
        
        if has_env_officer:
            print("✓ 表中存在 env_officer 字段")
        else:
            print("✗ 表中不存在 env_officer 字段")
            
        return has_env_officer
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    has_env_officer = check_table_structure()
    sys.exit(0 if has_env_officer else 1)