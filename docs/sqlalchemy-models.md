# SQLAlchemy ORM模型定义

本文档提供了悦恩人机共写平台的完整SQLAlchemy ORM模型定义代码。

## 1. 基础模型 (backend/app/models/base.py)

```python
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

Base = declarative_base()


class TimestampMixin:
    """时间戳混入类"""
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")


class BaseModel(Base, TimestampMixin):
    """基础模型类"""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
```

## 2. 用户模型 (backend/app/models/user.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from .base import BaseModel


class UserRole(PyEnum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱地址")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    full_name = Column(String(100), nullable=True, comment="用户全名")
    phone = Column(String(20), nullable=True, comment="手机号码")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, comment="用户角色")
    is_active = Column(Boolean, default=True, nullable=False, comment="账户是否激活")
    is_verified = Column(Boolean, default=False, nullable=False, comment="邮箱是否验证")
    last_login_at = Column(DateTime, nullable=True, comment="最后登录时间")
    
    # 关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    ai_generations = relationship("AIGeneration", back_populates="user", cascade="all, delete-orphan")
    document_versions = relationship("DocumentVersion", back_populates="created_by_user", cascade="all, delete-orphan")
    document_exports = relationship("DocumentExport", back_populates="user", cascade="all, delete-orphan")


class UserSession(BaseModel):
    """用户会话模型"""
    __tablename__ = "user_sessions"
    
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    token_hash = Column(String(255), nullable=False, index=True, comment="令牌哈希值")
    device_info = Column(Text, nullable=True, comment="设备信息")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    expires_at = Column(DateTime, nullable=False, index=True, comment="过期时间")
    
    # 关系
    user = relationship("User", back_populates="user_sessions")
```

## 3. 企业模型 (backend/app/models/company.py)

```python
from sqlalchemy import Column, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from .base import BaseModel


class Company(BaseModel):
    """企业模型"""
    __tablename__ = "companies"
    
    name = Column(String(200), nullable=False, index=True, comment="企业名称")
    unified_social_credit_code = Column(String(18), unique=True, nullable=True, index=True, comment="统一社会信用代码")
    legal_representative = Column(String(100), nullable=True, comment="法定代表人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    contact_email = Column(String(100), nullable=True, comment="联系邮箱")
    address = Column(Text, nullable=True, comment="企业地址")
    industry = Column(String(100), nullable=True, comment="所属行业")
    business_scope = Column(Text, nullable=True, comment="经营范围")
    
    # 关系
    projects = relationship("Project", back_populates="company")
    
    # 索引
    __table_args__ = (
        Index('idx_companies_name', 'name'),
        Index('idx_companies_unified_social_credit_code', 'unified_social_credit_code'),
    )
```

## 4. 项目模型 (backend/app/models/project.py)

```python
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
    metadata = Column(JSON, nullable=True, comment="项目元数据")
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
```

## 5. 文档模型 (backend/app/models/document.py)

```python
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, Index, JSON, LongText
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
    content = Column(LongText, nullable=True, comment="文档内容")
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
    content = Column(LongText, nullable=False, comment="版本内容")
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
```

## 6. AI生成模型 (backend/app/models/ai_generation.py)

```python
from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime, Index, JSON, LongText
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
    generated_content = Column(LongText, nullable=True, comment="生成内容")
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
```

## 7. 文档导出模型 (backend/app/models/document_export.py)

```python
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
```

## 8. 模型初始化文件 (backend/app/models/__init__.py)

```python
from .base import Base, BaseModel, TimestampMixin
from .user import User, UserSession, UserRole
from .company import Company
from .project import Project, ProjectForm, FormField, ProjectType, ProjectStatus
from .document import Document, DocumentVersion, DocumentFormat, DocumentStatus
from .ai_generation import AIGeneration, AIGenerationStatus
from .document_export import DocumentExport, ExportFormat

__all__ = [
    # 基础类
    "Base",
    "BaseModel", 
    "TimestampMixin",
    
    # 用户相关
    "User",
    "UserSession",
    "UserRole",
    
    # 企业相关
    "Company",
    
    # 项目相关
    "Project",
    "ProjectForm",
    "FormField",
    "ProjectType",
    "ProjectStatus",
    
    # 文档相关
    "Document",
    "DocumentVersion",
    "DocumentFormat",
    "DocumentStatus",
    
    # AI生成相关
    "AIGeneration",
    "AIGenerationStatus",
    
    # 文档导出相关
    "DocumentExport",
    "ExportFormat",
]
```

## 9. 数据库连接配置 (backend/app/core/database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.models import Base

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=True  # 开发环境开启SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 10. 使用示例

```python
from sqlalchemy.orm import Session
from app.models import User, Project, Document
from app.core.database import get_db

# 创建用户
def create_user(db: Session, username: str, email: str, password_hash: str):
    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 查询用户项目
def get_user_projects(db: Session, user_id: int):
    return db.query(Project).filter(Project.user_id == user_id).all()

# 创建文档
def create_document(db: Session, project_id: int, title: str, content: str):
    document = Document(
        project_id=project_id,
        title=title,
        content=content
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
```

这些SQLAlchemy模型定义提供了完整的数据库映射，包括所有必要的表、关系、索引和约束。模型遵循了最佳实践，使用了混入类来减少重复代码，并提供了清晰的类型定义和文档注释。