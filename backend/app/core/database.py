import time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.engine import Engine
import logging

from app.core.config import settings
from app.models import Base

# 设置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
if "sqlite" in settings.DATABASE_URL:
    # SQLite配置
    engine = create_engine(
        settings.DATABASE_URL,
        # SQLite特定配置
        connect_args={"check_same_thread": False},
        echo=getattr(settings, 'DEBUG', False)  # 开发环境开启SQL日志
    )
else:
    # MySQL或其他数据库配置
    engine = create_engine(
        settings.DATABASE_URL,
        # 根据数据库类型选择连接池
        poolclass=QueuePool,
        # 连接池配置
        pool_size=20,  # 连接池大小
        max_overflow=30,  # 最大溢出连接数
        pool_pre_ping=True,  # 连接前检查连接是否有效
        pool_recycle=3600,  # 连接回收时间（秒）
        echo=getattr(settings, 'DEBUG', False)  # 开发环境开启SQL日志
    )

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # 防止会话提交后对象过期
)


@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """SQL查询执行前的钩子，用于记录慢查询"""
    if not hasattr(context, 'query_start_time'):
        context.query_start_time = time.time()
    conn.info.setdefault('query_start_time', context.query_start_time)


@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """SQL查询执行后的钩子，用于记录慢查询"""
    total = time.time() - context.query_start_time
    
    # 记录超过1秒的查询
    if total > 1.0:
        logger.warning(f"慢查询检测: {total:.2f}s - {statement[:100]}...")
    
    # 记录所有查询的执行时间（仅在调试模式）
    if getattr(settings, 'DEBUG', False):
        logger.debug(f"查询执行时间: {total:.4f}s - {statement[:100]}...")


def create_tables():
    """创建所有表"""
    # 在SQLAlchemy 2.0中，使用Base.metadata.create_all
    try:
        # 直接使用Base的metadata
        from app.models import Base
        
        # 检查Base是否有metadata属性
        if hasattr(Base, 'metadata'):
            Base.metadata.create_all(bind=engine)
        else:
            # 如果没有metadata属性，尝试使用DeclarativeBase.metadata
            from sqlalchemy.orm import DeclarativeBase
            from sqlalchemy import MetaData
            
            # 创建元数据对象
            metadata = MetaData()
            
            # 获取所有模型类
            from app.models import User, Company, Project, Document, AIGeneration, DocumentExport
            
            # 创建表
            metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        raise


def get_db() -> Session:
    """
    获取数据库会话
    
    使用依赖注入模式，确保每个请求都有一个独立的数据库会话，
    并在请求结束后自动关闭会话。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """数据库管理器，提供高级数据库操作"""
    
    @staticmethod
    def execute_raw_sql(db: Session, sql: str, params: dict = None):
        """执行原生SQL"""
        try:
            result = db.execute(sql, params or {})
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"执行SQL失败: {str(e)}")
            raise
    
    @staticmethod
    def bulk_insert(db: Session, model_class, data_list: list):
        """批量插入数据"""
        try:
            db.bulk_insert_mappings(model_class, data_list)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"批量插入失败: {str(e)}")
            return False
    
    @staticmethod
    def bulk_update(db: Session, model_class, data_list: list, index_field: str = 'id'):
        """批量更新数据"""
        try:
            db.bulk_update_mappings(model_class, data_list)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"批量更新失败: {str(e)}")
            return False
    
    @staticmethod
    def get_table_count(db: Session, table_name: str) -> int:
        """获取表记录数"""
        try:
            result = db.execute(f"SELECT COUNT(*) FROM {table_name}")
            return result.scalar()
        except Exception as e:
            logger.error(f"获取表记录数失败: {str(e)}")
            return 0
    
    @staticmethod
    def analyze_table(db: Session, table_name: str):
        """分析表（MySQL）"""
        if "mysql" in settings.DATABASE_URL:
            try:
                db.execute(f"ANALYZE TABLE {table_name}")
                db.commit()
                logger.info(f"表 {table_name} 分析完成")
                return True
            except Exception as e:
                logger.error(f"分析表失败: {str(e)}")
                return False
        return False
    
    @staticmethod
    def optimize_table(db: Session, table_name: str):
        """优化表（MySQL）"""
        if "mysql" in settings.DATABASE_URL:
            try:
                db.execute(f"OPTIMIZE TABLE {table_name}")
                db.commit()
                logger.info(f"表 {table_name} 优化完成")
                return True
            except Exception as e:
                logger.error(f"优化表失败: {str(e)}")
                return False
        return False


# 创建数据库管理器实例
db_manager = DatabaseManager()