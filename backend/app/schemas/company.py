"""
企业相关的Pydantic模式定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class CompanyBase(BaseModel):
    """企业基础模式"""
    name: str = Field(..., min_length=1, max_length=200, description="企业名称")
    unified_social_credit_code: Optional[str] = Field(None, min_length=18, max_length=18, description="统一社会信用代码")
    legal_representative: Optional[str] = Field(None, max_length=100, description="法定代表人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    address: Optional[str] = Field(None, description="企业地址")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    business_scope: Optional[str] = Field(None, description="经营范围")


class CompanyCreate(CompanyBase):
    """创建企业模式"""
    pass


class CompanyUpdate(BaseModel):
    """更新企业模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="企业名称")
    unified_social_credit_code: Optional[str] = Field(None, min_length=18, max_length=18, description="统一社会信用代码")
    legal_representative: Optional[str] = Field(None, max_length=100, description="法定代表人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    address: Optional[str] = Field(None, description="企业地址")
    industry: Optional[str] = Field(None, max_length=100, description="所属行业")
    business_scope: Optional[str] = Field(None, description="经营范围")


class Company(CompanyBase):
    """企业完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="企业ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class CompanyWithDetails(Company):
    """包含详细信息的企业模式"""
    projects_count: Optional[int] = Field(0, description="项目数量")
    active_projects_count: Optional[int] = Field(0, description="活跃项目数量")
    completed_projects_count: Optional[int] = Field(0, description="已完成项目数量")
    documents_count: Optional[int] = Field(0, description="文档数量")


class CompanyList(BaseModel):
    """企业列表响应模式"""
    companies: List[CompanyWithDetails] = Field(..., description="企业列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class CompanySearch(BaseModel):
    """企业搜索模式"""
    keyword: Optional[str] = Field(None, description="搜索关键词")
    industry: Optional[str] = Field(None, description="所属行业")
    unified_social_credit_code: Optional[str] = Field(None, description="统一社会信用代码")
    legal_representative: Optional[str] = Field(None, description="法定代表人")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    address: Optional[str] = Field(None, description="企业地址")
    created_after: Optional[datetime] = Field(None, description="创建时间起始")
    created_before: Optional[datetime] = Field(None, description="创建时间结束")


class CompanyStatistics(BaseModel):
    """企业统计模式"""
    total_companies: int = Field(..., description="总企业数")
    active_companies: int = Field(..., description="活跃企业数")
    new_companies_today: int = Field(..., description="今日新增企业数")
    new_companies_this_week: int = Field(..., description="本周新增企业数")
    new_companies_this_month: int = Field(..., description="本月新增企业数")
    companies_by_industry: Dict[str, int] = Field(..., description="按行业统计企业数")
    company_registration_trend: List[Dict[str, Any]] = Field(..., description="企业注册趋势")
    top_industries: List[Dict[str, Any]] = Field(..., description="热门行业")


class CompanyVerification(BaseModel):
    """企业验证模式"""
    id: Optional[int] = Field(None, description="验证记录ID")
    company_id: int = Field(..., description="企业ID")
    verification_type: str = Field(..., description="验证类型")
    verification_status: str = Field(..., description="验证状态")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    verified_by: Optional[int] = Field(None, description="验证人ID")
    verified_at: Optional[datetime] = Field(None, description="验证时间")
    notes: Optional[str] = Field(None, description="验证备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class CompanyVerificationCreate(BaseModel):
    """创建企业验证记录模式"""
    company_id: int = Field(..., description="企业ID")
    verification_type: str = Field(..., description="验证类型")
    verification_data: Dict[str, Any] = Field(..., description="验证数据")
    notes: Optional[str] = Field(None, description="验证备注")


class CompanyVerificationUpdate(BaseModel):
    """更新企业验证记录模式"""
    verification_status: str = Field(..., description="验证状态")
    verified_by: Optional[int] = Field(None, description="验证人ID")
    verified_at: Optional[datetime] = Field(None, description="验证时间")
    notes: Optional[str] = Field(None, description="验证备注")


class CompanyVerificationWithDetails(CompanyVerification):
    """包含详细信息的企业验证模式"""
    company_name: Optional[str] = Field(None, description="企业名称")
    verified_by_name: Optional[str] = Field(None, description="验证人姓名")


class CompanyVerificationList(BaseModel):
    """企业验证记录列表响应模式"""
    verifications: List[CompanyVerificationWithDetails] = Field(..., description="验证记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class CompanyDocument(BaseModel):
    """企业文档模式"""
    id: Optional[int] = Field(None, description="文档ID")
    company_id: int = Field(..., description="企业ID")
    document_type: str = Field(..., description="文档类型")
    document_name: str = Field(..., description="文档名称")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., description="文件大小(字节)")
    upload_by: int = Field(..., description="上传人ID")
    is_verified: bool = Field(False, description="是否已验证")
    verified_by: Optional[int] = Field(None, description="验证人ID")
    verified_at: Optional[datetime] = Field(None, description="验证时间")
    notes: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class CompanyDocumentCreate(BaseModel):
    """创建企业文档模式"""
    company_id: int = Field(..., description="企业ID")
    document_type: str = Field(..., description="文档类型")
    document_name: str = Field(..., description="文档名称")
    file_url: str = Field(..., description="文件URL")
    file_size: int = Field(..., description="文件大小(字节)")
    notes: Optional[str] = Field(None, description="备注")


class CompanyDocumentUpdate(BaseModel):
    """更新企业文档模式"""
    document_type: Optional[str] = Field(None, description="文档类型")
    document_name: Optional[str] = Field(None, description="文档名称")
    file_url: Optional[str] = Field(None, description="文件URL")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    is_verified: Optional[bool] = Field(None, description="是否已验证")
    verified_by: Optional[int] = Field(None, description="验证人ID")
    verified_at: Optional[datetime] = Field(None, description="验证时间")
    notes: Optional[str] = Field(None, description="备注")


class CompanyDocumentWithDetails(CompanyDocument):
    """包含详细信息的企业文档模式"""
    company_name: Optional[str] = Field(None, description="企业名称")
    upload_by_name: Optional[str] = Field(None, description="上传人姓名")
    verified_by_name: Optional[str] = Field(None, description="验证人姓名")


class CompanyDocumentList(BaseModel):
    """企业文档列表响应模式"""
    documents: List[CompanyDocumentWithDetails] = Field(..., description="文档列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class CompanyContact(BaseModel):
    """企业联系人模式"""
    id: Optional[int] = Field(None, description="联系人ID")
    company_id: int = Field(..., description="企业ID")
    name: str = Field(..., description="联系人姓名")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    is_primary: bool = Field(False, description="是否主要联系人")
    is_active: bool = Field(True, description="是否活跃")
    notes: Optional[str] = Field(None, description="备注")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class CompanyContactCreate(BaseModel):
    """创建企业联系人模式"""
    company_id: int = Field(..., description="企业ID")
    name: str = Field(..., description="联系人姓名")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    is_primary: bool = Field(False, description="是否主要联系人")
    notes: Optional[str] = Field(None, description="备注")


class CompanyContactUpdate(BaseModel):
    """更新企业联系人模式"""
    name: Optional[str] = Field(None, description="联系人姓名")
    position: Optional[str] = Field(None, description="职位")
    phone: Optional[str] = Field(None, description="电话")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")
    is_primary: Optional[bool] = Field(None, description="是否主要联系人")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    notes: Optional[str] = Field(None, description="备注")


class CompanyContactWithDetails(CompanyContact):
    """包含详细信息的企业联系人模式"""
    company_name: Optional[str] = Field(None, description="企业名称")


class CompanyContactList(BaseModel):
    """企业联系人列表响应模式"""
    contacts: List[CompanyContactWithDetails] = Field(..., description="联系人列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")