from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from .base import BaseModel


class ExportFormat(PyEnum):
    """导出格式枚举"""
    PDF = "pdf"
    WORD = "word"
    HTML = "html"
    MARKDOWN = "markdown"


class DocumentExport(BaseModel):
    """文档导出模型"""
    __tablename__ = "document_exports"
    
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True, comment="文档ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
    format = Column(Enum(ExportFormat), nullable=False, comment="导出格式")
    file_url = Column(String(500), nullable=True, comment="文件URL")
    file_name = Column(String(255), nullable=True, comment="文件名")
    file_size = Column(Integer, nullable=True, comment="文件大小(字节)")
    
    # 关系
    document = relationship("Document", back_populates="document_exports")
    user = relationship("User", back_populates="document_exports")