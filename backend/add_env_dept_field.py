#!/usr/bin/env python3
"""
手动添加env_dept字段到enterprise_info表
"""

import sqlite3
import os
import sys

def add_env_dept_field():
    """添加env_dept字段到enterprise_info表"""
    
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(__file__), 'yueen.db')
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(enterprise_info)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'env_dept' in columns:
            print("env_dept字段已存在，无需添加")
            return True
        
        # 添加字段
        cursor.execute("ALTER TABLE enterprise_info ADD COLUMN env_dept VARCHAR(255)")
        conn.commit()
        
        print("✅ 成功添加env_dept字段到enterprise_info表")
        
        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(enterprise_info)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'env_dept' in columns:
            print("✅ 字段验证成功")
            return True
        else:
            print("❌ 字段验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 添加字段时出错: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = add_env_dept_field()
    sys.exit(0 if success else 1)