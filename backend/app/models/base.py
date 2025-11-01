from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr

# 创建Base类
Base = DeclarativeBase()


class TimestampMixin:
    """时间戳混入类"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")


class BaseModel(TimestampMixin):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")