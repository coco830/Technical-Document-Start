#!/usr/bin/env python3
"""
数据库初始化脚本
创建所有数据表
"""
from app.database import Base, engine
from app.models.user import User
from app.models.project import Project
from app.models.document import Document

def init_database():
    """初始化数据库，创建所有表"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建完成！")
    print(f"✓ 已创建表: {', '.join(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_database()
