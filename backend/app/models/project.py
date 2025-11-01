from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Index, JSON
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from .base import BaseModel


class ProjectType(PyEnum):
    """项目类型枚举"""
    EMERGENCY_PLAN = "emergency_plan"
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"


class ProjectStatus(PyEnum):
    """项目状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(BaseModel):
    """项目模型"""
    __tablename__ = "projects"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="所属用户ID")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True, comment="关联企业ID")
    name = Column(String(200), nullable=False, comment="项目名称")
    type = Column(Enum(ProjectType), nullable=False, comment="项目类型")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False, comment="项目状态")
    description = Column(Text, nullable=True, comment="项目描述")
    project_metadata = Column(JSON, nullable=True, comment="项目元数据")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    
    # 关系
    user = relationship("User", back_populates="projects")
    company = relationship("Company", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")
    project_forms = relationship("ProjectForm", back_populates="project", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index('idx_projects_user_id', 'user_id'),
        Index('idx_projects_company_id', 'company_id'),
        Index('idx_projects_type', 'type'),
        Index('idx_projects_status', 'status'),
        Index('idx_projects_created_at', 'created_at'),
        Index('idx_projects_user_status', 'user_id', 'status'),
        Index('idx_projects_type_status', 'type', 'status'),
    )


class ProjectForm(BaseModel):
    """项目表单模型"""
    __tablename__ = "project_forms"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True, comment="所属项目ID")
    form_type = Column(String(50), nullable=False, comment="表单类型")
    form_data = Column(JSON, nullable=False, comment="表单数据")
    
    # 关系
    project = relationship("Project", back_populates="project_forms")
    form_fields = relationship("FormField", back_populates="form", cascade="all, delete-orphan")


class FormField(BaseModel):
    """表单字段模型"""
    __tablename__ = "form_fields"
    
    form_id = Column(Integer, ForeignKey("project_forms.id"), nullable=False, index=True, comment="所属表单ID")
    field_name = Column(String(100), nullable=False, comment="字段名称")
    field_type = Column(String(50), nullable=False, comment="字段类型")
    field_label = Column(String(200), nullable=False, comment="字段标签")
    field_config = Column(JSON, nullable=True, comment="字段配置")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序顺序")
    is_required = Column(Integer, default=False, nullable=False, comment="是否必填")
    
    # 关系
    form = relationship("ProjectForm", back_populates="form_fields")