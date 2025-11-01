"""
文档导出服务层实现
"""
import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.document import Document, DocumentFormat
from app.models.document_export import DocumentExport, ExportFormat
from app.models.user import User
from app.schemas.document_export import (
    DocumentExportCreate, DocumentExportUpdate, DocumentExportWithDetails,
    DocumentExportRequest, DocumentExportResponse, ExportStatus,
    ExportOptions, ExportTemplate, ExportTemplateCreate, ExportTemplateUpdate,
    ExportStatistics
)
from app.services.base import CRUDBase
from app.core.exceptions import PermissionException, NotFoundException, ValidationException
from app.core.config import settings
from app.utils.document_export import (
    export_document, cleanup_export_file, get_export_file_url,
    validate_export_options, DocumentExportError
)
from app.utils.file import FileManager

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
        "user": ["read_own", "write_own", "document:read", "document:write", "document:create", "document:delete", "document:export"],
        "admin": ["read_own", "write_own", "read_team", "write_team", "read_all", "write_all", "admin", 
                 "document:read", "document:write", "document:create", "document:delete", "document:export", "system:admin"],
    }
    
    user_permissions = permission_map.get(user.role, [])
    return permission in user_permissions


class CRUDDocumentExport(CRUDBase[DocumentExport, DocumentExportCreate, DocumentExportUpdate]):
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
        
        # 确定导出状态
        status = ExportStatus.COMPLETED
        error_message = None
        if not export.file_url:
            status = ExportStatus.PENDING
        elif export.file_url and export.file_url.startswith("error:"):
            status = ExportStatus.FAILED
            error_message = export.file_url[6:]  # 移除 "error:" 前缀
        
        return DocumentExportWithDetails(
            id=int(export.id),
            document_id=int(export.document_id),
            user_id=int(export.user_id),
            format=ExportFormat(export.format.value),
            file_url=export.file_url if status == ExportStatus.COMPLETED else None,
            file_name=export.file_name,
            file_size=export.file_size,
            created_at=export.created_at,
            document_title=document_title,
            user_name=user_name,
            status=status,
            error_message=error_message,
            download_url=export.file_url if status == ExportStatus.COMPLETED else None
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
            
            # 确定导出状态
            status = ExportStatus.COMPLETED
            error_message = None
            if not export.file_url:
                status = ExportStatus.PENDING
            elif export.file_url and export.file_url.startswith("error:"):
                status = ExportStatus.FAILED
                error_message = export.file_url[6:]  # 移除 "error:" 前缀
            
            result.append(DocumentExportWithDetails(
                id=int(export.id),
                document_id=int(export.document_id),
                user_id=int(export.user_id),
                format=ExportFormat(export.format.value),
                file_url=export.file_url if status == ExportStatus.COMPLETED else None,
                file_name=export.file_name,
                file_size=export.file_size,
                created_at=export.created_at,
                document_title=document_title,
                user_name=user_name,
                status=status,
                error_message=error_message,
                download_url=export.file_url if status == ExportStatus.COMPLETED else None
            ))
        
        return result

    def update_status(
        self, 
        db: Session, 
        *, 
        export_id: int, 
        status: ExportStatus, 
        file_url: Optional[str] = None,
        file_name: Optional[str] = None,
        file_size: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> DocumentExport:
        """更新导出状态"""
        export = self.get(db, id=export_id)
        if not export:
            raise NotFoundException(f"导出记录 {export_id} 不存在")
        
        update_data = {}
        if status == ExportStatus.COMPLETED:
            update_data["file_url"] = file_url
            update_data["file_name"] = file_name
            update_data["file_size"] = file_size
        elif status == ExportStatus.FAILED:
            update_data["file_url"] = f"error:{error_message}" if error_message else "error:Unknown error"
        
        return self.update(db, db_obj=export, obj_in=update_data)


class DocumentExportService:
    """文档导出服务类，继承自BaseService"""
    
    def __init__(self):
        self.crud_document_export = CRUDDocumentExport(DocumentExport)
        self._export_templates: Dict[str, ExportTemplate] = {}
        self._default_options = ExportOptions()
        self._initialize_default_templates()
        self.file_manager = FileManager()
    
    def _initialize_default_templates(self):
        """初始化默认导出模板"""
        # PDF默认模板
        self._export_templates["pdf_default"] = ExportTemplate(
            id=None,
            name="PDF默认模板",
            description="适用于大多数PDF文档导出的默认模板",
            format=ExportFormat.PDF,
            options=ExportOptions(
                pdf_page_size="A4",
                pdf_orientation="portrait",
                pdf_margin_top=2.54,
                pdf_margin_bottom=2.54,
                pdf_margin_left=1.91,
                pdf_margin_right=1.91,
                pdf_font_size=12,
                pdf_line_height=1.5,
                include_header=True,
                include_footer=True,
                include_page_numbers=True
            ),
            is_default=True,
            is_active=True
        )
        
        # Word默认模板
        self._export_templates["word_default"] = ExportTemplate(
            id=None,
            name="Word默认模板",
            description="适用于大多数Word文档导出的默认模板",
            format=ExportFormat.WORD,
            options=ExportOptions(
                word_page_size="A4",
                word_orientation="portrait",
                word_margin_top=2.54,
                word_margin_bottom=2.54,
                word_margin_left=1.91,
                word_margin_right=1.91,
                word_font_size=12,
                word_line_height=1.5,
                include_header=True,
                include_footer=True,
                include_page_numbers=True
            ),
            is_default=True,
            is_active=True
        )
        
        # HTML默认模板
        self._export_templates["html_default"] = ExportTemplate(
            id=None,
            name="HTML默认模板",
            description="适用于大多数HTML文档导出的默认模板",
            format=ExportFormat.HTML,
            options=ExportOptions(
                html_css_style="default",
                html_include_toc=True,
                html_responsive=True,
                include_header=True,
                include_footer=True
            ),
            is_default=True,
            is_active=True
        )
        
        # Markdown默认模板
        self._export_templates["markdown_default"] = ExportTemplate(
            id=None,
            name="Markdown默认模板",
            description="适用于大多数Markdown文档导出的默认模板",
            format=ExportFormat.MARKDOWN,
            options=ExportOptions(),
            is_default=True,
            is_active=True
        )
    
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
        
        if not self._can_export_document(document, current_user):
            raise PermissionException("没有权限导出此文档")
        
        # 获取导出选项
        options = self._get_export_options(export_request)
        
        # 验证导出选项
        if not validate_export_options(options):
            raise ValidationException("导出选项无效")
        
        # 创建导出记录
        db_obj = DocumentExport(
            document_id=document_id,
            user_id=current_user.id,
            format=export_request.format
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 启动异步导出任务
        asyncio.create_task(
            self._process_export_task(
                db,
                export_id=db_obj.id,
                document=document,
                export_request=export_request,
                options=options,
                current_user=current_user
            )
        )
        
        logger.info(f"用户 {current_user.id} 创建了文档 {document_id} 的 {export_request.format.value} 格式导出请求")
        
        return DocumentExportResponse(
            export_id=db_obj.id,
            status=ExportStatus.PROCESSING,
            message="导出任务已创建，正在处理中",
            estimated_time=self._estimate_export_time(document.content, export_request.format)
        )
    
    async def _process_export_task(
        self,
        db: Session,
        *,
        export_id: int,
        document: Document,
        export_request: DocumentExportRequest,
        options: ExportOptions,
        current_user: User
    ):
        """处理导出任务"""
        try:
            # 更新状态为处理中
            self.crud_document_export.update_status(
                db, 
                export_id=export_id, 
                status=ExportStatus.PROCESSING
            )
            
            # 执行导出
            file_path, file_size = export_document(
                content=document.content or "",
                title=document.title,
                export_format=export_request.format,
                options=options,
                source_format=document.format
            )

            # 上传到云存储（如果启用）
            cloud_file_url = None
            cloud_file_path = None
            if settings.STORAGE_TYPE == "cos" and self.file_manager.cloud_storage._is_available():
                try:
                    # 生成云存储路径
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = os.path.splitext(file_path)[1]
                    cloud_filename = f"{document.title}_{timestamp}{file_extension}"
                    cloud_file_path = f"exports/{cloud_filename}"
                    
                    # 上传到云存储
                    upload_result = self.file_manager.cloud_storage.upload_file_from_path(
                        local_file_path=file_path,
                        cloud_file_path=cloud_file_path,
                        metadata={
                            'document_id': str(document.id),
                            'document_title': document.title,
                            'export_format': export_request.format.value,
                            'user_id': str(current_user.id),
                            'export_time': datetime.now().isoformat()
                        }
                    )
                    
                    cloud_file_url = upload_result.get('file_url')
                    logger.info(f"导出文件已上传到云存储: {cloud_file_path}")
                    
                except Exception as e:
                    logger.error(f"上传导出文件到云存储失败: {str(e)}")
                    # 继续使用本地文件
            
            # 获取文件URL
            if cloud_file_url:
                file_url = cloud_file_url
            else:
                file_url = get_export_file_url(file_path)
            
            file_name = os.path.basename(file_path)
            
            # 更新导出记录
            self.crud_document_export.update_status(
                db,
                export_id=export_id,
                status=ExportStatus.COMPLETED,
                file_url=file_url,
                file_name=file_name,
                file_size=file_size
            )
            
            # 如果启用了云存储，备份本地文件到云存储
            if settings.STORAGE_TYPE == "local" and self.file_manager.cloud_storage._is_available():
                try:
                    backup_result = self.file_manager.backup_file_to_cloud(
                        local_file_path=file_path,
                        backup_prefix="exports/backup"
                    )
                    logger.info(f"导出文件已备份到云存储: {backup_result}")
                except Exception as e:
                    logger.warning(f"备份导出文件到云存储失败: {str(e)}")
            
            logger.info(f"导出任务完成: {export_id}, 文件: {file_path}")
            
        except Exception as e:
            # 更新状态为失败
            self.crud_document_export.update_status(
                db, 
                export_id=export_id, 
                status=ExportStatus.FAILED,
                error_message=str(e)
            )
            
            logger.error(f"导出任务失败: {export_id}, 错误: {str(e)}")
    
    def _get_export_options(self, export_request: DocumentExportRequest) -> ExportOptions:
        """获取导出选项"""
        # 从请求中提取选项
        options = ExportOptions()
        
        # PDF选项
        options.pdf_page_size = export_request.page_size or "A4"
        options.pdf_margin_top = 2.54
        options.pdf_margin_bottom = 2.54
        options.pdf_margin_left = 1.91
        options.pdf_margin_right = 1.91
        
        # Word选项
        options.word_page_size = export_request.page_size or "A4"
        options.word_margin_top = 2.54
        options.word_margin_bottom = 2.54
        options.word_margin_left = 1.91
        options.word_margin_right = 1.91
        
        # 通用选项
        options.include_header = export_request.header is not None
        options.include_footer = export_request.footer is not None
        options.include_watermark = export_request.watermark is not None
        options.watermark_text = export_request.watermark
        
        return options
    
    def _estimate_export_time(self, content: str, export_format: ExportFormat) -> int:
        """估算导出时间（秒）"""
        if not content:
            return 5
        
        content_length = len(content)
        
        # 基础时间
        base_time = 5
        
        # 根据内容长度增加时间
        if content_length < 1000:
            return base_time
        elif content_length < 5000:
            return base_time + 10
        elif content_length < 20000:
            return base_time + 30
        else:
            return base_time + 60
        
        # 根据格式调整时间
        if export_format == ExportFormat.PDF:
            return int(base_time * 1.5)
        elif export_format == ExportFormat.WORD:
            return int(base_time * 1.2)
        
        return base_time
    
    def _can_export_document(self, document: Document, user: User) -> bool:
        """检查用户是否可以导出文档"""
        # 管理员可以导出所有文档
        if has_permission(user, "system:admin"):
            return True
        
        # 项目所有者可以导出项目的文档
        if document.project and document.project.user_id == user.id:
            return True
        
        # 检查导出权限
        if has_permission(user, "document:export"):
            return True
        
        return False
    
    def get_export_status(
        self, 
        db: Session, 
        *, 
        export_id: int, 
        current_user: User
    ) -> DocumentExportWithDetails:
        """获取导出状态"""
        export = self.crud_document_export.get_with_details(db, export_id=export_id)
        if not export:
            raise NotFoundException(f"导出记录 {export_id} 不存在")
        
        # 检查权限
        if export.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限查看此导出记录")
        
        return export
    
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
        user_id = None
        if current_user and not has_permission(current_user, "system:admin"):
            user_id = current_user.id
        
        return self.crud_document_export.get_multi_with_details(
            db=db, document_id=document_id, user_id=user_id, skip=skip, limit=limit
        )
    
    def delete_export(
        self, 
        db: Session, 
        *, 
        export_id: int, 
        current_user: User
    ) -> bool:
        """删除导出记录"""
        export = self.crud_document_export.get(db, id=export_id)
        if not export:
            raise NotFoundException(f"导出记录 {export_id} 不存在")
        
        # 检查权限
        if export.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限删除此导出记录")
        
        # 清理导出文件
        if export.file_url and not export.file_url.startswith("error:"):
            file_path = export.file_url
            
            # 检查是否是云存储URL
            if file_path.startswith(('http://', 'https://')):
                # 云存储文件，尝试从URL中提取路径
                if '/exports/' in file_path:
                    cloud_path = file_path.split('/exports/')[-1]
                    cloud_path = f"exports/{cloud_path}"
                    
                    # 从云存储删除
                    try:
                        if self.file_manager.cloud_storage._is_available():
                            self.file_manager.cloud_storage.delete_file(cloud_path)
                            logger.info(f"已从云存储删除导出文件: {cloud_path}")
                    except Exception as e:
                        logger.error(f"从云存储删除导出文件失败: {str(e)}")
            else:
                # 本地文件
                if not os.path.isabs(file_path):
                    # 如果是相对路径，转换为绝对路径
                    export_dir = os.environ.get("EXPORT_DIR", "exports")
                    file_path = os.path.join(export_dir, os.path.basename(file_path))
                
                cleanup_export_file(file_path)
        
        # 删除记录
        self.crud_document_export.remove(db, id=export_id)
        
        logger.info(f"用户 {current_user.id} 删除了导出记录 {export_id}")
        return True
    
    def get_export_templates(
        self, 
        *, 
        export_format: Optional[ExportFormat] = None
    ) -> List[ExportTemplate]:
        """获取导出模板列表"""
        templates = list(self._export_templates.values())
        
        if export_format:
            templates = [t for t in templates if t.format == export_format]
        
        return templates
    
    def get_export_template(
        self, 
        *, 
        template_id: str
    ) -> Optional[ExportTemplate]:
        """获取导出模板"""
        return self._export_templates.get(template_id)
    
    def create_export_template(
        self, 
        *, 
        template_in: ExportTemplateCreate
    ) -> ExportTemplate:
        """创建导出模板"""
        template_id = f"{template_in.format.value}_{template_in.name.lower().replace(' ', '_')}"
        
        template = ExportTemplate(
            id=None,
            name=template_in.name,
            description=template_in.description,
            format=template_in.format,
            options=template_in.options,
            is_default=template_in.is_default,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self._export_templates[template_id] = template
        
        logger.info(f"创建导出模板: {template_id}")
        return template
    
    def update_export_template(
        self, 
        *, 
        template_id: str, 
        template_in: ExportTemplateUpdate
    ) -> Optional[ExportTemplate]:
        """更新导出模板"""
        if template_id not in self._export_templates:
            return None
        
        template = self._export_templates[template_id]
        
        update_data = template_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.now()
        
        logger.info(f"更新导出模板: {template_id}")
        return template
    
    def delete_export_template(
        self, 
        *, 
        template_id: str
    ) -> bool:
        """删除导出模板"""
        if template_id not in self._export_templates:
            return False
        
        # 不允许删除默认模板
        if self._export_templates[template_id].is_default:
            return False
        
        del self._export_templates[template_id]
        
        logger.info(f"删除导出模板: {template_id}")
        return True
    
    def get_export_statistics(
        self, 
        db: Session, 
        *, 
        days: int = 30,
        current_user: User = None
    ) -> ExportStatistics:
        """获取导出统计"""
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 构建查询
        query = db.query(DocumentExport).filter(
            DocumentExport.created_at >= start_date,
            DocumentExport.created_at <= end_date
        )
        
        # 如果不是管理员，只查询用户的导出记录
        if current_user and not has_permission(current_user, "system:admin"):
            query = query.filter(DocumentExport.user_id == current_user.id)
        
        exports = query.all()
        
        # 计算统计数据
        total_exports = len(exports)
        successful_exports = len([e for e in exports if e.file_url and not e.file_url.startswith("error:")])
        failed_exports = total_exports - successful_exports
        
        # 按格式统计
        exports_by_format = {}
        for export in exports:
            format_name = export.format.value
            exports_by_format[format_name] = exports_by_format.get(format_name, 0) + 1
        
        # 按用户统计
        exports_by_user = {}
        for export in exports:
            user_name = export.user.full_name if export.user else f"用户{export.user_id}"
            exports_by_user[user_name] = exports_by_user.get(user_name, 0) + 1
        
        # 文件大小统计
        successful_exports_with_size = [e for e in exports if e.file_size]
        total_file_size = sum(e.file_size for e in successful_exports_with_size)
        average_file_size = total_file_size / len(successful_exports_with_size) if successful_exports_with_size else 0
        
        # 最常导出的文档
        document_counts = {}
        for export in exports:
            doc_id = export.document_id
            doc_title = export.document.title if export.document else f"文档{doc_id}"
            document_counts[doc_title] = document_counts.get(doc_title, 0) + 1
        
        most_exported_documents = [
            {"title": title, "count": count} 
            for title, count in sorted(document_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # 获取存储统计
        storage_stats = {}
        if self.file_manager.cloud_storage._is_available():
            try:
                # 统计云存储中的导出文件
                cloud_files = self.file_manager.cloud_storage.list_files("exports/", max_keys=1000)
                storage_stats = {
                    "cloud_files_count": len(cloud_files),
                    "cloud_total_size": sum(f.get('size', 0) for f in cloud_files),
                    "cloud_storage_type": "cos"
                }
            except Exception as e:
                logger.error(f"获取云存储统计失败: {str(e)}")
        
        return ExportStatistics(
            total_exports=total_exports,
            successful_exports=successful_exports,
            failed_exports=failed_exports,
            exports_by_format=exports_by_format,
            exports_by_user=exports_by_user,
            average_file_size=average_file_size / 1024,  # 转换为KB
            total_file_size=total_file_size / 1024,  # 转换为KB
            most_exported_documents=most_exported_documents,
            storage_stats=storage_stats
        )


# 创建实例
crud_document_export = CRUDDocumentExport(DocumentExport)
document_export_service = DocumentExportService()