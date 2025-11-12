from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Document(Base):
    """文档数据模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=True)  # HTML 或 JSON 格式的富文本内容
    content_type = Column(String(20), default="html", nullable=False)  # html, json, markdown
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)  # 版本控制
    is_template = Column(Integer, default=0, nullable=False, index=True)  # 0: 普通文档, 1: 模板
    doc_metadata = Column(JSON, nullable=True)  # 额外元数据（字数统计、标签等）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    project = relationship("Project", back_populates="documents")
    user = relationship("User", back_populates="documents")
    comments = relationship("Comment", back_populates="document", cascade="all, delete-orphan")

    # 复合索引定义
    __table_args__ = (
        Index('idx_user_template', 'user_id', 'is_template'),  # 用于用户模板过滤
        Index('idx_user_project', 'user_id', 'project_id'),  # 用于用户项目文档查询
        Index('idx_project_updated', 'project_id', 'updated_at'),  # 用于项目文档按更新时间排序
        Index('idx_user_updated', 'user_id', 'updated_at'),  # 用于用户文档按更新时间排序
    )

    def __repr__(self):
        return f"<Document {self.title}>"
