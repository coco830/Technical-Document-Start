"""
企业服务层测试文件
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.models.company import Company
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus, ProjectType
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanySearch
from app.services.company import CompanyService, CRUDCompany
from app.core.database import get_db
from app.core.exceptions import PermissionException, NotFoundException, ValidationException

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    """创建测试数据库会话"""
    # 创建所有表
    from app.models.base import BaseModel
    BaseModel.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # 删除所有表
        BaseModel.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """创建管理员用户"""
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash="hashed_password",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_company(db_session):
    """创建示例企业"""
    company = Company(
        name="测试企业",
        unified_social_credit_code="91110000123456789X",
        legal_representative="张三",
        contact_phone="13800138000",
        contact_email="contact@testcompany.com",
        address="北京市朝阳区测试街道123号",
        industry="软件开发",
        business_scope="软件开发、技术咨询"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


class TestCRUDCompany:
    """测试企业CRUD基础类"""
    
    def test_create_company(self, db_session, test_user):
        """测试创建企业"""
        crud = CRUDCompany(Company)
        company_in = CompanyCreate(
            name="新企业",
            unified_social_credit_code="91110000987654321Y",
            legal_representative="李四",
            contact_phone="13900139000",
            contact_email="contact@newcompany.com",
            address="上海市浦东新区测试路456号",
            industry="金融服务",
            business_scope="金融服务、投资咨询"
        )
        
        company = crud.create_with_user(db=db_session, obj_in=company_in, current_user=test_user)
        
        assert company.name == "新企业"
        assert company.unified_social_credit_code == "91110000987654321Y"
        assert company.legal_representative == "李四"
    
    def test_get_company(self, db_session, sample_company):
        """测试获取企业"""
        crud = CRUDCompany(Company)
        company = crud.get(db=db_session, id=sample_company.id)
        
        assert company is not None
        assert company.id == sample_company.id
        assert company.name == "测试企业"
    
    def test_get_by_unified_social_credit_code(self, db_session, sample_company):
        """测试根据统一社会信用代码获取企业"""
        crud = CRUDCompany(Company)
        company = crud.get_by_unified_social_credit_code(
            db=db_session, 
            unified_social_credit_code="91110000123456789X"
        )
        
        assert company is not None
        assert company.id == sample_company.id
        assert company.name == "测试企业"
    
    def test_get_by_name(self, db_session, sample_company):
        """测试根据企业名称获取企业"""
        crud = CRUDCompany(Company)
        company = crud.get_by_name(db=db_session, name="测试企业")
        
        assert company is not None
        assert company.id == sample_company.id
    
    def test_update_company(self, db_session, sample_company, test_user):
        """测试更新企业"""
        crud = CRUDCompany(Company)
        company_in = CompanyUpdate(
            name="更新后的企业名称",
            contact_phone="13700137000"
        )
        
        updated_company = crud.update_with_user(
            db=db_session, 
            db_obj=sample_company, 
            obj_in=company_in, 
            current_user=test_user
        )
        
        assert updated_company.name == "更新后的企业名称"
        assert updated_company.contact_phone == "13700137000"
        assert updated_company.unified_social_credit_code == "91110000123456789X"  # 未更改的字段保持不变
    
    def test_delete_company(self, db_session, sample_company, admin_user):
        """测试删除企业"""
        crud = CRUDCompany(Company)
        company_id = sample_company.id
        
        deleted_company = crud.delete_with_user(
            db=db_session, 
            company_id=company_id, 
            current_user=admin_user
        )
        
        assert deleted_company.id == company_id
        
        # 验证企业已被删除
        company = crud.get(db=db_session, id=company_id)
        assert company is None
    
    def test_search_companies(self, db_session, sample_company):
        """测试搜索企业"""
        crud = CRUDCompany(Company)
        search_params = CompanySearch(
            keyword="测试",
            industry="软件开发"
        )
        
        companies = crud.search_companies(
            db=db_session, 
            search_params=search_params, 
            skip=0, 
            limit=100
        )
        
        assert len(companies) >= 1
        assert any(company.id == sample_company.id for company in companies)
    
    def test_get_with_details(self, db_session, sample_company):
        """测试获取包含详细信息的企业"""
        crud = CRUDCompany(Company)
        company_with_details = crud.get_with_details(db=db_session, company_id=sample_company.id)
        
        assert company_with_details is not None
        assert company_with_details.id == sample_company.id
        assert company_with_details.name == "测试企业"
        assert company_with_details.projects_count == 0  # 初始没有项目
        assert company_with_details.active_projects_count == 0
        assert company_with_details.completed_projects_count == 0
        assert company_with_details.documents_count == 0


class TestCompanyService:
    """测试企业服务类"""
    
    def test_create_company_service(self, db_session, test_user):
        """测试通过服务创建企业"""
        service = CompanyService()
        company_in = CompanyCreate(
            name="服务创建的企业",
            unified_social_credit_code="91110000112233445Z",
            legal_representative="王五",
            contact_phone="13600136000",
            contact_email="contact@servicecompany.com",
            address="广州市天河区测试大道789号",
            industry="电子商务",
            business_scope="电子商务、在线销售"
        )
        
        company = service.create_company(db=db_session, company_in=company_in, current_user=test_user)
        
        assert company.name == "服务创建的企业"
        assert company.unified_social_credit_code == "91110000112233445Z"
    
    def test_get_company_service(self, db_session, sample_company, test_user):
        """测试通过服务获取企业"""
        service = CompanyService()
        company_with_details = service.get_company(
            db=db_session, 
            company_id=sample_company.id, 
            current_user=test_user
        )
        
        assert company_with_details is not None
        assert company_with_details.id == sample_company.id
        assert company_with_details.name == "测试企业"
    
    def test_get_companies_service(self, db_session, sample_company, test_user):
        """测试通过服务获取企业列表"""
        service = CompanyService()
        companies = service.get_companies(
            db=db_session, 
            skip=0, 
            limit=100, 
            current_user=test_user
        )
        
        assert len(companies) >= 1
        assert any(company.id == sample_company.id for company in companies)
    
    def test_update_company_service(self, db_session, sample_company, test_user):
        """测试通过服务更新企业"""
        service = CompanyService()
        company_in = CompanyUpdate(
            name="服务更新的企业名称",
            business_scope="更新后的经营范围"
        )
        
        updated_company = service.update_company(
            db=db_session, 
            company_id=sample_company.id, 
            company_in=company_in, 
            current_user=test_user
        )
        
        assert updated_company.name == "服务更新的企业名称"
        assert updated_company.business_scope == "更新后的经营范围"
    
    def test_search_companies_service(self, db_session, sample_company, test_user):
        """测试通过服务搜索企业"""
        service = CompanyService()
        search_params = CompanySearch(
            keyword="企业",
            industry="软件开发"
        )
        
        companies = service.search_companies(
            db=db_session, 
            search_params=search_params, 
            skip=0, 
            limit=100, 
            current_user=test_user
        )
        
        assert len(companies) >= 1
        assert any(company.id == sample_company.id for company in companies)
    
    def test_get_company_statistics(self, db_session, sample_company, test_user):
        """测试获取企业统计信息"""
        service = CompanyService()
        statistics = service.get_company_statistics(db=db_session, current_user=test_user)
        
        assert statistics.total_companies >= 1
        assert statistics.new_companies_today >= 0
        assert statistics.new_companies_this_week >= 0
        assert statistics.new_companies_this_month >= 0
        assert isinstance(statistics.companies_by_industry, dict)
        assert isinstance(statistics.company_registration_trend, list)
        assert isinstance(statistics.top_industries, list)
    
    def test_get_company_project_count(self, db_session, sample_company, test_user):
        """测试获取企业项目数量"""
        service = CompanyService()
        project_count = service.get_company_project_count(
            db=db_session, 
            company_id=sample_company.id, 
            current_user=test_user
        )
        
        assert project_count == 0  # 初始没有项目
    
    def test_verify_company(self, db_session, sample_company, admin_user):
        """测试验证企业"""
        service = CompanyService()
        verification_data = {
            "verification_type": "business_license",
            "verification_result": "passed",
            "notes": "验证通过"
        }
        
        verification_result = service.verify_company(
            db=db_session, 
            company_id=sample_company.id, 
            verification_data=verification_data, 
            current_user=admin_user
        )
        
        assert verification_result["company_id"] == sample_company.id
        assert verification_result["verification_status"] == "verified"
        assert verification_result["verified_by"] == admin_user.id
    
    def test_update_verification_status(self, db_session, sample_company, admin_user):
        """测试更新验证状态"""
        service = CompanyService()
        update_result = service.update_verification_status(
            db=db_session, 
            company_id=sample_company.id, 
            verification_status="rejected", 
            current_user=admin_user
        )
        
        assert update_result["company_id"] == sample_company.id
        assert update_result["verification_status"] == "rejected"
        assert update_result["updated_by"] == admin_user.id


class TestPermissionChecks:
    """测试权限检查"""
    
    def test_user_permission_denied(self, db_session, test_user):
        """测试普通用户权限被拒绝"""
        service = CompanyService()
        
        # 普通用户尝试验证企业应该失败
        with pytest.raises(PermissionException):
            service.verify_company(
                db=db_session, 
                company_id=1, 
                verification_data={}, 
                current_user=test_user
            )
    
    def test_admin_permission_granted(self, db_session, admin_user):
        """测试管理员权限被允许"""
        service = CompanyService()
        
        # 管理员尝试验证企业应该成功（即使企业不存在会抛出其他异常）
        with pytest.raises(NotFoundException):  # 企业不存在，但权限检查通过
            service.verify_company(
                db=db_session, 
                company_id=999, 
                verification_data={}, 
                current_user=admin_user
            )


class TestValidationChecks:
    """测试验证检查"""
    
    def test_duplicate_unified_social_credit_code(self, db_session, sample_company, test_user):
        """测试重复的统一社会信用代码"""
        service = CompanyService()
        company_in = CompanyCreate(
            name="重复信用代码的企业",
            unified_social_credit_code="91110000123456789X",  # 与sample_company相同
        )
        
        with pytest.raises(ValidationException) as exc_info:
            service.create_company(db=db_session, company_in=company_in, current_user=test_user)
        
        assert "统一社会信用代码已存在" in str(exc_info.value)
    
    def test_duplicate_company_name(self, db_session, sample_company, test_user):
        """测试重复的企业名称"""
        service = CompanyService()
        company_in = CompanyCreate(
            name="测试企业",  # 与sample_company相同
            unified_social_credit_code="91110000999887766A",
        )
        
        with pytest.raises(ValidationException) as exc_info:
            service.create_company(db=db_session, company_in=company_in, current_user=test_user)
        
        assert "企业名称已存在" in str(exc_info.value)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])