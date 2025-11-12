#!/usr/bin/env python3
"""
数据库迁移管理脚本
用于应用数据库迁移和版本管理
"""

import os
import sys
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据库路径
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yueen.db")
if DATABASE_URL.startswith("sqlite:///"):
    DB_PATH = DATABASE_URL.replace("sqlite:///", "")
else:
    logger.error("目前仅支持SQLite数据库迁移")
    sys.exit(1)

def ensure_migrations_table(conn: sqlite3.Connection):
    """确保migrations表存在"""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations (
            version INTEGER PRIMARY KEY,
            description TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
    """)
    conn.commit()

def get_applied_migrations(conn: sqlite3.Connection) -> List[int]:
    """获取已应用的迁移版本"""
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM migrations ORDER BY version")
    return [row[0] for row in cursor.fetchall()]

def get_pending_migrations() -> List[Dict[str, Any]]:
    """获取待应用的迁移"""
    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    pending = []
    for file_path in migration_files:
        try:
            version = int(file_path.stem.split("_")[0])
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 从文件内容中提取描述
            description = "未知迁移"
            for line in content.split('\n'):
                if line.strip().startswith('-- 描述：'):
                    description = line.replace('-- 描述：', '').strip()
                    break
            
            pending.append({
                'version': version,
                'description': description,
                'file_path': file_path,
                'content': content
            })
        except (ValueError, IndexError) as e:
            logger.warning(f"跳过无效的迁移文件: {file_path.name} - {e}")
    
    return pending

def apply_migration(conn: sqlite3.Connection, migration: Dict[str, Any]):
    """应用单个迁移"""
    logger.info(f"应用迁移 {migration['version']}: {migration['description']}")
    
    try:
        # 执行迁移SQL
        cursor = conn.cursor()
        cursor.executescript(migration['content'])
        
        # 记录迁移
        cursor.execute(
            "INSERT INTO migrations (version, description, applied_at) VALUES (?, ?, datetime('now'))",
            (migration['version'], migration['description'])
        )
        
        conn.commit()
        logger.info(f"迁移 {migration['version']} 应用成功")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"迁移 {migration['version']} 应用失败: {e}")
        return False

def migrate():
    """执行数据库迁移"""
    logger.info("开始数据库迁移...")
    
    # 连接数据库
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        logger.error(f"无法连接到数据库: {e}")
        return False
    
    try:
        # 确保migrations表存在
        ensure_migrations_table(conn)
        
        # 获取已应用的迁移
        applied_versions = get_applied_migrations(conn)
        logger.info(f"已应用的迁移版本: {applied_versions}")
        
        # 获取待应用的迁移
        pending_migrations = get_pending_migrations()
        logger.info(f"发现 {len(pending_migrations)} 个迁移文件")
        
        # 应用待应用的迁移
        applied_count = 0
        for migration in pending_migrations:
            if migration['version'] not in applied_versions:
                if apply_migration(conn, migration):
                    applied_count += 1
                else:
                    logger.error(f"迁移失败，停止后续迁移")
                    break
            else:
                logger.info(f"迁移 {migration['version']} 已应用，跳过")
        
        logger.info(f"迁移完成，共应用 {applied_count} 个新迁移")
        return True
        
    except Exception as e:
        logger.error(f"迁移过程中发生错误: {e}")
        return False
    finally:
        conn.close()

def rollback_migration(target_version: int):
    """回滚到指定版本（仅用于开发环境）"""
    logger.warning(f"回滚数据库到版本 {target_version}")
    
    # 连接数据库
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        logger.error(f"无法连接到数据库: {e}")
        return False
    
    try:
        # 确保migrations表存在
        ensure_migrations_table(conn)
        
        # 获取当前版本
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM migrations")
        current_version = cursor.fetchone()[0] or 0
        
        if current_version <= target_version:
            logger.info(f"当前版本 {current_version} 已经小于或等于目标版本 {target_version}")
            return True
        
        # 删除大于目标版本的迁移记录
        cursor.execute("DELETE FROM migrations WHERE version > ?", (target_version,))
        conn.commit()
        
        logger.info(f"数据库已回滚到版本 {target_version}")
        logger.warning("注意：回滚仅删除了迁移记录，数据库结构可能需要手动调整")
        return True
        
    except Exception as e:
        logger.error(f"回滚过程中发生错误: {e}")
        return False
    finally:
        conn.close()

def show_status():
    """显示迁移状态"""
    logger.info("查询迁移状态...")
    
    # 连接数据库
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        logger.error(f"无法连接到数据库: {e}")
        return
    
    try:
        # 确保migrations表存在
        ensure_migrations_table(conn)
        
        # 获取已应用的迁移
        applied_versions = get_applied_migrations(conn)
        
        # 获取所有迁移
        pending_migrations = get_pending_migrations()
        
        print("\n=== 数据库迁移状态 ===")
        print(f"数据库路径: {DB_PATH}")
        print(f"当前版本: {max(applied_versions) if applied_versions else 0}")
        print(f"已应用迁移数: {len(applied_versions)}")
        print(f"待应用迁移数: {len([m for m in pending_migrations if m['version'] not in applied_versions])}")
        
        print("\n=== 迁移历史 ===")
        for migration in pending_migrations:
            status = "✓ 已应用" if migration['version'] in applied_versions else "✗ 待应用"
            print(f"  {migration['version']}: {migration['description']} {status}")
        
    except Exception as e:
        logger.error(f"查询状态时发生错误: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法:")
        print("  python migrate.py migrate    # 应用所有待应用的迁移")
        print("  python migrate.py status     # 显示迁移状态")
        print("  python migrate.py rollback N # 回滚到版本N（仅开发环境）")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate":
        success = migrate()
        sys.exit(0 if success else 1)
    elif command == "status":
        show_status()
    elif command == "rollback" and len(sys.argv) == 3:
        try:
            target_version = int(sys.argv[2])
            success = rollback_migration(target_version)
            sys.exit(0 if success else 1)
        except ValueError:
            logger.error("无效的版本号")
            sys.exit(1)
    else:
        print("无效的命令")
        sys.exit(1)

if __name__ == "__main__":
    main()