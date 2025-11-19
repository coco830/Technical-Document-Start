#!/usr/bin/env python3
"""
执行数据库迁移的脚本
"""

import sqlite3
import os
import sys

def execute_migration(migration_file):
    """执行指定的迁移文件"""
    try:
        # 检查迁移文件是否存在
        if not os.path.exists(migration_file):
            print(f"错误: 迁移文件 {migration_file} 不存在")
            return False
            
        # 连接数据库
        conn = sqlite3.connect('yueen.db')
        cursor = conn.cursor()
        
        # 读取迁移文件内容
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # 执行迁移
        print(f"正在执行迁移: {migration_file}")
        cursor.executescript(migration_sql)
        
        # 提交更改
        conn.commit()
        print(f"✓ 迁移 {migration_file} 执行成功")
        
        return True
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    except Exception as e:
        print(f"执行迁移时出错: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python execute_migration.py <迁移文件路径>")
        sys.exit(1)
        
    migration_file = sys.argv[1]
    success = execute_migration(migration_file)
    sys.exit(0 if success else 1)