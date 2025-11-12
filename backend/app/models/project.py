from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Project(Base):
    """项目数据模型"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active", index=True)  # active, completed, archived
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    enterprise_info = relationship("EnterpriseInfo", back_populates="project", cascade="all, delete-orphan")

    # 复合索引定义
    __table_args__ = (
        Index('idx_user_status', 'user_id', 'status'),  # 用于用户项目状态过滤
        Index('idx_user_created', 'user_id', 'created_at'),  # 用于用户项目按创建时间排序
    )

    def __repr__(self):
        return f"<Project {self.title}>"
