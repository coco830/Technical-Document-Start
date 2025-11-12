from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Comment(Base):
    """文档评论数据模型"""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)  # 评论内容
    selection_text = Column(Text, nullable=True)  # 批注的选中文本
    position_start = Column(Integer, nullable=True)  # 批注位置开始（字符索引）
    position_end = Column(Integer, nullable=True)  # 批注位置结束（字符索引）
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)  # 回复的父评论ID
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联关系
    document = relationship("Document", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], back_populates="replies")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")

    # 复合索引定义
    __table_args__ = (
        Index('idx_document_parent', 'document_id', 'parent_id'),  # 用于获取评论和回复
        Index('idx_document_created', 'document_id', 'created_at'),  # 用于文档评论按时间排序
        Index('idx_parent_created', 'parent_id', 'created_at'),  # 用于回复按时间排序
    )

    def __repr__(self):
        return f"<Comment {self.id} on Document {self.document_id}>"
