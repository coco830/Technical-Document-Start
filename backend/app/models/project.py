from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    # user = relationship("User", back_populates="projects")

    def __repr__(self):
        return f"<Project {self.title}>"
