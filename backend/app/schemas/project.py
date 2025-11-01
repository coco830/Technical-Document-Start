"""
项目相关的Pydantic模式定义
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ProjectType(str, Enum):
    """项目类型枚举"""
    EMERGENCY_PLAN = "emergency_plan"
    ENVIRONMENTAL_ASSESSMENT = "environmental_assessment"


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    GENERATING = "generating"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectBase(BaseModel):
    """项目基础模式"""
    name: str = Field(..., min_length=1, max_length=200, description="项目名称")
    type: ProjectType = Field(..., description="项目类型")
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="项目状态")
    description: Optional[str] = Field(None, description="项目描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")


class ProjectCreate(ProjectBase):
    """创建项目模式"""
    user_id: int = Field(..., gt=0, description="所属用户ID")
    company_id: Optional[int] = Field(None, gt=0, description="关联企业ID")


class ProjectUpdate(BaseModel):
    """更新项目模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="项目名称")
    type: Optional[ProjectType] = Field(None, description="项目类型")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")
    description: Optional[str] = Field(None, description="项目描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="项目元数据")
    company_id: Optional[int] = Field(None, gt=0, description="关联企业ID")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class Project(ProjectBase):
    """项目完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="项目ID")
    user_id: int = Field(..., description="所属用户ID")
    company_id: Optional[int] = Field(None, description="关联企业ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class ProjectWithDetails(Project):
    """包含详细信息的项目模式"""
    user_name: Optional[str] = Field(None, description="用户名")
    company_name: Optional[str] = Field(None, description="企业名称")
    documents_count: Optional[int] = Field(0, description="文档数量")
    forms_count: Optional[int] = Field(0, description="表单数量")
    progress: Optional[float] = Field(0.0, description="项目进度(0-100)")


class ProjectList(BaseModel):
    """项目列表响应模式"""
    projects: List[ProjectWithDetails] = Field(..., description="项目列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class ProjectFormBase(BaseModel):
    """项目表单基础模式"""
    form_type: str = Field(..., min_length=1, max_length=50, description="表单类型")
    form_data: Dict[str, Any] = Field(..., description="表单数据")


class ProjectFormCreate(ProjectFormBase):
    """创建项目表单模式"""
    project_id: int = Field(..., gt=0, description="所属项目ID")


class ProjectFormUpdate(BaseModel):
    """更新项目表单模式"""
    form_type: Optional[str] = Field(None, min_length=1, max_length=50, description="表单类型")
    form_data: Optional[Dict[str, Any]] = Field(None, description="表单数据")


class ProjectForm(ProjectFormBase):
    """项目表单完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="表单ID")
    project_id: int = Field(..., description="所属项目ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ProjectFormWithDetails(ProjectForm):
    """包含详细信息的项目表单模式"""
    project_name: Optional[str] = Field(None, description="项目名称")
    fields_count: Optional[int] = Field(0, description="字段数量")


class ProjectFormList(BaseModel):
    """项目表单列表响应模式"""
    forms: List[ProjectFormWithDetails] = Field(..., description="表单列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class FormFieldBase(BaseModel):
    """表单字段基础模式"""
    field_name: str = Field(..., min_length=1, max_length=100, description="字段名称")
    field_type: str = Field(..., min_length=1, max_length=50, description="字段类型")
    field_label: str = Field(..., min_length=1, max_length=200, description="字段标签")
    field_config: Optional[Dict[str, Any]] = Field(None, description="字段配置")
    sort_order: int = Field(0, description="排序顺序")
    is_required: bool = Field(False, description="是否必填")


class FormFieldCreate(FormFieldBase):
    """创建表单字段模式"""
    form_id: int = Field(..., gt=0, description="所属表单ID")


class FormFieldUpdate(BaseModel):
    """更新表单字段模式"""
    field_name: Optional[str] = Field(None, min_length=1, max_length=100, description="字段名称")
    field_type: Optional[str] = Field(None, min_length=1, max_length=50, description="字段类型")
    field_label: Optional[str] = Field(None, min_length=1, max_length=200, description="字段标签")
    field_config: Optional[Dict[str, Any]] = Field(None, description="字段配置")
    sort_order: Optional[int] = Field(None, description="排序顺序")
    is_required: Optional[bool] = Field(None, description="是否必填")


class FormField(FormFieldBase):
    """表单字段完整模式"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="字段ID")
    form_id: int = Field(..., description="所属表单ID")


class FormFieldWithDetails(FormField):
    """包含详细信息的表单字段模式"""
    form_type: Optional[str] = Field(None, description="表单类型")
    project_name: Optional[str] = Field(None, description="项目名称")


class FormFieldList(BaseModel):
    """表单字段列表响应模式"""
    fields: List[FormFieldWithDetails] = Field(..., description="字段列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class ProjectTemplate(BaseModel):
    """项目模板模式"""
    id: Optional[int] = Field(None, description="模板ID")
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    type: ProjectType = Field(..., description="项目类型")
    template_data: Dict[str, Any] = Field(..., description="模板数据")
    forms: List[Dict[str, Any]] = Field(..., description="表单模板")
    is_default: bool = Field(False, description="是否为默认模板")
    is_active: bool = Field(True, description="是否启用")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ProjectTemplateCreate(BaseModel):
    """创建项目模板模式"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    type: ProjectType = Field(..., description="项目类型")
    template_data: Dict[str, Any] = Field(..., description="模板数据")
    forms: List[Dict[str, Any]] = Field(..., description="表单模板")
    is_default: bool = Field(False, description="是否为默认模板")


class ProjectTemplateUpdate(BaseModel):
    """更新项目模板模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    template_data: Optional[Dict[str, Any]] = Field(None, description="模板数据")
    forms: Optional[List[Dict[str, Any]]] = Field(None, description="表单模板")
    is_default: Optional[bool] = Field(None, description="是否为默认模板")
    is_active: Optional[bool] = Field(None, description="是否启用")


class ProjectTemplateList(BaseModel):
    """项目模板列表响应模式"""
    templates: List[ProjectTemplate] = Field(..., description="模板列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")


class ProjectStatistics(BaseModel):
    """项目统计模式"""
    total_projects: int = Field(..., description="总项目数")
    active_projects: int = Field(..., description="活跃项目数")
    completed_projects: int = Field(..., description="已完成项目数")
    projects_by_type: Dict[str, int] = Field(..., description="按类型统计项目数")
    projects_by_status: Dict[str, int] = Field(..., description="按状态统计项目数")
    new_projects_today: int = Field(..., description="今日新增项目数")
    new_projects_this_week: int = Field(..., description="本周新增项目数")
    new_projects_this_month: int = Field(..., description="本月新增项目数")
    project_creation_trend: List[Dict[str, Any]] = Field(..., description="项目创建趋势")
    average_completion_time: Optional[float] = Field(None, description="平均完成时间(天)")


class ProjectProgress(BaseModel):
    """项目进度模式"""
    project_id: int = Field(..., description="项目ID")
    total_steps: int = Field(..., description="总步骤数")
    completed_steps: int = Field(..., description="已完成步骤数")
    progress_percentage: float = Field(..., description="进度百分比")
    current_step: Optional[str] = Field(None, description="当前步骤")
    next_step: Optional[str] = Field(None, description="下一步骤")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间")