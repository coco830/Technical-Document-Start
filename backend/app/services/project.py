from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import logging

from app.models.project import Project, ProjectForm, FormField, ProjectType, ProjectStatus
from app.models.user import User
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectFormCreate, ProjectFormUpdate,
    ProjectStatistics, ProjectWithDetails, ProjectFormWithDetails
)
from app.services.base import CRUDBase
from app.core.exceptions import PermissionException, NotFoundException

# 设置日志
logger = logging.getLogger(__name__)


def has_permission(user: User, permission: str) -> bool:
    """检查用户是否有特定权限"""
    if not user or not user.is_active:
        return False
    
    # 简单的权限检查，可以根据需要扩展
    if user.role == "admin":
        return True
    
    # 可以在这里添加更复杂的权限逻辑
    permission_map = {
        "user": ["read_own", "write_own", "project:read", "project:write", "project:create", "project:delete"],
        "admin": ["read_own", "write_own", "read_team", "write_team", "read_all", "write_all", "admin", 
                 "project:read", "project:write", "project:create", "project:delete", "system:admin"],
    }
    
    user_permissions = permission_map.get(user.role, [])
    return permission in user_permissions


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """获取用户的项目列表"""
        return (
            db.query(self.model)
            .filter(Project.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_company_id(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """获取企业的项目列表"""
        return (
            db.query(self.model)
            .filter(Project.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(self, db: Session, *, status: ProjectStatus, skip: int = 0, limit: int = 100) -> List[Project]:
        """根据状态获取项目列表"""
        return (
            db.query(self.model)
            .filter(Project.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(self, db: Session, *, project_type: ProjectType, skip: int = 0, limit: int = 100) -> List[Project]:
        """根据类型获取项目列表"""
        return (
            db.query(self.model)
            .filter(Project.type == project_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_projects(
        self, db: Session, *, query: str, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """搜索项目"""
        filters = [
            or_(
                Project.name.ilike(f"%{query}%"),
                Project.description.ilike(f"%{query}%"),
            )
        ]
        
        if user_id:
            filters.append(Project.user_id == user_id)
        
        return (
            db.query(self.model)
            .filter(and_(*filters))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db: Session, *, project_id: int) -> Optional[ProjectWithDetails]:
        """获取包含详细信息的项目"""
        project = db.query(self.model).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # 获取关联信息
        user_name = project.user.full_name if project.user else None
        company_name = project.company.name if project.company else None
        documents_count = len(project.documents) if project.documents else 0
        forms_count = len(project.project_forms) if project.project_forms else 0
        
        # 计算项目进度
        progress = self._calculate_project_progress(project)
        
        return ProjectWithDetails(
            id=int(project.id),
            user_id=int(project.user_id),
            company_id=int(project.company_id) if project.company_id else None,
            name=str(project.name),
            type=ProjectType(project.type.value),
            status=ProjectStatus(project.status.value),
            description=str(project.description) if project.description else None,
            metadata=dict(project.metadata) if project.metadata else None,
            created_at=project.created_at,
            updated_at=project.updated_at,
            completed_at=project.completed_at,
            user_name=user_name,
            company_name=company_name,
            documents_count=documents_count,
            forms_count=forms_count,
            progress=progress
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        status: Optional[ProjectStatus] = None,
        project_type: Optional[ProjectType] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[ProjectWithDetails]:
        """获取包含详细信息的多个项目"""
        query = db.query(self.model)
        
        # 应用筛选条件
        if user_id:
            query = query.filter(Project.user_id == user_id)
        if company_id:
            query = query.filter(Project.company_id == company_id)
        if status:
            query = query.filter(Project.status == status)
        if project_type:
            query = query.filter(Project.type == project_type)
        
        # 应用排序
        if order_by and hasattr(Project, order_by):
            order_column = getattr(Project, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        
        projects = query.offset(skip).limit(limit).all()
        
        result = []
        for project in projects:
            user_name = project.user.full_name if project.user else None
            company_name = project.company.name if project.company else None
            documents_count = len(project.documents) if project.documents else 0
            forms_count = len(project.project_forms) if project.project_forms else 0
            progress = self._calculate_project_progress(project)
            
            result.append(ProjectWithDetails(
                id=int(project.id),
                user_id=int(project.user_id),
                company_id=int(project.company_id) if project.company_id else None,
                name=str(project.name),
                type=ProjectType(project.type.value),
                status=ProjectStatus(project.status.value),
                description=str(project.description) if project.description else None,
                metadata=dict(project.metadata) if project.metadata else None,
                created_at=project.created_at,
                updated_at=project.updated_at,
                completed_at=project.completed_at,
                user_name=user_name,
                company_name=company_name,
                documents_count=documents_count,
                forms_count=forms_count,
                progress=progress
            ))
        
        return result

    def create_with_user(self, db: Session, *, obj_in: ProjectCreate, current_user: User) -> Project:
        """创建项目"""
        # 检查权限
        if not has_permission(current_user, "project:create"):
            raise PermissionException("没有创建项目的权限")
        
        # 如果指定了user_id，检查是否有权限为其他用户创建项目
        if obj_in.user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限为其他用户创建项目")
        
        db_obj = Project(
            user_id=obj_in.user_id,
            company_id=obj_in.company_id,
            name=obj_in.name,
            type=obj_in.type,
            status=obj_in.status,
            description=obj_in.description,
            metadata=obj_in.metadata,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"用户 {current_user.id} 创建了项目 {db_obj.id}")
        return db_obj

    def update_with_user(
        self, 
        db: Session, 
        *, 
        db_obj: Project, 
        obj_in: Union[ProjectUpdate, Dict[str, Any]],
        current_user: User
    ) -> Project:
        """更新项目"""
        # 检查权限
        if not self._can_modify_project(db_obj, current_user):
            raise PermissionException("没有修改此项目的权限")
        
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        # 如果状态变为已完成，设置完成时间
        if "status" in update_data and update_data["status"] == ProjectStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        
        result = super().update(db, db_obj=db_obj, obj_in=update_data)
        
        logger.info(f"用户 {current_user.id} 更新了项目 {db_obj.id}")
        return result

    def delete_with_user(self, db: Session, *, project_id: int, current_user: User) -> Project:
        """删除项目"""
        project = self.get(db, id=project_id)
        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")
        
        # 检查权限
        if not self._can_modify_project(project, current_user):
            raise PermissionException("没有删除此项目的权限")
        
        db.delete(project)
        db.commit()
        
        logger.info(f"用户 {current_user.id} 删除了项目 {project_id}")
        return project

    def update_status(
        self, 
        db: Session, 
        *, 
        project_id: int, 
        status: ProjectStatus, 
        current_user: User
    ) -> Project:
        """更新项目状态"""
        project = self.get(db, id=project_id)
        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")
        
        # 检查权限
        if not self._can_modify_project(project, current_user):
            raise PermissionException("没有修改此项目状态的权限")
        
        old_status = project.status
        project.status = status
        
        # 如果状态变为已完成，设置完成时间
        if status == ProjectStatus.COMPLETED:
            project.completed_at = datetime.utcnow()
        elif old_status == ProjectStatus.COMPLETED and status != ProjectStatus.COMPLETED:
            # 如果从已完成状态变为其他状态，清除完成时间
            project.completed_at = None
        
        db.commit()
        db.refresh(project)
        
        logger.info(f"用户 {current_user.id} 将项目 {project_id} 状态从 {old_status} 更新为 {status}")
        return project

    def get_statistics(self, db: Session, *, user_id: Optional[int] = None, current_user: Optional[User] = None) -> ProjectStatistics:
        """获取项目统计信息"""
        # 检查权限
        if current_user and not has_permission(current_user, "project:read"):
            raise PermissionException("没有查看项目统计的权限")
        
        # 如果指定了user_id，检查是否有权限查看其他用户的统计
        if user_id and current_user and user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限查看其他用户的项目统计")
        
        # 构建基础查询
        base_query = db.query(self.model)
        if user_id:
            base_query = base_query.filter(Project.user_id == user_id)
        
        # 总项目数
        total_projects = base_query.count()
        
        # 活跃项目数（非草稿和非归档状态）
        active_projects = base_query.filter(
            Project.status.in_([ProjectStatus.GENERATING, ProjectStatus.REVIEWING])
        ).count()
        
        # 已完成项目数
        completed_projects = base_query.filter(Project.status == ProjectStatus.COMPLETED).count()
        
        # 按类型统计
        projects_by_type = {}
        for project_type in ProjectType:
            count = base_query.filter(Project.type == project_type).count()
            projects_by_type[project_type.value] = count
        
        # 按状态统计
        projects_by_status = {}
        for status in ProjectStatus:
            count = base_query.filter(Project.status == status).count()
            projects_by_status[status.value] = count
        
        # 今日新增项目
        today = datetime.utcnow().date()
        new_projects_today = base_query.filter(
            and_(
                Project.created_at >= today,
                Project.created_at < today + timedelta(days=1)
            )
        ).count()
        
        # 本周新增项目
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_projects_this_week = base_query.filter(Project.created_at >= week_ago).count()
        
        # 本月新增项目
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_projects_this_month = base_query.filter(Project.created_at >= month_ago).count()
        
        # 项目创建趋势（最近7天）
        project_creation_trend = []
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            count = base_query.filter(
                and_(
                    Project.created_at >= date,
                    Project.created_at < date + timedelta(days=1)
                )
            ).count()
            project_creation_trend.append({
                "date": date.isoformat(),
                "count": count
            })
        project_creation_trend.reverse()  # 按时间正序排列
        
        # 平均完成时间
        completed_projects_with_time = base_query.filter(
            and_(
                Project.status == ProjectStatus.COMPLETED,
                Project.completed_at.isnot(None)
            )
        ).all()
        
        average_completion_time = None
        if completed_projects_with_time:
            total_time = sum(
                (p.completed_at - p.created_at).total_seconds() / 86400  # 转换为天数
                for p in completed_projects_with_time
            )
            average_completion_time = total_time / len(completed_projects_with_time)
        
        return ProjectStatistics(
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            projects_by_type=projects_by_type,
            projects_by_status=projects_by_status,
            new_projects_today=new_projects_today,
            new_projects_this_week=new_projects_this_week,
            new_projects_this_month=new_projects_this_month,
            project_creation_trend=project_creation_trend,
            average_completion_time=average_completion_time
        )

    def _can_modify_project(self, project: Project, user: User) -> bool:
        """检查用户是否可以修改项目"""
        # 管理员可以修改所有项目
        if has_permission(user, "system:admin"):
            return True
        
        # 项目所有者可以修改自己的项目
        if project.user_id == user.id:
            return True
        
        # 检查企业权限（如果项目属于企业）
        if project.company_id and hasattr(user, 'company_id') and user.company_id == project.company_id:
            # 这里可以添加更复杂的企业权限检查
            return True
        
        return False

    def _calculate_project_progress(self, project: Project) -> float:
        """计算项目进度"""
        # 根据项目状态计算进度
        status_progress = {
            ProjectStatus.DRAFT: 0.0,
            ProjectStatus.GENERATING: 0.3,
            ProjectStatus.REVIEWING: 0.7,
            ProjectStatus.COMPLETED: 1.0,
            ProjectStatus.ARCHIVED: 1.0,
        }
        
        base_progress = status_progress.get(project.status, 0.0)
        
        # 可以根据其他因素调整进度，例如表单完成度、文档数量等
        # 这里只是一个简单的实现
        
        return base_progress


class CRUDProjectForm(CRUDBase[ProjectForm, ProjectFormCreate, ProjectFormUpdate]):
    def get_by_project_id(self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100) -> List[ProjectForm]:
        """获取项目的表单列表"""
        return (
            db.query(self.model)
            .filter(ProjectForm.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(self, db: Session, *, form_type: str, skip: int = 0, limit: int = 100) -> List[ProjectForm]:
        """根据类型获取表单列表"""
        return (
            db.query(self.model)
            .filter(ProjectForm.form_type == form_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_details(self, db: Session, *, form_id: int) -> Optional[ProjectFormWithDetails]:
        """获取包含详细信息的表单"""
        form = db.query(self.model).filter(ProjectForm.id == form_id).first()
        if not form:
            return None
        
        # 获取关联信息
        project_name = form.project.name if form.project else None
        fields_count = len(form.form_fields) if form.form_fields else 0
        
        return ProjectFormWithDetails(
            id=int(form.id),
            project_id=int(form.project_id),
            form_type=str(form.form_type),
            form_data=dict(form.form_data),
            created_at=form.created_at,
            updated_at=form.updated_at,
            project_name=project_name,
            fields_count=fields_count
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        project_id: Optional[int] = None,
        form_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ProjectFormWithDetails]:
        """获取包含详细信息的多个表单"""
        query = db.query(self.model)
        
        # 应用筛选条件
        if project_id:
            query = query.filter(ProjectForm.project_id == project_id)
        if form_type:
            query = query.filter(ProjectForm.form_type == form_type)
        
        forms = query.offset(skip).limit(limit).all()
        
        result = []
        for form in forms:
            project_name = form.project.name if form.project else None
            fields_count = len(form.form_fields) if form.form_fields else 0
            
            result.append(ProjectFormWithDetails(
                id=int(form.id),
                project_id=int(form.project_id),
                form_type=str(form.form_type),
                form_data=dict(form.form_data),
                created_at=form.created_at,
                updated_at=form.updated_at,
                project_name=project_name,
                fields_count=fields_count
            ))
        
        return result

    def create_with_user(self, db: Session, *, obj_in: ProjectFormCreate, current_user: User) -> ProjectForm:
        """创建项目表单"""
        # 检查项目权限
        project = db.query(Project).filter(Project.id == obj_in.project_id).first()
        if not project:
            raise NotFoundException(f"项目 {obj_in.project_id} 不存在")
        
        if not crud_project._can_modify_project(project, current_user):
            raise PermissionException("没有权限为此项目创建表单")
        
        db_obj = ProjectForm(
            project_id=obj_in.project_id,
            form_type=obj_in.form_type,
            form_data=obj_in.form_data,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"用户 {current_user.id} 为项目 {obj_in.project_id} 创建了表单 {db_obj.id}")
        return db_obj

    def update_with_user(
        self, 
        db: Session, 
        *, 
        db_obj: ProjectForm, 
        obj_in: Union[ProjectFormUpdate, Dict[str, Any]],
        current_user: User
    ) -> ProjectForm:
        """更新项目表单"""
        # 检查项目权限
        project = db.query(Project).filter(Project.id == db_obj.project_id).first()
        if not project:
            raise NotFoundException(f"项目 {db_obj.project_id} 不存在")
        
        if not crud_project._can_modify_project(project, current_user):
            raise PermissionException("没有权限修改此项目的表单")
        
        result = super().update(db, db_obj=db_obj, obj_in=obj_in)
        
        logger.info(f"用户 {current_user.id} 更新了项目 {db_obj.project_id} 的表单 {db_obj.id}")
        return result

    def delete_with_user(self, db: Session, *, form_id: int, current_user: User) -> ProjectForm:
        """删除项目表单"""
        form = self.get(db, id=form_id)
        if not form:
            raise NotFoundException(f"表单 {form_id} 不存在")
        
        # 检查项目权限
        project = db.query(Project).filter(Project.id == form.project_id).first()
        if not project:
            raise NotFoundException(f"项目 {form.project_id} 不存在")
        
        if not crud_project._can_modify_project(project, current_user):
            raise PermissionException("没有权限删除此项目的表单")
        
        db.delete(form)
        db.commit()
        
        logger.info(f"用户 {current_user.id} 删除了项目 {form.project_id} 的表单 {form_id}")
        return form


class ProjectService:
    """项目服务类，继承自BaseService"""
    
    def __init__(self):
        self.crud_project = CRUDProject(Project)
        self.crud_project_form = CRUDProjectForm(ProjectForm)
    
    def create_project(self, db: Session, *, project_in: ProjectCreate, current_user: User) -> Project:
        """创建项目"""
        return self.crud_project.create_with_user(db=db, obj_in=project_in, current_user=current_user)
    
    def get_project(self, db: Session, *, project_id: int, current_user: User) -> Optional[ProjectWithDetails]:
        """获取单个项目"""
        project = self.crud_project.get(db, id=project_id)
        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")
        
        # 检查权限
        if not self.crud_project._can_modify_project(project, current_user) and \
           not has_permission(current_user, "project:read"):
            raise PermissionException("没有权限查看此项目")
        
        return self.crud_project.get_with_details(db, project_id=project_id)
    
    def get_projects(
        self, 
        db: Session, 
        *, 
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        status: Optional[ProjectStatus] = None,
        project_type: Optional[ProjectType] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True,
        current_user: User = None
    ) -> List[ProjectWithDetails]:
        """获取项目列表（支持分页、筛选、排序）"""
        # 如果指定了user_id，检查是否有权限查看其他用户的项目
        if user_id and current_user and user_id != current_user.id and not has_permission(current_user, "system:admin"):
            raise PermissionException("没有权限查看其他用户的项目")
        
        # 如果没有指定user_id，默认查看当前用户的项目
        if not user_id and current_user and not has_permission(current_user, "system:admin"):
            user_id = current_user.id
        
        return self.crud_project.get_multi_with_details(
            db=db,
            user_id=user_id,
            company_id=company_id,
            status=status,
            project_type=project_type,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def update_project(
        self, 
        db: Session, 
        *, 
        project_id: int, 
        project_in: ProjectUpdate, 
        current_user: User
    ) -> Project:
        """更新项目"""
        project = self.crud_project.get(db, id=project_id)
        if not project:
            raise NotFoundException(f"项目 {project_id} 不存在")
        
        return self.crud_project.update_with_user(db, db_obj=project, obj_in=project_in, current_user=current_user)
    
    def delete_project(self, db: Session, *, project_id: int, current_user: User) -> Project:
        """删除项目"""
        return self.crud_project.delete_with_user(db, project_id=project_id, current_user=current_user)
    
    def update_project_status(
        self, 
        db: Session, 
        *, 
        project_id: int, 
        status: ProjectStatus, 
        current_user: User
    ) -> Project:
        """更新项目状态"""
        return self.crud_project.update_status(db, project_id=project_id, status=status, current_user=current_user)
    
    def get_project_statistics(
        self, 
        db: Session, 
        *, 
        user_id: Optional[int] = None, 
        current_user: Optional[User] = None
    ) -> ProjectStatistics:
        """获取项目统计信息"""
        return self.crud_project.get_statistics(db, user_id=user_id, current_user=current_user)
    
    def create_project_form(self, db: Session, *, form_in: ProjectFormCreate, current_user: User) -> ProjectForm:
        """创建项目表单"""
        return self.crud_project_form.create_with_user(db=db, obj_in=form_in, current_user=current_user)
    
    def update_project_form(
        self, 
        db: Session, 
        *, 
        form_id: int, 
        form_in: ProjectFormUpdate, 
        current_user: User
    ) -> ProjectForm:
        """更新项目表单"""
        form = self.crud_project_form.get(db, id=form_id)
        if not form:
            raise NotFoundException(f"表单 {form_id} 不存在")
        
        return self.crud_project_form.update_with_user(db, db_obj=form, obj_in=form_in, current_user=current_user)
    
    def get_project_forms(
        self, 
        db: Session, 
        *, 
        project_id: Optional[int] = None,
        form_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[ProjectFormWithDetails]:
        """获取项目表单列表"""
        # 如果指定了project_id，检查项目权限
        if project_id:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                raise NotFoundException(f"项目 {project_id} 不存在")
            
            if not self.crud_project._can_modify_project(project, current_user) and \
               not has_permission(current_user, "project:read"):
                raise PermissionException("没有权限查看此项目的表单")
        
        return self.crud_project_form.get_multi_with_details(
            db=db,
            project_id=project_id,
            form_type=form_type,
            skip=skip,
            limit=limit
        )


# 创建实例
crud_project = CRUDProject(Project)
crud_project_form = CRUDProjectForm(ProjectForm)
project_service = ProjectService()