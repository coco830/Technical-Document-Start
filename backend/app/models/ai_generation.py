from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Index, JSON
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from .base import BaseModel


class AIGenerationStatus(PyEnum):
    """AI生成状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AIGeneration(BaseModel):
    """AI生成记录模型"""
    __tablename__ = "ai_generations"
    
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True, comment="文档ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    prompt = Column(Text, nullable=False, comment="生成提示词")
    generation_config = Column(JSON, nullable=True, comment="生成配置")
    generated_content = Column(Text, nullable=True, comment="生成内容")
    status = Column(Enum(AIGenerationStatus), default=AIGenerationStatus.PENDING, nullable=False, comment="生成状态")
    metadata = Column(JSON, nullable=True, comment="元数据")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关系
    document = relationship("Document", back_populates="ai_generations")
    user = relationship("User", back_populates="ai_generations")
    
    # 索引
    __table_args__ = (
        Index('idx_ai_generations_document_id', 'document_id'),
        Index('idx_ai_generations_user_id', 'user_id'),
        Index('idx_ai_generations_status', 'status'),
        Index('idx_ai_generations_created_at', 'created_at'),
        Index('idx_ai_generations_document_status', 'document_id', 'status'),
        Index('idx_ai_generations_user_created', 'user_id', 'created_at'),
    )