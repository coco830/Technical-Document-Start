from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 从环境变量读取数据库URL，默认使用SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./yueen.db")

# 创建数据库引擎
# SQLite需要check_same_thread=False以支持多线程
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类，所有模型都继承自此
Base = declarative_base()

# 数据库依赖项，用于FastAPI路由
def get_db():
    """
    数据库会话依赖项
    使用方法：
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 初始化数据库（创建所有表）
def init_db():
    """
    初始化数据库，创建所有表
    在main.py启动时调用
    """
    Base.metadata.create_all(bind=engine)
