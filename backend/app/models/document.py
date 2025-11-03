from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
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
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    version = Column(Integer, default=1, nullable=False)  # 版本控制
    is_template = Column(Integer, default=0, nullable=False)  # 0: 普通文档, 1: 模板
    doc_metadata = Column(JSON, nullable=True)  # 额外元数据（字数统计、标签等）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系（根据需要取消注释）
    # project = relationship("Project", back_populates="documents")
    # user = relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.title}>"
