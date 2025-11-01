from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import logging

from app.models.company import Company
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.company import (
    CompanyCreate, CompanyUpdate, CompanyWithDetails, CompanySearch,
    CompanyStatistics, CompanyVerification, CompanyVerificationCreate,
    CompanyVerificationUpdate, CompanyVerificationWithDetails
)
from app.services.base import CRUDBase
from app.core.exceptions import PermissionException, NotFoundException, ValidationException

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
        "user": ["read_own", "write_own", "company:read", "company:write", "company:create", "company:delete"],
        "admin": ["read_own", "write_own", "read_team", "write_team", "read_all", "write_all", "admin", 
                 "company:read", "company:write", "company:create", "company:delete", "company:verify", "system:admin"],
    }
    
    user_permissions = permission_map.get(user.role, [])
    return permission in user_permissions


class CRUDCompany(CRUDBase[Company, CompanyCreate, CompanyUpdate]):
    def get_by_unified_social_credit_code(self, db: Session, *, unified_social_credit_code: str) -> Optional[Company]:
        """根据统一社会信用代码获取企业"""
        return db.query(self.model).filter(
            self.model.unified_social_credit_code == unified_social_credit_code
        ).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Company]:
        """根据企业名称获取企业"""
        return db.query(self.model).filter(self.model.name == name).first()

    def get_by_industry(self, db: Session, *, industry: str, skip: int = 0, limit: int = 100) -> List[Company]:
        """根据行业获取企业列表"""
        return (
            db.query(self.model)
            .filter(Company.industry == industry)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_companies(
        self, 
        db: Session, 
        *, 
        search_params: CompanySearch, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Company]:
        """搜索企业"""
        filters = []
        
        if search_params.keyword:
            filters.append(
                or_(
                    Company.name.ilike(f"%{search_params.keyword}%"),
                    Company.legal_representative.ilike(f"%{search_params.keyword}%"),
                    Company.business_scope.ilike(f"%{search_params.keyword}%"),
                    Company.address.ilike(f"%{search_params.keyword}%"),
                )
            )
        
        if search_params.unified_social_credit_code:
            filters.append(Company.unified_social_credit_code.ilike(f"%{search_params.unified_social_credit_code}%"))
        
        if search_params.industry:
            filters.append(Company.industry == search_params.industry)
        
        if search_params.legal_representative:
            filters.append(Company.legal_representative.ilike(f"%{search_params.legal_representative}%"))
        
        if search_params.contact_phone:
            filters.append(Company.contact_phone.ilike(f"%{search_params.contact_phone}%"))
        
        if search_params.contact_email:
            filters.append(Company.contact_email.ilike(f"%{search_params.contact_email}%"))
        
        if search_params.address:
            filters.append(Company.address.ilike(f"%{search_params.address}%"))
        
        if search_params.created_after:
            filters.append(Company.created_at >= search_params.created_after)
        
        if search_params.created_before:
            filters.append(Company.created_at <= search_params.created_before)
        
        query = db.query(self.model)
        if filters:
            query = query.filter(and_(*filters))
        
        return query.offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, *, company_id: int) -> Optional[CompanyWithDetails]:
        """获取包含详细信息的企业"""
        company = db.query(self.model).filter(Company.id == company_id).first()
        if not company:
            return None
        
        # 获取关联信息
        projects_count = len(company.projects) if company.projects else 0
        
        # 计算活跃项目数和已完成项目数
        active_projects_count = 0
        completed_projects_count = 0
        if company.projects:
            for project in company.projects:
                if project.status in [ProjectStatus.GENERATING, ProjectStatus.REVIEWING]:
                    active_projects_count += 1
                elif project.status == ProjectStatus.COMPLETED:
                    completed_projects_count += 1
        
        # 计算文档数量（这里简化处理，实际可能需要更复杂的查询）
        documents_count = 0
        if company.projects:
            for project in company.projects:
                if hasattr(project, 'documents') and project.documents:
                    documents_count += len(project.documents)
        
        return CompanyWithDetails(
            id=int(company.id),
            name=str(company.name),
            unified_social_credit_code=company.unified_social_credit_code,
            legal_representative=company.legal_representative,
            contact_phone=company.contact_phone,
            contact_email=company.contact_email,
            address=company.address,
            industry=company.industry,
            business_scope=company.business_scope,
            created_at=company.created_at,
            updated_at=company.updated_at,
            projects_count=projects_count,
            active_projects_count=active_projects_count,
            completed_projects_count=completed_projects_count,
            documents_count=documents_count
        )

    def get_multi_with_details(
        self, 
        db: Session, 
        *, 
        search_params: Optional[CompanySearch] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True
    ) -> List[CompanyWithDetails]:
        """获取包含详细信息的多个企业"""
        query = db.query(self.model)
        
        # 应用搜索条件
        if search_params:
            filters = []
            
            if search_params.keyword:
                filters.append(
                    or_(
                        Company.name.ilike(f"%{search_params.keyword}%"),
                        Company.legal_representative.ilike(f"%{search_params.keyword}%"),
                        Company.business_scope.ilike(f"%{search_params.keyword}%"),
                        Company.address.ilike(f"%{search_params.keyword}%"),
                    )
                )
            
            if search_params.unified_social_credit_code:
                filters.append(Company.unified_social_credit_code.ilike(f"%{search_params.unified_social_credit_code}%"))
            
            if search_params.industry:
                filters.append(Company.industry == search_params.industry)
            
            if search_params.legal_representative:
                filters.append(Company.legal_representative.ilike(f"%{search_params.legal_representative}%"))
            
            if search_params.contact_phone:
                filters.append(Company.contact_phone.ilike(f"%{search_params.contact_phone}%"))
            
            if search_params.contact_email:
                filters.append(Company.contact_email.ilike(f"%{search_params.contact_email}%"))
            
            if search_params.address:
                filters.append(Company.address.ilike(f"%{search_params.address}%"))
            
            if search_params.created_after:
                filters.append(Company.created_at >= search_params.created_after)
            
            if search_params.created_before:
                filters.append(Company.created_at <= search_params.created_before)
            
            if filters:
                query = query.filter(and_(*filters))
        
        # 应用排序
        if order_by and hasattr(Company, order_by):
            order_column = getattr(Company, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        
        companies = query.offset(skip).limit(limit).all()
        
        result = []
        for company in companies:
            # 获取关联信息
            projects_count = len(company.projects) if company.projects else 0
            
            # 计算活跃项目数和已完成项目数
            active_projects_count = 0
            completed_projects_count = 0
            if company.projects:
                for project in company.projects:
                    if project.status in [ProjectStatus.GENERATING, ProjectStatus.REVIEWING]:
                        active_projects_count += 1
                    elif project.status == ProjectStatus.COMPLETED:
                        completed_projects_count += 1
            
            # 计算文档数量
            documents_count = 0
            if company.projects:
                for project in company.projects:
                    if hasattr(project, 'documents') and project.documents:
                        documents_count += len(project.documents)
            
            result.append(CompanyWithDetails(
                id=int(company.id),
                name=str(company.name),
                unified_social_credit_code=company.unified_social_credit_code,
                legal_representative=company.legal_representative,
                contact_phone=company.contact_phone,
                contact_email=company.contact_email,
                address=company.address,
                industry=company.industry,
                business_scope=company.business_scope,
                created_at=company.created_at,
                updated_at=company.updated_at,
                projects_count=projects_count,
                active_projects_count=active_projects_count,
                completed_projects_count=completed_projects_count,
                documents_count=documents_count
            ))
        
        return result

    def create_with_user(self, db: Session, *, obj_in: CompanyCreate, current_user: User) -> Company:
        """创建企业"""
        # 检查权限
        if not has_permission(current_user, "company:create"):
            raise PermissionException("没有创建企业的权限")
        
        # 检查统一社会信用代码是否已存在
        if obj_in.unified_social_credit_code:
            existing_company = self.get_by_unified_social_credit_code(
                db, unified_social_credit_code=obj_in.unified_social_credit_code
            )
            if existing_company:
                raise ValidationException("统一社会信用代码已存在")
        
        # 检查企业名称是否已存在
        existing_company = self.get_by_name(db, name=obj_in.name)
        if existing_company:
            raise ValidationException("企业名称已存在")
        
        db_obj = Company(
            name=obj_in.name,
            unified_social_credit_code=obj_in.unified_social_credit_code,
            legal_representative=obj_in.legal_representative,
            contact_phone=obj_in.contact_phone,
            contact_email=obj_in.contact_email,
            address=obj_in.address,
            industry=obj_in.industry,
            business_scope=obj_in.business_scope,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        logger.info(f"用户 {current_user.id} 创建了企业 {db_obj.id}")
        return db_obj

    def update_with_user(
        self, 
        db: Session, 
        *, 
        db_obj: Company, 
        obj_in: Union[CompanyUpdate, Dict[str, Any]],
        current_user: User
    ) -> Company:
        """更新企业"""
        # 检查权限
        if not has_permission(current_user, "company:write"):
            raise PermissionException("没有修改企业的权限")
        
        update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
        
        # 如果更新统一社会信用代码，检查是否已存在
        if "unified_social_credit_code" in update_data and update_data["unified_social_credit_code"]:
            existing_company = self.get_by_unified_social_credit_code(
                db, unified_social_credit_code=update_data["unified_social_credit_code"]
            )
            if existing_company and existing_company.id != db_obj.id:
                raise ValidationException("统一社会信用代码已存在")
        
        # 如果更新企业名称，检查是否已存在
        if "name" in update_data and update_data["name"]:
            existing_company = self.get_by_name(db, name=update_data["name"])
            if existing_company and existing_company.id != db_obj.id:
                raise ValidationException("企业名称已存在")
        
        result = super().update(db, db_obj=db_obj, obj_in=update_data)
        
        logger.info(f"用户 {current_user.id} 更新了企业 {db_obj.id}")
        return result

    def delete_with_user(self, db: Session, *, company_id: int, current_user: User) -> Company:
        """删除企业"""
        company = self.get(db, id=company_id)
        if not company:
            raise NotFoundException(f"企业 {company_id} 不存在")
        
        # 检查权限
        if not has_permission(current_user, "company:delete"):
            raise PermissionException("没有删除企业的权限")
        
        # 检查是否有关联的项目
        if company.projects:
            raise ValidationException("企业有关联的项目，无法删除")
        
        db.delete(company)
        db.commit()
        
        logger.info(f"用户 {current_user.id} 删除了企业 {company_id}")
        return company

    def get_statistics(self, db: Session, *, current_user: Optional[User] = None) -> CompanyStatistics:
        """获取企业统计信息"""
        # 检查权限
        if current_user and not has_permission(current_user, "company:read"):
            raise PermissionException("没有查看企业统计的权限")
        
        # 总企业数
        total_companies = db.query(self.model).count()
        
        # 活跃企业数（有活跃项目的企业）
        active_companies = (
            db.query(self.model)
            .join(Company.projects)
            .filter(Project.status.in_([ProjectStatus.GENERATING, ProjectStatus.REVIEWING]))
            .distinct()
            .count()
        )
        
        # 今日新增企业
        today = datetime.utcnow().date()
        new_companies_today = db.query(self.model).filter(
            and_(
                Company.created_at >= today,
                Company.created_at < today + timedelta(days=1)
            )
        ).count()
        
        # 本周新增企业
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_companies_this_week = db.query(self.model).filter(
            Company.created_at >= week_ago
        ).count()
        
        # 本月新增企业
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_companies_this_month = db.query(self.model).filter(
            Company.created_at >= month_ago
        ).count()
        
        # 按行业统计企业数
        companies_by_industry = {}
        industries = db.query(Company.industry).filter(Company.industry.isnot(None)).distinct().all()
        for industry in industries:
            if industry[0]:  # 确保industry不为None
                count = db.query(self.model).filter(Company.industry == industry[0]).count()
                companies_by_industry[industry[0]] = count
        
        # 企业注册趋势（最近7天）
        company_registration_trend = []
        for i in range(7):
            date = (datetime.utcnow() - timedelta(days=i)).date()
            count = db.query(self.model).filter(
                and_(
                    Company.created_at >= date,
                    Company.created_at < date + timedelta(days=1)
                )
            ).count()
            company_registration_trend.append({
                "date": date.isoformat(),
                "count": count
            })
        company_registration_trend.reverse()  # 按时间正序排列
        
        # 热门行业（按企业数量排序的前5个行业）
        top_industries = []
        sorted_industries = sorted(companies_by_industry.items(), key=lambda x: x[1], reverse=True)
        for industry, count in sorted_industries[:5]:
            top_industries.append({
                "industry": industry,
                "count": count
            })
        
        return CompanyStatistics(
            total_companies=total_companies,
            active_companies=active_companies,
            new_companies_today=new_companies_today,
            new_companies_this_week=new_companies_this_week,
            new_companies_this_month=new_companies_this_month,
            companies_by_industry=companies_by_industry,
            company_registration_trend=company_registration_trend,
            top_industries=top_industries
        )

    def get_companies_by_verification_status(
        self, 
        db: Session, 
        *, 
        verification_status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Company]:
        """按验证状态获取企业"""
        # 这里需要根据实际的验证状态字段来实现
        # 由于Company模型中没有verification_status字段，这里只是一个示例
        # 实际实现可能需要关联验证表或添加验证状态字段
        return (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_company_project_count(self, db: Session, *, company_id: int) -> int:
        """获取企业项目数量"""
        return db.query(Project).filter(Project.company_id == company_id).count()


class CompanyService:
    """企业服务类，继承自BaseService"""
    
    def __init__(self):
        self.crud_company = CRUDCompany(Company)
    
    def create_company(self, db: Session, *, company_in: CompanyCreate, current_user: User) -> Company:
        """创建企业"""
        return self.crud_company.create_with_user(db=db, obj_in=company_in, current_user=current_user)
    
    def get_company(self, db: Session, *, company_id: int, current_user: User) -> Optional[CompanyWithDetails]:
        """获取单个企业"""
        company = self.crud_company.get(db, id=company_id)
        if not company:
            raise NotFoundException(f"企业 {company_id} 不存在")
        
        # 检查权限
        if not has_permission(current_user, "company:read"):
            raise PermissionException("没有权限查看此企业")
        
        return self.crud_company.get_with_details(db, company_id=company_id)
    
    def get_companies(
        self, 
        db: Session, 
        *, 
        search_params: Optional[CompanySearch] = None,
        skip: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = "created_at",
        order_desc: bool = True,
        current_user: User = None
    ) -> List[CompanyWithDetails]:
        """获取企业列表（支持分页、筛选、排序）"""
        # 检查权限
        if current_user and not has_permission(current_user, "company:read"):
            raise PermissionException("没有权限查看企业列表")
        
        return self.crud_company.get_multi_with_details(
            db=db,
            search_params=search_params,
            skip=skip,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def update_company(
        self, 
        db: Session, 
        *, 
        company_id: int, 
        company_in: CompanyUpdate, 
        current_user: User
    ) -> Company:
        """更新企业"""
        company = self.crud_company.get(db, id=company_id)
        if not company:
            raise NotFoundException(f"企业 {company_id} 不存在")
        
        return self.crud_company.update_with_user(db, db_obj=company, obj_in=company_in, current_user=current_user)
    
    def delete_company(self, db: Session, *, company_id: int, current_user: User) -> Company:
        """删除企业"""
        return self.crud_company.delete_with_user(db, company_id=company_id, current_user=current_user)
    
    def search_companies(
        self, 
        db: Session, 
        *, 
        search_params: CompanySearch,
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[Company]:
        """搜索企业（按名称、统一社会信用代码等）"""
        # 检查权限
        if current_user and not has_permission(current_user, "company:read"):
            raise PermissionException("没有权限搜索企业")
        
        return self.crud_company.search_companies(db, search_params=search_params, skip=skip, limit=limit)
    
    def get_companies_by_verification_status(
        self, 
        db: Session, 
        *, 
        verification_status: str,
        skip: int = 0, 
        limit: int = 100,
        current_user: User = None
    ) -> List[Company]:
        """按验证状态获取企业"""
        # 检查权限
        if current_user and not has_permission(current_user, "company:read"):
            raise PermissionException("没有权限查看企业")
        
        return self.crud_company.get_companies_by_verification_status(
            db, verification_status=verification_status, skip=skip, limit=limit
        )
    
    def get_company_statistics(
        self, 
        db: Session, 
        *, 
        current_user: Optional[User] = None
    ) -> CompanyStatistics:
        """获取企业统计信息"""
        return self.crud_company.get_statistics(db, current_user=current_user)
    
    def get_company_project_count(self, db: Session, *, company_id: int, current_user: User = None) -> int:
        """获取企业项目数量"""
        # 检查权限
        if current_user and not has_permission(current_user, "company:read"):
            raise PermissionException("没有权限查看企业项目数量")
        
        return self.crud_company.get_company_project_count(db, company_id=company_id)
    
    def verify_company(
        self, 
        db: Session, 
        *, 
        company_id: int, 
        verification_data: Dict[str, Any],
        current_user: User
    ) -> Dict[str, Any]:
        """验证企业信息"""
        # 检查权限
        if not has_permission(current_user, "company:verify"):
            raise PermissionException("没有权限验证企业")
        
        company = self.crud_company.get(db, id=company_id)
        if not company:
            raise NotFoundException(f"企业 {company_id} 不存在")
        
        # 这里应该实现验证逻辑
        # 由于没有验证表，这里只是一个示例
        verification_result = {
            "company_id": company_id,
            "verification_status": "verified",
            "verified_by": current_user.id,
            "verified_at": datetime.utcnow(),
            "verification_data": verification_data
        }
        
        logger.info(f"用户 {current_user.id} 验证了企业 {company_id}")
        return verification_result
    
    def update_verification_status(
        self, 
        db: Session, 
        *, 
        company_id: int, 
        verification_status: str,
        current_user: User
    ) -> Dict[str, Any]:
        """更新验证状态"""
        # 检查权限
        if not has_permission(current_user, "company:verify"):
            raise PermissionException("没有权限更新企业验证状态")
        
        company = self.crud_company.get(db, id=company_id)
        if not company:
            raise NotFoundException(f"企业 {company_id} 不存在")
        
        # 这里应该实现更新验证状态的逻辑
        # 由于没有验证表，这里只是一个示例
        update_result = {
            "company_id": company_id,
            "verification_status": verification_status,
            "updated_by": current_user.id,
            "updated_at": datetime.utcnow()
        }
        
        logger.info(f"用户 {current_user.id} 更新了企业 {company_id} 的验证状态为 {verification_status}")
        return update_result


# 创建实例
crud_company = CRUDCompany(Company)
company_service = CompanyService()