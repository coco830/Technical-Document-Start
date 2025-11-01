from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from .base import BaseModel


class DocumentFormat(PyEnum):
    """文档格式枚举"""
    MARKDOWN = "markdown"
    HTML = "html"
    PLAIN_TEXT = "plain_text"


class DocumentStatus(PyEnum):
    """文档状态枚举"""
    DRAFT = "draft"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    PUBLISHED = "published"


class Document(BaseModel):
    """文档模型"""
    __tablename__ = "documents"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="所属项目ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    content = Column(Text, nullable=True, comment="文档内容")
    format = Column(Enum(DocumentFormat), default=DocumentFormat.MARKDOWN, nullable=False, comment="文档格式")
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False, comment="文档状态")
    metadata = Column(JSON, nullable=True, comment="文档元数据")
    
    # 关系
    project = relationship("Project", back_populates="documents")
    document_versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    ai_generations = relationship("AIGeneration", back_populates="document", cascade="all, delete-orphan")
    document_exports = relationship("DocumentExport", back_populates="document", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_documents_project_id', 'project_id'),
        Index('idx_documents_status', 'status'),
        Index('idx_documents_created_at', 'created_at'),
        Index('idx_documents_project_status', 'project_id', 'status'),
    )


class DocumentVersion(BaseModel):
    """文档版本模型"""
    __tablename__ = "document_versions"
    
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True, comment="文档ID")
    version_number = Column(Integer, nullable=False, comment="版本号")
    content = Column(Text, nullable=False, comment="版本内容")
    changes_summary = Column(JSON, nullable=True, comment="变更摘要")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建者ID")
    
    # 关系
    document = relationship("Document", back_populates="document_versions")
    created_by_user = relationship("User", back_populates="document_versions")
    
    # 索引
    __table_args__ = (
        Index('idx_document_versions_document_id', 'document_id'),
        Index('idx_document_versions_version_number', 'document_id', 'version_number'),
    )