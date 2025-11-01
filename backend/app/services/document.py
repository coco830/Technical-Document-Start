"""
文档服务层实现
"""
import logging
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.document import Document, DocumentVersion, DocumentFormat, DocumentStatus
from app.models.document_export import DocumentExport, ExportFormat
from app.models.project import Project
from app.models.user import User
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentWithDetails,
    DocumentVersionCreate, DocumentVersionWithDetails,
    DocumentList, DocumentVersionList
)
from app.schemas.document_export import (
    DocumentExportCreate, DocumentExportWithDetails, DocumentExportList,
    DocumentExportRequest, DocumentExportResponse, ExportStatus,
    ExportTemplate, ExportStatistics
)
from app.services.base import CRUDBase
from app.core.exceptions import PermissionException, NotFoundException
from app.services.document_export import document_export_service

# 设置日志
logger = logging.getLogger(__name__)


def has_permission(user: User, permission: str) -> bool:
    """检查用户是否有特定权限"""
    if not user or not user.is_active:
        return False
    
    # 管理员拥有所有权限
    if user.role == "admin":
        return True
    
    # 普通用户权限
    permission_map = {
        "user": ["read_own", "write_own", "document:read", "document:write", "document:create", "document:delete"],
        "admin": ["read_own", "write_own", "read_team", "write_team", "read_all", "write_all", "admin", 
                 "document:read", "document:write", "document:create", "document:delete", "system:admin"],
    }
    
    user_permissions = permission_map.get(user.role, [])
    return permission in user_permissions


def convert_document_format(content: str, from_format: DocumentFormat, to_format: DocumentFormat) -> str:
    """转换文档格式"""
    if from_format == to_format:
        return content
    
    # 简单的格式转换实现
    if from_format == DocumentFormat.MARKDOWN and to_format == DocumentFormat.HTML:
        # 简单的 Markdown 到 HTML 转换
        content = re.sub(r'### (.*)', r'<h3>\1</h3>', content)
        content = re.sub(r'## (.*)', r'<h2>\1</h2>', content)
        content = re.sub(r'# (.*)', r'<h1>\1</h1>', content)
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        content = re.sub(r'`([^`]*)`', r'<code>\1</code>', content)
        content = re.sub(r'\n\n', '</p><p>', content)
        content = '<p>' + content + '</p>'
        content = re.sub(r'<p></p>', '', content)
        return content
    
    elif from_format == DocumentFormat.HTML and to_format == DocumentFormat.MARKDOWN:
        # 简单的 HTML 到 Markdown 转换
        content = re.sub(r'<h1>(.*?)</h1>', r'# \1', content)
        content = re.sub(r'<h2>(.*?)</h2>', r'## \2', content)
        content = re.sub(r'<h3>(.*?)</h3>', r'### \3', content)
        content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
        content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
        content = re.sub(r'<code>(.*?)</code>', r'`\1`', content)
        content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content)
        content = re.sub(r'\n\n+', '\n\n', content)
        return content.strip()
    
    elif to_format == DocumentFormat.PLAIN_TEXT:
        # 转换为纯文本
        if from_format == DocumentFormat.HTML:
            content = re.sub(r'<[^>]+>', '', content)
        elif from_format == DocumentFormat.MARKDOWN:
            content = re.sub(r'[#*`]', '', content)
        return content
    
    # 默认返回原内容
    return content


class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    def get_by_project_id(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """获取项目的文档列表"""
        return (
            db.query(self.model)
            .filter(Document.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, db: Session, *, status: DocumentStatus, skip: int = 0, limit: int = 100) -> List[Document]:
        """根据状态获取文档列表"""
        return (
            db.query(self.model)
            .filter(Document.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_format(self, db: Session, *, format: DocumentFormat, skip: int = 0, limit: int = 100) -> List[Document]:
        """根据格式获取文档列表"""
        return (
            db.query(self.model)
            .filter(Document.format == format)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_documents(
        self, db: Session, *, query: str, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """搜索文档"""
        filters = [
            or_(
                Document.title.ilike(f"%{query}%"),
                Document.content.ilike(f"%{query}%"),
            )
        ]
        
        if user_id:
            filters.append(Document.project.has(Project.user_id == user_id))
        
        return (
            db.query(self.model)
            .join(Project)
            .filter(and_(*filters))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db: Session, *, document_id: int) -> Optional[DocumentWithDetails]:
        """获取包含详细信息的文档"""
        document = db.query(self.model).filter(Document.id == document_id).first()
        if not document:
            return None
        
        # 获取关联信息
        project_name = document.project.name if document.project else None
        versions_count = len(document.document_versions) if document.document_versions else 0
        ai_generations_count = len(document.ai_generations) if document.ai_generations else 0
        exports_count = len(document.document_exports) if document.document_exports else 0
        
        return DocumentWithDetails(
            id=int(document.id),
            project_id=int(document.project_id),
            title=str(document.title),
            content=str(document.content) if document.content else None,
            format=DocumentFormat(document.format.value),
            status=DocumentStatus(document.status.value),
            metadata=dict(document.metadata) if document.metadata else None,
            created_at=document.created_at,
            updated_at=document.updated_at,
            project_name=project_name,
            versions_count=versions_count,
            ai_generations_count=ai_generations_count,
            exports_count=exports_count
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        project_id: Optional[int] = None,
        status: Optional[DocumentStatus] = None,
        format: Optional[DocumentFormat] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[DocumentWithDetails]:
        """获取包含详细信息的多个文档"""
        query = db.query(self.model).join(Project)
        
        # 应用筛选条件
        if project_id:
            query = query.filter(Document.project_id == project_id)
        if status:
            query = query.filter(Document.status == status)
        if format:
            query = query.filter(Document.format == format)
        
        # 应用排序
        if order_by and hasattr(Document, order_by):
            order_column = getattr(Document, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        
        documents = query.offset(skip).limit(limit).all()
        
        result = []
        for document in documents:
            project_name = document.project.name if document.project else None
            versions_count = len(document.document_versions) if document.document_versions else 0
            ai_generations_count = len(document.ai_generations) if document.ai_generations else 0
            exports_count = len(document.document_exports) if document.document_exports else 0
            
            result.append(DocumentWithDetails(
                id=int(document.id),
                project_id=int(document.project_id),
                title=str(document.title),
                content=str(document.content) if document.content else None,
                format=DocumentFormat(document.format.value),
                status=DocumentStatus(document.status.value),
                metadata=dict(document.metadata) if document.metadata else None,
                created_at=document.created_at,
                updated_at=document.updated_at,
                project_name=project_name,
                versions_count=versions_count,
                ai_generations_count=ai_generations_count,
                exports_count=exports_count
            ))
        
        return result

    def create_with_user(self, db: Session, *, obj_in: DocumentCreate, current_user: User) -> Document:
        """创建文档"""
        # 检查权限
        if not has_permission(current_user, "document:create"):
            raise PermissionException("没有创建文档的权限")
        
        # 检查项目权限
        project = db.query(Project).filter(Project.id == obj_in.project_id).first()
        if not project:
            raise NotFoundException(f"项目 {obj_in.project_id} 不存在")
        
        if project.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限为此项目创建文档")
        
        db_obj = Document(
            project_id=obj_in.project_id,
            title=obj_in.title,
            content=obj_in.content,
            format=obj_in.format,
            status=obj_in.status,
            metadata=obj_in.metadata,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 创建初始版本
        if db_obj.content:
            self._create_version(db, document=db_obj, content=db_obj.content, user=current_user)
        
        logger.info(f"用户 {current_user.id} 创建了文档 {db_obj.id}")
        return db_obj

    def update_with_user(
        self, 
        db: Session, 
        *, 
        db_obj: Document, 
        obj_in: Union[DocumentUpdate, Dict[str, Any]],
        current_user: User
    ) -> Document:
        """更新文档"""
        # 检查权限
        if not self._can_modify_document(db_obj, current_user):
            raise PermissionException("没有修改此文档的权限")
        
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        # 如果内容发生变化，创建新版本
        if "content" in update_data and update_data["content"] != db_obj.content:
            self._create_version(db, document=db_obj, content=update_data["content"], user=current_user)
        
        # 格式转换
        if "format" in update_data and update_data["format"] != db_obj.format and db_obj.content:
            update_data["content"] = convert_document_format(
                db_obj.content, db_obj.format, update_data["format"]
            )
        
        result = super().update(db, db_obj=db_obj, obj_in=update_data)
        
        logger.info(f"用户 {current_user.id} 更新了文档 {db_obj.id}")
        return result

    def delete_with_user(self, db: Session, *, document_id: int, current_user: User) -> Document:
        """删除文档"""
        document = self.get(db, id=document_id)
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        # 检查权限
        if not self._can_modify_document(document, current_user):
            raise PermissionException("没有删除此文档的权限")
        
        db.delete(document)
        db.commit()
        
        logger.info(f"用户 {current_user.id} 删除了文档 {document_id}")
        return document

    def update_status(
        self, 
        db: Session, 
        *, 
        document_id: int, 
        status: DocumentStatus, 
        current_user: User
    ) -> Document:
        """更新文档状态"""
        document = self.get(db, id=document_id)
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        # 检查权限
        if not self._can_modify_document(document, current_user):
            raise PermissionException("没有修改此文档状态的权限")
        
        old_status = document.status
        document.status = status
        db.commit()
        db.refresh(document)
        
        logger.info(f"用户 {current_user.id} 将文档 {document_id} 状态从 {old_status} 更新为 {status}")
        return document

    def _can_modify_document(self, document: Document, user: User) -> bool:
        """检查用户是否可以修改文档"""
        # 管理员可以修改所有文档
        if has_permission(user, "system:admin"):
            return True
        
        # 项目所有者可以修改项目的文档
        if document.project and document.project.user_id == user.id:
            return True
        
        return False

    def _create_version(self, db: Session, *, document: Document, content: str, user: User) -> DocumentVersion:
        """创建文档版本"""
        # 获取最新版本号
        latest_version = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == document.id
        ).order_by(desc(DocumentVersion.version_number)).first()
        
        version_number = 1
        if latest_version:
            version_number = latest_version.version_number + 1
        
        # 计算变更摘要
        changes_summary = None
        if document.content:
            changes_summary = {
                "type": "content_update",
                "old_length": len(document.content),
                "new_length": len(content),
                "diff": len(content) - len(document.content)
            }
        
        version = DocumentVersion(
            document_id=document.id,
            version_number=version_number,
            content=content,
            changes_summary=changes_summary,
            created_by=user.id
        )
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return version


class CRUDDocumentVersion(CRUDBase[DocumentVersion, DocumentVersionCreate, DocumentVersionCreate]):
    def get_by_document_id(self, db: Session, *, document_id: int, skip: int = 0, limit: int = 100) -> List[DocumentVersion]:
        """获取文档的版本列表"""
        return (
            db.query(self.model)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.version_number))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_latest_version(self, db: Session, *, document_id: int) -> Optional[DocumentVersion]:
        """获取文档的最新版本"""
        return (
            db.query(self.model)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.version_number))
            .first()
        )

    def get_with_details(self, db: Session, *, version_id: int) -> Optional[DocumentVersionWithDetails]:
        """获取包含详细信息的文档版本"""
        version = db.query(self.model).filter(DocumentVersion.id == version_id).first()
        if not version:
            return None
        
        # 获取关联信息
        document_title = version.document.title if version.document else None
        created_by_name = version.created_by_user.full_name if version.created_by_user else None
        
        return DocumentVersionWithDetails(
            id=int(version.id),
            document_id=int(version.document_id),
            version_number=int(version.version_number),
            content=str(version.content),
            changes_summary=dict(version.changes_summary) if version.changes_summary else None,
            created_by=int(version.created_by),
            created_at=version.created_at,
            document_title=document_title,
            created_by_name=created_by_name
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        document_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[DocumentVersionWithDetails]:
        """获取包含详细信息的多个文档版本"""
        versions = (
            db.query(self.model)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(desc(DocumentVersion.version_number))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for version in versions:
            document_title = version.document.title if version.document else None
            created_by_name = version.created_by_user.full_name if version.created_by_user else None
            
            result.append(DocumentVersionWithDetails(
                id=int(version.id),
                document_id=int(version.document_id),
                version_number=int(version.version_number),
                content=str(version.content),
                changes_summary=dict(version.changes_summary) if version.changes_summary else None,
                created_by=int(version.created_by),
                created_at=version.created_at,
                document_title=document_title,
                created_by_name=created_by_name
            ))
        
        return result

    def restore_version(self, db: Session, *, version_id: int, current_user: User) -> Document:
        """恢复文档到特定版本"""
        version = self.get(db, id=version_id)
        if not version:
            raise NotFoundException(f"文档版本 {version_id} 不存在")
        
        document = db.query(Document).filter(Document.id == version.document_id).first()
        if not document:
            raise NotFoundException(f"文档 {version.document_id} 不存在")
        
        # 检查权限
        if not crud_document._can_modify_document(document, current_user):
            raise PermissionException("没有权限恢复此文档")
        
        # 创建当前内容的版本备份
        if document.content:
            crud_document._create_version(db, document=document, content=document.content, user=current_user)
        
        # 恢复内容
        document.content = version.content
        db.commit()
        db.refresh(document)
        
        logger.info(f"用户 {current_user.id} 将文档 {document.id} 恢复到版本 {version.version_number}")
        return document


class CRUDDocumentExport(CRUDBase[DocumentExport, DocumentExportCreate, DocumentExportCreate]):
    def get_by_document_id(self, db: Session, *, document_id: int, skip: int = 0, limit: int = 100) -> List[DocumentExport]:
        """获取文档的导出记录列表"""
        return (
            db.query(self.model)
            .filter(DocumentExport.document_id == document_id)
            .order_by(desc(DocumentExport.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[DocumentExport]:
        """获取用户的导出记录列表"""
        return (
            db.query(self.model)
            .filter(DocumentExport.user_id == user_id)
            .order_by(desc(DocumentExport.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db: Session, *, export_id: int) -> Optional[DocumentExportWithDetails]:
        """获取包含详细信息的文档导出记录"""
        export = db.query(self.model).filter(DocumentExport.id == export_id).first()
        if not export:
            return None
        
        # 获取关联信息
        document_title = export.document.title if export.document else None
        user_name = export.user.full_name if export.user else None
        
        return DocumentExportWithDetails(
            id=int(export.id),
            document_id=int(export.document_id),
            user_id=int(export.user_id),
            format=ExportFormat(export.format.value),
            file_url=export.file_url,
            file_name=export.file_name,
            file_size=export.file_size,
            created_at=export.created_at,
            document_title=document_title,
            user_name=user_name,
            status=ExportStatus.COMPLETED if export.file_url else ExportStatus.PENDING,
            download_url=export.file_url
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[DocumentExportWithDetails]:
        """获取包含详细信息的多个文档导出记录"""
        query = db.query(self.model)
        
        # 应用筛选条件
        if document_id:
            query = query.filter(DocumentExport.document_id == document_id)
        if user_id:
            query = query.filter(DocumentExport.user_id == user_id)
        
        exports = query.order_by(desc(DocumentExport.created_at)).offset(skip).limit(limit).all()
        
        result = []
        for export in exports:
            document_title = export.document.title if export.document else None
            user_name = export.user.full_name if export.user else None
            
            result.append(DocumentExportWithDetails(
                id=int(export.id),
                document_id=int(export.document_id),
                user_id=int(export.user_id),
                format=ExportFormat(export.format.value),
                file_url=export.file_url,
                file_name=export.file_name,
                file_size=export.file_size,
                created_at=export.created_at,
                document_title=document_title,
                user_name=user_name,
                status=ExportStatus.COMPLETED if export.file_url else ExportStatus.PENDING,
                download_url=export.file_url
            ))
        
        return result

    def create_export_request(
        self, 
        db: Session, 
        *, 
        document_id: int, 
        export_request: DocumentExportRequest, 
        current_user: User
    ) -> DocumentExportResponse:
        """创建文档导出请求"""
        # 检查文档权限
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        if not crud_document._can_modify_document(document, current_user):
            raise PermissionException("没有权限导出此文档")
        
        # 创建导出记录
        db_obj = DocumentExport(
            document_id=document_id,
            user_id=current_user.id,
            format=export_request.format
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 这里应该启动异步任务来处理导出
        # 为了简化，我们直接模拟导出完成
        file_name = f"{document.title}.{export_request.format.value}"
        file_url = f"/exports/{file_name}"
        file_size = len(document.content) if document.content else 0
        
        db_obj.file_name = file_name
        db_obj.file_url = file_url
        db_obj.file_size = file_size
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"用户 {current_user.id} 导出了文档 {document_id} 为 {export_request.format.value} 格式")
        
        return DocumentExportResponse(
            export_id=db_obj.id,
            status=ExportStatus.COMPLETED,
            message="导出完成",
            download_url=file_url,
            file_name=file_name,
            file_size=file_size
        )


class DocumentService:
    """文档服务类，继承自BaseService"""
    
    def __init__(self):
        self.crud_document = CRUDDocument(Document)
        self.crud_document_version = CRUDDocumentVersion(DocumentVersion)
        self.crud_document_export = CRUDDocumentExport(DocumentExport)
    
    # 文档CRUD操作
    def create_document(self, db: Session, *, document_in: DocumentCreate, current_user: User) -> Document:
        """创建文档"""
        return self.crud_document.create_with_user(db=db, obj_in=document_in, current_user=current_user)
    
    def get_document(self, db: Session, *, document_id: int, current_user: User) -> Optional[DocumentWithDetails]:
        """获取单个文档"""
        document = self.crud_document.get(db, id=document_id)
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        # 检查权限
        if not self.crud_document._can_modify_document(document, current_user) and \
           not has_permission(current_user, "document:read"):
            raise PermissionException("没有权限查看此文档")
        
        return self.crud_document.get_with_details(db, document_id=document_id)
    
    def get_documents(
        self, 
        db: Session, 
        *, 
        project_id: Optional[int] = None,
        status: Optional[DocumentStatus] = None,
        format: Optional[DocumentFormat] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True,
        current_user: User = None
    ) -> List[DocumentWithDetails]:
        """获取文档列表（支持分页、筛选、排序）"""
        # 如果指定了project_id，检查项目权限
        if project_id and current_user:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise NotFoundException(f"项目 {project_id} 不存在")
            
            if project.user_id != current_user.id and not has_permission(current_user, "system:admin"):
                raise PermissionException("没有权限查看此项目的文档")
        
        return self.crud_document.get_multi_with_details(
            db=db,
            project_id=project_id,
            status=status,
            format=format,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def update_document(
        self, 
        db: Session, 
        *, 
        document_id: int, 
        document_in: DocumentUpdate, 
        current_user: User
    ) -> Document:
        """更新文档"""
        document = self.crud_document.get(db, id=document_id)
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        return self.crud_document.update_with_user(db, db_obj=document, obj_in=document_in, current_user=current_user)
    
    def delete_document(self, db: Session, *, document_id: int, current_user: User) -> Document:
        """删除文档"""
        return self.crud_document.delete_with_user(db, document_id=document_id, current_user=current_user)
    
    # 文档版本管理
    def create_document_version(
        self, 
        db: Session, 
        *, 
        document_id: int, 
        content: str, 
        current_user: User
    ) -> DocumentVersion:
        """创建文档版本"""
        document = self.crud_document.get(db, id=document_id)
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        if not self.crud_document._can_modify_document(document, current_user):
            raise PermissionException("没有权限为此文档创建版本")
        
        return self.crud_document._create_version(db, document=document, content=content, user=current_user)
    
    def get_document_versions(
        self, 
        db: Session, 
        *, 
        document_id: int, 
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[DocumentVersionWithDetails]:
        """获取文档版本列表"""
        # 检查文档权限
        document = self.crud_document.get(db, id=document_id)
        if not document:
            raise NotFoundException(f"文档 {document_id} 不存在")
        
        if not self.crud_document._can_modify_document(document, current_user) and \
           not has_permission(current_user, "document:read"):
            raise PermissionException("没有权限查看此文档的版本")
        
        return self.crud_document_version.get_multi_with_details(
            db=db, document_id=document_id, skip=skip, limit=limit
        )
    
    def get_document_version(
        self, 
        db: Session, 
        *, 
        version_id: int, 
        current_user: User = None
    ) -> Optional[DocumentVersionWithDetails]:
        """获取特定版本的文档"""
        version = self.crud_document_version.get(db, id=version_id)
        if not version:
            raise NotFoundException(f"文档版本 {version_id} 不存在")
        
        # 检查文档权限
        document = self.crud_document.get(db, id=version.document_id)
        if not document:
            raise NotFoundException(f"文档 {version.document_id} 不存在")
        
        if not self.crud_document._can_modify_document(document, current_user) and \
           not has_permission(current_user, "document:read"):
            raise PermissionException("没有权限查看此文档的版本")
        
        return self.crud_document_version.get_with_details(db, version_id=version_id)
    
    def restore_document_version(
        self, 
        db: Session, 
        *, 
        version_id: int, 
        current_user: User
    ) -> Document:
        """恢复文档到特定版本"""
        return self.crud_document_version.restore_version(db, version_id=version_id, current_user=current_user)
    
    # 文档状态管理
    def update_document_status(
        self, 
        db: Session, 
        *, 
        document_id: int, 
        status: DocumentStatus, 
        current_user: User
    ) -> Document:
        """更新文档状态"""
        return self.crud_document.update_status(db, document_id=document_id, status=status, current_user=current_user)
    
    def get_documents_by_status(
        self, 
        db: Session, 
        *, 
        status: DocumentStatus, 
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[DocumentWithDetails]:
        """按状态获取文档"""
        # 如果不是管理员，只返回用户有权限的文档
        if current_user and not has_permission(current_user, "system:admin"):
            # 获取用户的项目ID列表
            user_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
            project_ids = [p.id for p in user_projects]
            
            # 获取这些项目的文档
            documents = (
                db.query(Document)
                .filter(and_(Document.status == status, Document.project_id.in_(project_ids)))
                .offset(skip)
                .limit(limit)
                .all()
            )
        else:
            documents = self.crud_document.get_by_status(db, status=status, skip=skip, limit=limit)
        
        result = []
        for document in documents:
            project_name = document.project.name if document.project else None
            versions_count = len(document.document_versions) if document.document_versions else 0
            ai_generations_count = len(document.ai_generations) if document.ai_generations else 0
            exports_count = len(document.document_exports) if document.document_exports else 0
            
            result.append(DocumentWithDetails(
                id=int(document.id),
                project_id=int(document.project_id),
                title=str(document.title),
                content=str(document.content) if document.content else None,
                format=DocumentFormat(document.format.value),
                status=DocumentStatus(document.status.value),
                metadata=dict(document.metadata) if document.metadata else None,
                created_at=document.created_at,
                updated_at=document.updated_at,
                project_name=project_name,
                versions_count=versions_count,
                ai_generations_count=ai_generations_count,
                exports_count=exports_count
            ))
        
        return result
    
    # 文档搜索和筛选
    def search_documents(
        self, 
        db: Session, 
        *, 
        query: str, 
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[DocumentWithDetails]:
        """搜索文档"""
        user_id = None
        if current_user and not has_permission(current_user, "system:admin"):
            user_id = current_user.id
        
        documents = self.crud_document.search_documents(db, query=query, user_id=user_id, skip=skip, limit=limit)
        
        result = []
        for document in documents:
            project_name = document.project.name if document.project else None
            versions_count = len(document.document_versions) if document.document_versions else 0
            ai_generations_count = len(document.ai_generations) if document.ai_generations else 0
            exports_count = len(document.document_exports) if document.document_exports else 0
            
            result.append(DocumentWithDetails(
                id=int(document.id),
                project_id=int(document.project_id),
                title=str(document.title),
                content=str(document.content) if document.content else None,
                format=DocumentFormat(document.format.value),
                status=DocumentStatus(document.status.value),
                metadata=dict(document.metadata) if document.metadata else None,
                created_at=document.created_at,
                updated_at=document.updated_at,
                project_name=project_name,
                versions_count=versions_count,
                ai_generations_count=ai_generations_count,
                exports_count=exports_count
            ))
        
        return result
    
    def get_documents_by_project(
        self, 
        db: Session, 
        *, 
        project_id: int, 
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[DocumentWithDetails]:
        """获取项目相关文档"""
        # 检查项目权限
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")
        
        if not has_permission(current_user, "system:admin") and project.user_id != current_user.id:
            raise PermissionException("没有权限查看此项目的文档")
        
        return self.crud_document.get_multi_with_details(
            db=db, project_id=project_id, skip=skip, limit=limit
        )
    
    # 文档导出
    def export_document(
        self,
        db: Session,
        *,
        document_id: int,
        export_request: DocumentExportRequest,
        current_user: User
    ) -> DocumentExportResponse:
        """导出文档"""
        return document_export_service.create_export_request(
            db=db, document_id=document_id, export_request=export_request, current_user=current_user
        )
    
    def get_export_status(
        self,
        db: Session,
        *,
        export_id: int,
        current_user: User
    ) -> DocumentExportWithDetails:
        """获取导出状态"""
        return document_export_service.get_export_status(
            db=db, export_id=export_id, current_user=current_user
        )
    
    def get_export_history(
        self,
        db: Session,
        *,
        document_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
        current_user: User = None
    ) -> List[DocumentExportWithDetails]:
        """获取导出历史"""
        return document_export_service.get_export_history(
            db=db, document_id=document_id, skip=skip, limit=limit, current_user=current_user
        )
    
    def delete_export(
        self,
        db: Session,
        *,
        export_id: int,
        current_user: User
    ) -> bool:
        """删除导出记录"""
        return document_export_service.delete_export(
            db=db, export_id=export_id, current_user=current_user
        )
    
    def get_export_templates(
        self,
        *,
        export_format: Optional[ExportFormat] = None
    ) -> List[ExportTemplate]:
        """获取导出模板列表"""
        return document_export_service.get_export_templates(export_format=export_format)
    
    def get_export_statistics(
        self,
        db: Session,
        *,
        days: int = 30,
        current_user: User = None
    ) -> ExportStatistics:
        """获取导出统计"""
        return document_export_service.get_export_statistics(
            db=db, days=days, current_user=current_user
        )


# 创建实例
crud_document = CRUDDocument(Document)
crud_document_version = CRUDDocumentVersion(DocumentVersion)
crud_document_export = CRUDDocumentExport(DocumentExport)
document_service = DocumentService()