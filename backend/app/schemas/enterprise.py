"""
企业信息相关的Pydantic模式
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class EnterpriseBasicBase(BaseModel):
    """企业基本信息基础模式"""
    enterprise_name: str = Field(..., description="企业名称", min_length=1, max_length=255)
    address: Optional[str] = Field(None, description="企业地址", max_length=500)
    industry: Optional[str] = Field(None, description="所属行业", max_length=100)
    legal_representative: Optional[str] = Field(None, description="法定代表人", max_length=100)
    contact_phone: Optional[str] = Field(None, description="联系电话", max_length=50)
    fax: Optional[str] = Field(None, description="传真", max_length=50)
    email: Optional[str] = Field(None, description="电子邮箱", max_length=100)
    overview: Optional[str] = Field(None, description="企业概况")
    risk_level: Optional[str] = Field(None, description="风险级别", max_length=50)


class EnvPermitsBase(BaseModel):
    """环保手续信息基础模式"""
    env_assessment_no: Optional[str] = Field(None, description="环评批复编号", max_length=255)
    acceptance_no: Optional[str] = Field(None, description="验收文件编号", max_length=255)
    discharge_permit_no: Optional[str] = Field(None, description="排污许可证编号", max_length=255)
    has_emergency_plan: Optional[str] = Field(None, description="是否有历史应急预案", max_length=10)  # 有/无
    emergency_plan_code: Optional[str] = Field(None, description="历史应急预案编号", max_length=100)  # 仅当有预案时填写


class HazardousMaterialBase(BaseModel):
    """危险化学品基础模式"""
    name: Optional[str] = Field(None, description="化学品名称", max_length=255)
    max_storage: Optional[str] = Field(None, description="最大储存量（吨）", max_length=50)
    annual_usage: Optional[str] = Field(None, description="年使用量（吨）", max_length=50)
    storage_location: Optional[str] = Field(None, description="储存位置", max_length=255)


class EmergencyResourceBase(BaseModel):
    """应急资源基础模式"""
    name: Optional[str] = Field(None, description="物资名称", max_length=255)
    custom_resource_name: Optional[str] = Field(None, description="自定义应急物资名称", max_length=255)
    quantity: Optional[str] = Field(None, description="数量", max_length=100)
    purpose: Optional[str] = Field(None, description="用途", max_length=500)
    storage_location: Optional[str] = Field(None, description="存放地点", max_length=255)
    custodian: Optional[str] = Field(None, description="保管人", max_length=100)
    custodian_contact: Optional[str] = Field(None, description="保管人联系方式", max_length=100)


class EmergencyOrgBase(BaseModel):
    """应急组织基础模式"""
    org_name: Optional[str] = Field(None, description="组织机构名称", max_length=255)
    responsible_person: Optional[str] = Field(None, description="负责人", max_length=100)
    contact_phone: Optional[str] = Field(None, description="联系电话", max_length=50)
    department: Optional[str] = Field(None, description="企业对应部门", max_length=500)
    duty_phone: Optional[str] = Field(None, description="企业24小时值班电话", max_length=50)


class ExternalEmergencyContactBase(BaseModel):
    """外部应急救援通讯方式基础模式"""
    unit_name: Optional[str] = Field(None, description="单位名称", max_length=255)
    contact_method: Optional[str] = Field(None, description="通讯方式", max_length=255)
    custom_contact_method: Optional[str] = Field(None, description="自定义通讯方式", max_length=255)
    custom_unit_name: Optional[str] = Field(None, description="自定义单位名称", max_length=255)


class EnterpriseInfoCreate(BaseModel):
    """企业信息创建模式"""
    enterprise_basic: EnterpriseBasicBase
    env_permits: EnvPermitsBase
    hazardous_materials: List[HazardousMaterialBase] = Field(default_factory=list, description="危险化学品信息列表")
    emergency_resources: List[EmergencyResourceBase] = Field(default_factory=list, description="应急资源信息列表")
    emergency_orgs: List[EmergencyOrgBase] = Field(default_factory=list, description="应急组织信息列表")
    external_emergency_contacts: List[ExternalEmergencyContactBase] = Field(default_factory=list, description="外部应急救援通讯方式列表")
    project_id: Optional[int] = Field(None, description="关联项目ID")

    @validator('enterprise_basic')
    def validate_enterprise_basic(cls, v):
        if not v.enterprise_name:
            raise ValueError('企业名称不能为空')
        return v


class EnterpriseBasicResponse(EnterpriseBasicBase):
    """企业基本信息响应模式"""
    pass


class EnvPermitsResponse(EnvPermitsBase):
    """环保手续信息响应模式"""
    pass


class HazardousMaterialResponse(HazardousMaterialBase):
    """危险化学品响应模式"""
    id: Optional[str] = Field(None, description="ID")


class EmergencyResourceResponse(EmergencyResourceBase):
    """应急资源响应模式"""
    id: Optional[str] = Field(None, description="ID")


class EmergencyOrgResponse(EmergencyOrgBase):
    """应急组织响应模式"""
    id: Optional[str] = Field(None, description="ID")


class ExternalEmergencyContactResponse(ExternalEmergencyContactBase):
    """外部应急救援通讯方式响应模式"""
    id: Optional[str] = Field(None, description="ID")


class EnterpriseInfoResponse(BaseModel):
    """企业信息响应模式"""
    id: int
    user_id: int
    project_id: Optional[int] = None
    enterprise_basic: EnterpriseBasicResponse
    env_permits: EnvPermitsResponse
    hazardous_materials: List[HazardousMaterialResponse] = []
    emergency_resources: List[EmergencyResourceResponse] = []
    emergency_orgs: List[EmergencyOrgResponse] = []
    external_emergency_contacts: List[ExternalEmergencyContactResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EnterpriseInfoUpdate(BaseModel):
    """企业信息更新模式"""
    enterprise_basic: Optional[EnterpriseBasicBase] = None
    env_permits: Optional[EnvPermitsBase] = None
    hazardous_materials: Optional[List[HazardousMaterialBase]] = None
    emergency_resources: Optional[List[EmergencyResourceBase]] = None
    emergency_orgs: Optional[List[EmergencyOrgBase]] = None
    external_emergency_contacts: Optional[List[ExternalEmergencyContactBase]] = None
    project_id: Optional[int] = None


class EnterpriseInfoList(BaseModel):
    """企业信息列表响应模式"""
    enterprise_infos: List[EnterpriseInfoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int