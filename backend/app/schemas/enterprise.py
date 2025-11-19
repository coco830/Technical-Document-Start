"""
企业信息相关的Pydantic模式
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class EnterpriseIdentityBase(BaseModel):
    """企业身份信息基础模式"""
    enterprise_name: str = Field(..., description="企业名称（全称）", min_length=1, max_length=255)
    unified_social_credit_code: Optional[str] = Field(None, description="统一社会信用代码", max_length=50)
    group_company: Optional[str] = Field(None, description="所属集团/母公司（选填）", max_length=255)
    industry: Optional[str] = Field(None, description="所在行业", max_length=100)
    industry_subdivision: Optional[str] = Field(None, description="行业细分说明")
    park_name: Optional[str] = Field(None, description="所在园区/工业区名称（选填）", max_length=255)
    risk_level: Optional[str] = Field(None, description="企业风险级别（一般/较大/重大）", max_length=50)


class EnterpriseAddressBase(BaseModel):
    """地址与空间信息基础模式"""
    province: Optional[str] = Field(None, description="所在省", max_length=100)
    city: Optional[str] = Field(None, description="所在市", max_length=100)
    district: Optional[str] = Field(None, description="所在区/县", max_length=100)
    detailed_address: Optional[str] = Field(None, description="详细地址", max_length=500)
    postal_code: Optional[str] = Field(None, description="邮编", max_length=20)
    fax: Optional[str] = Field(None, description="传真", max_length=50)
    longitude: Optional[str] = Field(None, description="企业中心点经度（WGS84）", max_length=50)
    latitude: Optional[str] = Field(None, description="企业中心点纬度（WGS84）", max_length=50)


class EnterpriseContactsBase(BaseModel):
    """联系人与职责基础模式"""
    legal_representative_name: Optional[str] = Field(None, description="法定代表人姓名", max_length=100)
    legal_representative_phone: Optional[str] = Field(None, description="法定代表人手机", max_length=50)
    env_officer_name: Optional[str] = Field(None, description="环保负责人姓名", max_length=100)
    env_officer_position: Optional[str] = Field(None, description="环保负责人职务/部门", max_length=100)
    env_officer_phone: Optional[str] = Field(None, description="环保负责人手机", max_length=50)
    emergency_contact_name: Optional[str] = Field(None, description="应急联系人姓名", max_length=100)
    emergency_contact_position: Optional[str] = Field(None, description="应急联系人职务", max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, description="应急联系人手机", max_length=50)
    landline_phone: Optional[str] = Field(None, description="固定电话（总机或值班电话）", max_length=50)
    enterprise_email: Optional[str] = Field(None, description="企业联系邮箱", max_length=100)


class EnterpriseOperationBase(BaseModel):
    """企业运营概况基础模式"""
    establishment_date: Optional[str] = Field(None, description="成立时间（年月）", max_length=50)
    production_date: Optional[str] = Field(None, description="建成/投产时间（年月，选填）", max_length=50)
    production_status: Optional[str] = Field(None, description="企业在产状态（在产/停产/在建改扩建）", max_length=50)
    total_employees: Optional[int] = Field(None, description="员工总数（人）")
    production_staff: Optional[int] = Field(None, description="生产人员数量（人）")
    management_staff: Optional[int] = Field(None, description="管理及后勤人员数量（人，可选）")
    shift_system: Optional[str] = Field(None, description="班制（单班/两班/三班/其它）", max_length=50)
    daily_work_hours: Optional[str] = Field(None, description="日工作时间（小时/班）", max_length=50)
    annual_work_days: Optional[int] = Field(None, description="年运行天数（d/a）")
    land_area: Optional[int] = Field(None, description="占地面积（m²）")
    building_area: Optional[int] = Field(None, description="总建筑面积（m²）")
    total_investment: Optional[int] = Field(None, description="总投资额（万元）")
    env_investment: Optional[int] = Field(None, description="环保投资额（万元，选填）")
    business_types: Optional[list] = Field(None, description="主要业务/服务类型（多选+补充说明）")


class EnterpriseIntroBase(BaseModel):
    """企业简介文本基础模式"""
    enterprise_intro: Optional[str] = Field(None, description="企业简介原文（多行文本）")


# 步骤2：生产过程与风险物质 - 2.1 产品与产能
class ProductInfoBase(BaseModel):
    """产品信息基础模式"""
    product_name: Optional[str] = Field(None, description="产品名称")
    product_type: Optional[str] = Field(None, description="产品类型（主产品/副产品/中间产品/副产物/公用工程）")
    design_capacity: Optional[str] = Field(None, description="设计产能（单位+数值）")
    actual_annual_output: Optional[str] = Field(None, description="实际年产量（最近一年）")


# 步骤2：生产过程与风险物质 - 2.2 原辅料与能源
class RawMaterialInfoBase(BaseModel):
    """原辅材料信息基础模式"""
    material_name: Optional[str] = Field(None, description="物料名称")
    cas_number: Optional[str] = Field(None, description="CAS号（选填）")
    material_category: Optional[str] = Field(None, description="物料类别（原料/辅料/包装材料/催化剂等）")
    is_hazardous: Optional[str] = Field(None, description="是否危险化学品（是/否）")
    hazard_categories: Optional[list] = Field(None, description="危险性类别（易燃液体/有毒/腐蚀性/氧化剂/气体等，多选）")
    annual_usage: Optional[str] = Field(None, description="年使用量（t/a或其他）")
    max_inventory: Optional[str] = Field(None, description="企业内最大同时存量（t或m³）")
    main_process_equipment: Optional[str] = Field(None, description="主要使用工序/设备")
    material_phase: Optional[str] = Field(None, description="物相（气/液/固）")


class EnergyUsageBase(BaseModel):
    """能源使用情况基础模式"""
    water_usage: Optional[str] = Field(None, description="年总用水量（m³/a）")
    industrial_water: Optional[str] = Field(None, description="工业用水（m³/a）")
    domestic_water: Optional[str] = Field(None, description="生活用水（m³/a）")
    electricity_usage: Optional[str] = Field(None, description="年用电量（万kWh/a）")
    other_energy: Optional[list] = Field(None, description="其他能源（天然气、蒸汽、煤、柴油等：类型+年用量）")


# 步骤2：生产过程与风险物质 - 2.3 生产工艺与工序
class ProductionProcessBase(BaseModel):
    """生产工艺与工序基础模式"""
    process_type: Optional[str] = Field(None, description="工艺类型（连续/间歇/混合）")
    process_description: Optional[str] = Field(None, description="总体工艺简述（多行文本）")
    process_flow_file: Optional[str] = Field(None, description="工艺流程图文件（上传文件ID）")
    process_nodes: Optional[list] = Field(None, description="工序节点列表")


class ProcessNodeBase(BaseModel):
    """工序节点基础模式"""
    node_name: Optional[str] = Field(None, description="工序/工段名称")
    node_function: Optional[str] = Field(None, description="工序功能简述")
    key_equipment: Optional[str] = Field(None, description="关键设备名称")
    involves_hazardous: Optional[str] = Field(None, description="是否涉及危险化学品（是/否）")


# 步骤2：生产过程与风险物质 - 2.4 储存与装卸设施
class StorageFacilityBase(BaseModel):
    """储存单元基础模式"""
    facility_name: Optional[str] = Field(None, description="储存单元名称（如'危化品库房1''柴油罐区'）")
    facility_type: Optional[str] = Field(None, description="储存设施类型（库房/地上罐/地下罐/气瓶/危废暂存间等）")
    main_materials: Optional[list] = Field(None, description="主要储存物质（可多选/多条）")
    rated_capacity: Optional[str] = Field(None, description="单设施额定容量（t/m³/套）")
    max_inventory: Optional[str] = Field(None, description="最大实际库存（t/m³）")
    storage_method: Optional[str] = Field(None, description="储存方式（室内/室外；地上/地下）")
    has_bund: Optional[str] = Field(None, description="有无围堰或事故池（是/否）")
    anti_seep_measures: Optional[str] = Field(None, description="防渗措施描述（混凝土+防渗层/双层罐等）")
    location_description: Optional[str] = Field(None, description="所在厂区位置描述（如'东侧危化品库区'）")


class LoadingOperationBase(BaseModel):
    """装卸作业信息基础模式"""
    has_loading: Optional[str] = Field(None, description="是否存在物料装卸作业（是/否）")
    main_materials: Optional[list] = Field(None, description="主要装卸物料")
    loading_area_location: Optional[str] = Field(None, description="装卸区域名称与位置描述")
    leak_prevention: Optional[str] = Field(None, description="是否设置地面截流/集水井/抛洒收集等防泄漏设施（选择+说明）")


# 步骤2：生产过程与风险物质 - 2.5 危险化学品明细
class HazardousChemicalBase(BaseModel):
    """危险化学品明细基础模式"""
    chemical_name: Optional[str] = Field(None, description="物质名称")
    cas_number: Optional[str] = Field(None, description="CAS号")
    hazard_category: Optional[str] = Field(None, description="危险性类别（国标分类，下拉）")
    location_unit: Optional[str] = Field(None, description="所在工艺单元/储存单元")
    max_inventory: Optional[str] = Field(None, description="最大存量（t）")
    critical_quantity: Optional[str] = Field(None, description="临界量（t，可不让用户填，由后台字典算）")
    material_phase: Optional[str] = Field(None, description="物相（气/液/固）")
    is_major_hazard: Optional[str] = Field(None, description="是否构成重大危险源（是/否/自动计算后回填）")
    msds_file: Optional[str] = Field(None, description="MSDS文件（上传）")


# 步骤2：生产过程与风险物质 - 2.6 危险废物与其他风险物质
class HazardousWasteBase(BaseModel):
    """危险废物与其他风险物质基础模式"""
    waste_name: Optional[str] = Field(None, description="危险废物名称")
    waste_category: Optional[str] = Field(None, description="危废类别（如HW01、HW08）")
    waste_code: Optional[str] = Field(None, description="危险废物代码")
    source_process: Optional[str] = Field(None, description="主要来源工序/设备")
    hazard_characteristics: Optional[list] = Field(None, description="危险特性（毒性/易燃/腐蚀/反应性等，多选）")
    storage_location: Optional[str] = Field(None, description="暂存地点名称")
    storage_method: Optional[str] = Field(None, description="暂存方式（危废间/容器/贮罐等）")
    max_storage: Optional[str] = Field(None, description="最大暂存量（t）")
    max_storage_days: Optional[str] = Field(None, description="最长暂存时间（d）")
    disposal_company: Optional[str] = Field(None, description="委外处置单位名称")


# 步骤3：环境信息 - 3.1 自然与功能区信息
class NaturalFunctionZoneBase(BaseModel):
    """自然与功能区信息基础模式"""
    administrative_division_code: Optional[str] = Field(None, description="行政区划代码", max_length=50)
    water_environment_function_zone: Optional[str] = Field(None, description="所属水环境功能区", max_length=255)
    atmospheric_environment_function_zone: Optional[str] = Field(None, description="所属大气环境功能区类别", max_length=255)
    watershed_name: Optional[str] = Field(None, description="所在流域名称", max_length=255)
    nearest_surface_water_body: Optional[str] = Field(None, description="最近地表水体名称", max_length=255)
    distance_to_surface_water: Optional[str] = Field(None, description="最近地表水体与厂界最短距离", max_length=50)
    surface_water_direction: Optional[str] = Field(None, description="最近地表水体相对方位", max_length=100)


# 步骤3：环境信息 - 3.2 周边环境风险受体
class EnvironmentalRiskReceptorBase(BaseModel):
    """周边环境风险受体基础模式"""
    environment_element: Optional[str] = Field(None, description="环境要素")
    receptor_type: Optional[str] = Field(None, description="受体类型")
    receptor_name: Optional[str] = Field(None, description="受体名称")
    relative_direction: Optional[str] = Field(None, description="相对方位")
    distance_to_boundary: Optional[str] = Field(None, description="距离厂界最近点距离")
    function_and_scale: Optional[str] = Field(None, description="功能与规模")
    environmental_quality_target: Optional[str] = Field(None, description="环境质量目标")


# 步骤3：环境信息 - 3.3 废水产生与治理
class WastewaterTreatmentFacilityBase(BaseModel):
    """废水处理设施基础模式"""
    facility_name: Optional[str] = Field(None, description="设施名称")
    service_scope: Optional[str] = Field(None, description="主要服务范围")
    process_type: Optional[str] = Field(None, description="工艺类型")
    design_capacity: Optional[str] = Field(None, description="设计处理规模")
    actual_treatment_volume: Optional[str] = Field(None, description="实际平均处理量")
    discharge_destination: Optional[str] = Field(None, description="出水去向")
    has_accident_pool: Optional[str] = Field(None, description="是否设置事故池")
    accident_pool_volume: Optional[str] = Field(None, description="事故池有效容积")


class WastewaterOutletBase(BaseModel):
    """废水排口基础模式"""
    outlet_id: Optional[str] = Field(None, description="排口编号/名称")
    outlet_type: Optional[str] = Field(None, description="排口类型")
    discharge_destination: Optional[str] = Field(None, description="排放去向")
    has_online_monitoring: Optional[str] = Field(None, description="是否安装在线监测")


class WastewaterManagementBase(BaseModel):
    """废水产生与治理基础模式"""
    drainage_system: Optional[str] = Field(None, description="排水体制", max_length=100)
    has_production_wastewater: Optional[str] = Field(None, description="是否存在生产废水", max_length=10)
    has_domestic_sewage: Optional[str] = Field(None, description="是否存在生活污水", max_length=10)
    wastewater_treatment_facilities: Optional[List[WastewaterTreatmentFacilityBase]] = Field(default_factory=list, description="废水处理设施列表")
    wastewater_outlets: Optional[List[WastewaterOutletBase]] = Field(default_factory=list, description="废水排口列表")


# 步骤3：环境信息 - 3.4 废气产生与治理
class OrganizedWasteGasSourceBase(BaseModel):
    """有组织废气源基础模式"""
    source_name: Optional[str] = Field(None, description="废气源名称/编号")
    corresponding_process: Optional[str] = Field(None, description="对应工段或设备")
    main_pollutants: Optional[str] = Field(None, description="主要污染物")
    treatment_facility_type: Optional[str] = Field(None, description="处理设施类型")
    stack_number: Optional[str] = Field(None, description="排气筒编号")
    stack_height: Optional[str] = Field(None, description="排气筒高度")
    discharge_destination: Optional[str] = Field(None, description="排放去向")
    has_online_monitoring: Optional[str] = Field(None, description="是否在线监测")


class UnorganizedWasteGasBase(BaseModel):
    """无组织废气源概况基础模式"""
    has_obvious_unorganized_gas: Optional[str] = Field(None, description="是否存在明显无组织废气")
    main_emission_areas: Optional[str] = Field(None, description="主要无组织排放区域")
    existing_control_measures: Optional[str] = Field(None, description="现有控制措施")


class WasteGasManagementBase(BaseModel):
    """废气产生与治理基础模式"""
    organized_waste_gas_sources: Optional[List[OrganizedWasteGasSourceBase]] = Field(default_factory=list, description="有组织废气源列表")
    unorganized_waste_gas: Optional[UnorganizedWasteGasBase] = Field(None, description="无组织废气源概况")


# 步骤3：环境信息 - 3.5 噪声与固体废物
class NoiseSourceBase(BaseModel):
    """主要噪声源基础模式"""
    noise_source_name: Optional[str] = Field(None, description="噪声源名称/设备")
    location: Optional[str] = Field(None, description="位置")
    noise_control_measures: Optional[str] = Field(None, description="噪声控制措施")


class GeneralSolidWasteBase(BaseModel):
    """一般固废基础模式"""
    waste_name: Optional[str] = Field(None, description="固废名称")
    source_process: Optional[str] = Field(None, description="来源工序")
    nature: Optional[str] = Field(None, description="性质")
    annual_generation: Optional[str] = Field(None, description="年产生量")
    storage_method: Optional[str] = Field(None, description="暂存方式")
    disposal_method: Optional[str] = Field(None, description="处置方式")
    destination_unit: Optional[str] = Field(None, description="去向单位")


class NoiseAndSolidWasteBase(BaseModel):
    """噪声与固体废物基础模式"""
    main_noise_sources: Optional[List[NoiseSourceBase]] = Field(default_factory=list, description="主要噪声源列表")
    general_solid_wastes: Optional[List[GeneralSolidWasteBase]] = Field(default_factory=list, description="一般固废列表")


# 步骤3：环境信息 - 3.6 事故防控设施
class AccidentPreventionFacilitiesBase(BaseModel):
    """事故防控设施基础模式"""
    has_rain_sewage_diversion: Optional[str] = Field(None, description="是否设置事故雨污分流及切换设施", max_length=10)
    rain_sewage_diversion_description: Optional[str] = Field(None, description="事故雨污分流描述")
    has_key_area_bunds: Optional[str] = Field(None, description="是否设置重点区域围堰", max_length=10)
    bunds_location: Optional[str] = Field(None, description="围堰位置", max_length=255)
    hazardous_chemicals_warehouse_seepage: Optional[str] = Field(None, description="危险化学品库/危废间防渗结构说明")
    key_valves_and_shutoff_facilities: Optional[str] = Field(None, description="关键阀门与切断设施说明")


# 步骤4：环保手续与管理制度

# 4.1 环保手续（证照）- 环评文件
class EIAFileBase(BaseModel):
    """环评文件基础模式"""
    eia_project_name: Optional[str] = Field(None, description="环评项目名称", max_length=255)
    eia_document_number: Optional[str] = Field(None, description="环评文号", max_length=255)
    eia_approval_date: Optional[str] = Field(None, description="批复日期", max_length=50)
    eia_consistency_status: Optional[str] = Field(None, description="与现状一致性", max_length=100)
    eia_report_upload: Optional[str] = Field(None, description="环评报告/报告表上传", max_length=255)
    eia_approval_upload: Optional[str] = Field(None, description="环评批复文件上传", max_length=255)


# 4.1 环保手续（证照）- 竣工环保验收
class EnvironmentalAcceptanceBase(BaseModel):
    """竣工环保验收基础模式"""
    acceptance_type: Optional[str] = Field(None, description="验收类别", max_length=100)
    acceptance_document_number: Optional[str] = Field(None, description="验收文号", max_length=255)
    acceptance_date: Optional[str] = Field(None, description="验收日期", max_length=50)
    acceptance_report_upload: Optional[str] = Field(None, description="验收报告上传", max_length=255)
    acceptance_approval_upload: Optional[str] = Field(None, description="验收批复上传", max_length=255)


# 4.1 环保手续（证照）- 排污许可证
class DischargePermitBase(BaseModel):
    """排污许可证基础模式"""
    discharge_permit_number: Optional[str] = Field(None, description="排污许可证编号", max_length=255)
    issuing_authority: Optional[str] = Field(None, description="发证机关", max_length=255)
    permit_start_date: Optional[str] = Field(None, description="有效期起始日期", max_length=50)
    permit_end_date: Optional[str] = Field(None, description="有效期截止日期", max_length=50)
    permitted_pollutants: Optional[str] = Field(None, description="许可排放的主要污染物")
    permit_scan_upload: Optional[str] = Field(None, description="证书扫描件上传", max_length=255)


# 4.1 环保手续（证照）- 其他环保相关许可证
class OtherEnvCertificateBase(BaseModel):
    """其他环保相关许可证基础模式"""
    certificate_type: Optional[str] = Field(None, description="证书类型")
    certificate_number: Optional[str] = Field(None, description="证书编号")
    certificate_issuing_authority: Optional[str] = Field(None, description="发证机关")
    certificate_validity_period: Optional[str] = Field(None, description="有效期")
    certificate_scan_upload: Optional[str] = Field(None, description="扫描件上传")


# 4.2 危险废物/医废处置协议 - 危废处置协议
class HazardousWasteAgreementBase(BaseModel):
    """危废处置协议基础模式"""
    hazardous_waste_agreement_unit: Optional[str] = Field(None, description="协议单位名称", max_length=255)
    hazardous_waste_unit_permit_number: Optional[str] = Field(None, description="单位许可证编号", max_length=255)
    hazardous_waste_agreement_start_date: Optional[str] = Field(None, description="协议起始日期", max_length=50)
    hazardous_waste_agreement_end_date: Optional[str] = Field(None, description="协议结束日期", max_length=50)
    hazardous_waste_categories: Optional[str] = Field(None, description="涉及危废类别")
    hazardous_waste_agreement_upload: Optional[str] = Field(None, description="协议扫描件上传", max_length=255)


# 4.2 危险废物/医废处置协议 - 医疗废物处置协议
class MedicalWasteAgreementBase(BaseModel):
    """医疗废物处置协议基础模式"""
    medical_waste_agreement_unit: Optional[str] = Field(None, description="协议单位名称", max_length=255)
    medical_waste_unit_permit_number: Optional[str] = Field(None, description="单位许可证编号", max_length=255)
    medical_waste_agreement_start_date: Optional[str] = Field(None, description="协议起始日期", max_length=50)
    medical_waste_agreement_end_date: Optional[str] = Field(None, description="协议结束日期", max_length=50)
    medical_waste_categories: Optional[str] = Field(None, description="涉及医废类别")
    medical_waste_agreement_upload: Optional[str] = Field(None, description="协议扫描件上传", max_length=255)


# 4.3 环境应急预案备案情况
class EmergencyPlanFilingBase(BaseModel):
    """环境应急预案备案情况基础模式"""
    has_emergency_plan: Optional[str] = Field(None, description="是否已编制突发环境事件应急预案", max_length=10)
    has_emergency_plan_filed: Optional[str] = Field(None, description="是否已备案", max_length=10)
    emergency_plan_filing_number: Optional[str] = Field(None, description="备案编号", max_length=255)
    emergency_plan_filing_date: Optional[str] = Field(None, description="备案日期", max_length=50)
    emergency_plan_filing_upload: Optional[str] = Field(None, description="备案回执/备案表上传", max_length=255)


# 4.4 管理制度与处罚记录 - 管理制度情况
class ManagementSystemBase(BaseModel):
    """管理制度情况基础模式"""
    has_risk_inspection_system: Optional[str] = Field(None, description="是否建立环境风险隐患排查制度", max_length=10)
    has_hazardous_chemicals_management_system: Optional[str] = Field(None, description="是否建立危险化学品安全管理制度", max_length=10)
    has_hazardous_waste_management_system: Optional[str] = Field(None, description="是否建立危险废物管理制度", max_length=10)
    has_emergency_drill_training_system: Optional[str] = Field(None, description="是否建立应急演练及培训制度", max_length=10)
    management_system_files_upload: Optional[str] = Field(None, description="相关制度文件打包上传", max_length=255)


# 4.4 管理制度与处罚记录 - 近三年行政处罚/事故记录
class PenaltyAccidentRecordBase(BaseModel):
    """近三年行政处罚/事故记录基础模式"""
    has_administrative_penalty: Optional[str] = Field(None, description="近三年是否受到生态环境部门行政处罚", max_length=10)
    administrative_penalty_details: Optional[str] = Field(None, description="处罚日期、处罚决定文号、主要违法事实、整改情况")
    has_environmental_accident: Optional[str] = Field(None, description="近三年是否有较大及以上环境事故", max_length=10)
    environmental_accident_details: Optional[str] = Field(None, description="简要说明，用于风险等级调整和案例编写")


# 步骤4：环保手续与管理制度整体
class EnvironmentalPermitsAndManagementBase(BaseModel):
    """环保手续与管理制度基础模式"""
    # 4.1 环保手续（证照）
    eia_file: Optional[EIAFileBase] = Field(None, description="环评文件")
    environmental_acceptance: Optional[EnvironmentalAcceptanceBase] = Field(None, description="竣工环保验收")
    discharge_permit: Optional[DischargePermitBase] = Field(None, description="排污许可证")
    other_env_certificates: Optional[List[OtherEnvCertificateBase]] = Field(default_factory=list, description="其他环保相关许可证")
    
    # 4.2 危险废物/医废处置协议
    hazardous_waste_agreement: Optional[HazardousWasteAgreementBase] = Field(None, description="危废处置协议")
    medical_waste_agreement: Optional[MedicalWasteAgreementBase] = Field(None, description="医疗废物处置协议")
    
    # 4.3 环境应急预案备案情况
    emergency_plan_filing: Optional[EmergencyPlanFilingBase] = Field(None, description="环境应急预案备案情况")
    
    # 4.4 管理制度与处罚记录
    management_system: Optional[ManagementSystemBase] = Field(None, description="管理制度情况")
    penalty_accident_record: Optional[PenaltyAccidentRecordBase] = Field(None, description="近三年行政处罚/事故记录")


# 步骤5：应急管理与资源

# 5.1 应急组织机构与联络方式
class InternalEmergencyContactBase(BaseModel):
    """内部应急通讯录基础模式"""
    organization_role: Optional[str] = Field(None, description="组织机构角色")
    department_name: Optional[str] = Field(None, description="对应部门名称")
    contact_name: Optional[str] = Field(None, description="姓名")
    position: Optional[str] = Field(None, description="职务")
    phone_number: Optional[str] = Field(None, description="手机号")


class ExternalEmergencyUnitContactBase(BaseModel):
    """外部应急单位联系方式基础模式"""
    unit_category: Optional[str] = Field(None, description="单位类别")
    unit_name: Optional[str] = Field(None, description="单位名称")
    contact_phone: Optional[str] = Field(None, description="联系电话")
    emergency_capability_description: Optional[str] = Field(None, description="主要应急能力说明")
    has_cooperation_agreement: Optional[str] = Field(None, description="是否签订互助/协议")


class EmergencyOrganizationAndContactsBase(BaseModel):
    """应急组织机构与联络方式基础模式"""
    enterprise_24h_duty_phone: Optional[str] = Field(None, description="企业24小时值班电话", max_length=50)
    internal_emergency_contacts: Optional[List[InternalEmergencyContactBase]] = Field(default_factory=list, description="内部应急通讯录，动态数组")
    external_emergency_unit_contacts: Optional[List[ExternalEmergencyUnitContactBase]] = Field(default_factory=list, description="外部应急单位联系方式，动态数组")


# 5.2 应急物资与装备
class EmergencyMaterialBase(BaseModel):
    """自储应急物资清单基础模式"""
    material_name: Optional[str] = Field(None, description="名称")
    unit: Optional[str] = Field(None, description="单位")
    quantity: Optional[str] = Field(None, description="数量")
    purpose: Optional[list] = Field(None, description="用途，多选")
    storage_location: Optional[str] = Field(None, description="存放地点")
    custodian_name: Optional[str] = Field(None, description="保管人姓名")
    custodian_phone: Optional[str] = Field(None, description="保管人电话")


class EmergencyFacilitiesBase(BaseModel):
    """关键应急设施基础模式"""
    emergency_warehouse_count: Optional[int] = Field(None, description="应急物资专用仓库数量")
    warehouse_total_area: Optional[int] = Field(None, description="应急物资仓库总面积")
    has_accident_pool: Optional[str] = Field(None, description="事故应急池是否存在", max_length=10)
    accident_pool_volume: Optional[str] = Field(None, description="事故池有效容积", max_length=50)
    emergency_vehicles: Optional[dict] = Field(None, description="应急车辆数量及类型")


class EmergencyMaterialsAndEquipmentBase(BaseModel):
    """应急物资与装备基础模式"""
    emergency_materials_list: Optional[List[EmergencyMaterialBase]] = Field(default_factory=list, description="自储应急物资清单，动态数组")
    emergency_facilities: Optional[EmergencyFacilitiesBase] = Field(None, description="关键应急设施")


# 5.3 应急队伍与保障
class EmergencyTeamAndSupportBase(BaseModel):
    """应急队伍与保障基础模式"""
    has_internal_rescue_team: Optional[str] = Field(None, description="是否建立企业内部应急救援队伍", max_length=10)
    rescue_team_size: Optional[int] = Field(None, description="应急队伍人数")
    team_composition_description: Optional[str] = Field(None, description="队伍构成说明")
    has_emergency_budget: Optional[str] = Field(None, description="是否有应急经费专项预算", max_length=10)
    annual_emergency_budget: Optional[str] = Field(None, description="年度应急经费预算额度", max_length=50)


# 5.4 演练与培训记录
class DrillRecordBase(BaseModel):
    """演练记录基础模式"""
    drill_date: Optional[str] = Field(None, description="演练日期")
    drill_type: Optional[str] = Field(None, description="演练类型")
    simulated_event_type: Optional[str] = Field(None, description="模拟事件类型")
    participating_departments: Optional[str] = Field(None, description="主要参与部门/单位")
    drill_records_upload: Optional[str] = Field(None, description="演练记录或照片上传")


class EmergencyDrillsBase(BaseModel):
    """应急演练基础模式"""
    has_conducted_drills: Optional[str] = Field(None, description="最近三年是否开展应急演练", max_length=10)
    drill_records: Optional[List[DrillRecordBase]] = Field(default_factory=list, description="演练记录列表，动态数组")


class EmergencyTrainingBase(BaseModel):
    """应急与环保培训基础模式"""
    annual_emergency_training_count: Optional[int] = Field(None, description="年度应急培训次数")
    annual_environmental_training_count: Optional[int] = Field(None, description="年度环保培训次数")
    employee_coverage_rate: Optional[str] = Field(None, description="职工覆盖率", max_length=50)
    includes_hazardous_chemicals_safety: Optional[str] = Field(None, description="是否包含危化品安全和环境应急内容", max_length=10)


class DrillsAndTrainingRecordsBase(BaseModel):
    """演练与培训记录基础模式"""
    emergency_drills: Optional[EmergencyDrillsBase] = Field(None, description="应急演练")
    emergency_training: Optional[EmergencyTrainingBase] = Field(None, description="应急与环保培训")


# 5.5 应急资源调查元数据
class EmergencyResourceSurveyMetadataBase(BaseModel):
    """应急资源调查元数据基础模式"""
    emergency_resource_survey_year: Optional[str] = Field(None, description="本次应急资源调查基准年份", max_length=10)
    survey_start_date: Optional[str] = Field(None, description="调查工作开始日期", max_length=50)
    survey_end_date: Optional[str] = Field(None, description="调查工作结束日期", max_length=50)
    survey_leader_name: Optional[str] = Field(None, description="调查负责人姓名", max_length=100)
    survey_contact_phone: Optional[str] = Field(None, description="调查联系人及电话", max_length=50)


class EnterpriseBasicBase(BaseModel):
    """企业基本信息基础模式（兼容性）"""
    # 保持原有字段以确保兼容性
    enterprise_name: Optional[str] = Field(None, description="企业名称", max_length=255)
    organization_code: Optional[str] = Field(None, description="组织机构代码", max_length=100)
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


class EnvManagementBase(BaseModel):
    """环境管理制度基础模式"""
    env_management_system: Optional[str] = Field(None, description="环境管理体系认证", max_length=50)
    env_officer: Optional[str] = Field(None, description="环保负责人", max_length=100)


class EnvReceptorBase(BaseModel):
    """环境受体基础模式"""
    population_density: Optional[str] = Field(None, description="周边人口密度", max_length=255)
    sensitive_distance: Optional[str] = Field(None, description="敏感目标距离", max_length=255)


class EnvPollutantBase(BaseModel):
    """污染物基础模式"""
    main_pollutants: Optional[str] = Field(None, description="主要污染物类型", max_length=255)
    discharge_method: Optional[str] = Field(None, description="排放方式", max_length=255)


class EnvPreventionBase(BaseModel):
    """防控设施基础模式"""
    wastewater_facility: Optional[str] = Field(None, description="废水处理设施", max_length=255)
    waste_gas_facility: Optional[str] = Field(None, description="废气处理设施", max_length=255)


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
    # 企业基本信息 - 5个小表块
    enterprise_identity: Optional[EnterpriseIdentityBase] = Field(None, description="企业身份信息")
    enterprise_address: Optional[EnterpriseAddressBase] = Field(None, description="地址与空间信息")
    enterprise_contacts: Optional[EnterpriseContactsBase] = Field(None, description="联系人与职责")
    enterprise_operation: Optional[EnterpriseOperationBase] = Field(None, description="企业运营概况")
    enterprise_intro: Optional[EnterpriseIntroBase] = Field(None, description="企业简介文本")
    
    # 步骤2：生产过程与风险物质 - 6个小表块
    products_info: Optional[List[ProductInfoBase]] = Field(default_factory=list, description="产品列表信息")
    raw_materials_info: Optional[List[RawMaterialInfoBase]] = Field(default_factory=list, description="原辅材料列表信息")
    energy_usage: Optional[EnergyUsageBase] = Field(None, description="能源使用情况信息")
    production_process: Optional[ProductionProcessBase] = Field(None, description="生产工艺与工序信息")
    storage_facilities: Optional[List[StorageFacilityBase]] = Field(default_factory=list, description="储存单元列表信息")
    loading_operations: Optional[LoadingOperationBase] = Field(None, description="装卸作业信息")
    hazardous_chemicals: Optional[List[HazardousChemicalBase]] = Field(default_factory=list, description="危险化学品明细信息")
    hazardous_waste: Optional[List[HazardousWasteBase]] = Field(default_factory=list, description="危险废物与其他风险物质信息")
    
    # 步骤3：环境信息 - 6个小表块
    natural_function_zone: Optional[NaturalFunctionZoneBase] = Field(None, description="自然与功能区信息")
    environmental_risk_receptors: Optional[List[EnvironmentalRiskReceptorBase]] = Field(default_factory=list, description="周边环境风险受体")
    wastewater_management: Optional[WastewaterManagementBase] = Field(None, description="废水产生与治理")
    waste_gas_management: Optional[WasteGasManagementBase] = Field(None, description="废气产生与治理")
    noise_and_solid_waste: Optional[NoiseAndSolidWasteBase] = Field(None, description="噪声与固体废物")
    accident_prevention_facilities: Optional[AccidentPreventionFacilitiesBase] = Field(None, description="事故防控设施")
    
    # 步骤4：环保手续与管理制度
    environmental_permits_and_management: Optional[EnvironmentalPermitsAndManagementBase] = Field(None, description="环保手续与管理制度")
    
    # 步骤5：应急管理与资源
    emergency_organization_and_contacts: Optional[EmergencyOrganizationAndContactsBase] = Field(None, description="应急组织机构与联络方式")
    emergency_materials_and_equipment: Optional[EmergencyMaterialsAndEquipmentBase] = Field(None, description="应急物资与装备")
    emergency_team_and_support: Optional[EmergencyTeamAndSupportBase] = Field(None, description="应急队伍与保障")
    drills_and_training_records: Optional[DrillsAndTrainingRecordsBase] = Field(None, description="演练与培训记录")
    emergency_resource_survey_metadata: Optional[EmergencyResourceSurveyMetadataBase] = Field(None, description="应急资源调查元数据")
    
    # 其他信息
    env_permits: Optional[EnvPermitsBase] = Field(None, description="环保手续信息")
    env_management: Optional[EnvManagementBase] = Field(None, description="环境管理制度")
    env_receptor_info: Optional[EnvReceptorBase] = Field(None, description="环境受体信息")
    env_pollutant_info: Optional[EnvPollutantBase] = Field(None, description="污染物信息")
    env_prevention_facilities: Optional[EnvPreventionBase] = Field(None, description="防控设施信息")
    hazardous_materials: List[HazardousMaterialBase] = Field(default_factory=list, description="危险化学品信息列表")
    emergency_resources: List[EmergencyResourceBase] = Field(default_factory=list, description="应急资源信息列表")
    emergency_orgs: List[EmergencyOrgBase] = Field(default_factory=list, description="应急组织信息列表")
    external_emergency_contacts: List[ExternalEmergencyContactBase] = Field(default_factory=list, description="外部应急救援通讯方式列表")
    project_id: Optional[int] = Field(None, description="关联项目ID")

    @validator('enterprise_identity')
    def validate_enterprise_identity(cls, v):
        if v and not v.enterprise_name:
            raise ValueError('企业名称不能为空')
        return v


class EnterpriseBasicResponse(EnterpriseBasicBase):
    """企业基本信息响应模式"""
    pass


class EnvPermitsResponse(EnvPermitsBase):
    """环保手续信息响应模式"""
    pass


class EnvManagementResponse(EnvManagementBase):
    """环境管理制度响应模式"""
    pass


class EnvReceptorResponse(EnvReceptorBase):
    """环境受体响应模式"""
    pass


class EnvPollutantResponse(EnvPollutantBase):
    """污染物响应模式"""
    pass


class EnvPreventionResponse(EnvPreventionBase):
    """防控设施响应模式"""
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


class EnterpriseIdentityResponse(EnterpriseIdentityBase):
    """企业身份信息响应模式"""
    pass


class EnterpriseAddressResponse(EnterpriseAddressBase):
    """地址与空间信息响应模式"""
    pass


class EnterpriseContactsResponse(EnterpriseContactsBase):
    """联系人与职责响应模式"""
    pass


class EnterpriseOperationResponse(EnterpriseOperationBase):
    """企业运营概况响应模式"""
    pass


class EnterpriseIntroResponse(EnterpriseIntroBase):
    """企业简介文本响应模式"""
    pass


# 步骤2：生产过程与风险物质的响应模式
class ProductInfoResponse(ProductInfoBase):
    """产品信息响应模式"""
    pass


class RawMaterialInfoResponse(RawMaterialInfoBase):
    """原辅材料信息响应模式"""
    pass


class EnergyUsageResponse(EnergyUsageBase):
    """能源使用情况响应模式"""
    pass


class ProductionProcessResponse(ProductionProcessBase):
    """生产工艺与工序响应模式"""
    pass


class StorageFacilityResponse(StorageFacilityBase):
    """储存单元响应模式"""
    pass


class LoadingOperationResponse(LoadingOperationBase):
    """装卸作业信息响应模式"""
    pass


class HazardousChemicalResponse(HazardousChemicalBase):
    """危险化学品明细响应模式"""
    pass


class HazardousWasteResponse(HazardousWasteBase):
    """危险废物与其他风险物质响应模式"""
    pass


# 步骤3：环境信息的响应模式
class NaturalFunctionZoneResponse(NaturalFunctionZoneBase):
    """自然与功能区信息响应模式"""
    pass


class EnvironmentalRiskReceptorResponse(EnvironmentalRiskReceptorBase):
    """周边环境风险受体响应模式"""
    pass


class WastewaterTreatmentFacilityResponse(WastewaterTreatmentFacilityBase):
    """废水处理设施响应模式"""
    pass


class WastewaterOutletResponse(WastewaterOutletBase):
    """废水排口响应模式"""
    pass


class WastewaterManagementResponse(WastewaterManagementBase):
    """废水产生与治理响应模式"""
    pass


class OrganizedWasteGasSourceResponse(OrganizedWasteGasSourceBase):
    """有组织废气源响应模式"""
    pass


class UnorganizedWasteGasResponse(UnorganizedWasteGasBase):
    """无组织废气源概况响应模式"""
    pass


class WasteGasManagementResponse(WasteGasManagementBase):
    """废气产生与治理响应模式"""
    pass


class NoiseSourceResponse(NoiseSourceBase):
    """主要噪声源响应模式"""
    pass


class GeneralSolidWasteResponse(GeneralSolidWasteBase):
    """一般固废响应模式"""
    pass


class NoiseAndSolidWasteResponse(NoiseAndSolidWasteBase):
    """噪声与固体废物响应模式"""
    pass


class AccidentPreventionFacilitiesResponse(AccidentPreventionFacilitiesBase):
    """事故防控设施响应模式"""
    pass


# 步骤4：环保手续与管理制度的响应模式
class EIAFileResponse(EIAFileBase):
    """环评文件响应模式"""
    pass


class EnvironmentalAcceptanceResponse(EnvironmentalAcceptanceBase):
    """竣工环保验收响应模式"""
    pass


class DischargePermitResponse(DischargePermitBase):
    """排污许可证响应模式"""
    pass


class OtherEnvCertificateResponse(OtherEnvCertificateBase):
    """其他环保相关许可证响应模式"""
    pass


class HazardousWasteAgreementResponse(HazardousWasteAgreementBase):
    """危废处置协议响应模式"""
    pass


class MedicalWasteAgreementResponse(MedicalWasteAgreementBase):
    """医疗废物处置协议响应模式"""
    pass


class EmergencyPlanFilingResponse(EmergencyPlanFilingBase):
    """环境应急预案备案情况响应模式"""
    pass


class ManagementSystemResponse(ManagementSystemBase):
    """管理制度情况响应模式"""
    pass


class PenaltyAccidentRecordResponse(PenaltyAccidentRecordBase):
    """近三年行政处罚/事故记录响应模式"""
    pass


class EnvironmentalPermitsAndManagementResponse(EnvironmentalPermitsAndManagementBase):
    """环保手续与管理制度响应模式"""
    pass


# 步骤5：应急管理与资源的响应模式
class InternalEmergencyContactResponse(InternalEmergencyContactBase):
    """内部应急通讯录响应模式"""
    pass


class ExternalEmergencyUnitContactResponse(ExternalEmergencyUnitContactBase):
    """外部应急单位联系方式响应模式"""
    pass


class EmergencyOrganizationAndContactsResponse(EmergencyOrganizationAndContactsBase):
    """应急组织机构与联络方式响应模式"""
    pass


class EmergencyMaterialResponse(EmergencyMaterialBase):
    """自储应急物资清单响应模式"""
    pass


class EmergencyFacilitiesResponse(EmergencyFacilitiesBase):
    """关键应急设施响应模式"""
    pass


class EmergencyMaterialsAndEquipmentResponse(EmergencyMaterialsAndEquipmentBase):
    """应急物资与装备响应模式"""
    pass


class EmergencyTeamAndSupportResponse(EmergencyTeamAndSupportBase):
    """应急队伍与保障响应模式"""
    pass


class DrillRecordResponse(DrillRecordBase):
    """演练记录响应模式"""
    pass


class EmergencyDrillsResponse(EmergencyDrillsBase):
    """应急演练响应模式"""
    pass


class EmergencyTrainingResponse(EmergencyTrainingBase):
    """应急与环保培训响应模式"""
    pass


class DrillsAndTrainingRecordsResponse(DrillsAndTrainingRecordsBase):
    """演练与培训记录响应模式"""
    pass


class EmergencyResourceSurveyMetadataResponse(EmergencyResourceSurveyMetadataBase):
    """应急资源调查元数据响应模式"""
    pass


class EnterpriseInfoResponse(BaseModel):
    """企业信息响应模式"""
    id: int
    user_id: int
    project_id: Optional[int] = None
    # 企业基本信息 - 5个小表块
    enterprise_identity: Optional[EnterpriseIdentityResponse] = None
    enterprise_address: Optional[EnterpriseAddressResponse] = None
    enterprise_contacts: Optional[EnterpriseContactsResponse] = None
    enterprise_operation: Optional[EnterpriseOperationResponse] = None
    enterprise_intro: Optional[EnterpriseIntroResponse] = None
    # 步骤2：生产过程与风险物质 - 6个小表块
    products_info: List[ProductInfoResponse] = []
    raw_materials_info: List[RawMaterialInfoResponse] = []
    energy_usage: Optional[EnergyUsageResponse] = None
    production_process: Optional[ProductionProcessResponse] = None
    storage_facilities: List[StorageFacilityResponse] = []
    loading_operations: Optional[LoadingOperationResponse] = None
    hazardous_chemicals: List[HazardousChemicalResponse] = []
    hazardous_waste: List[HazardousWasteResponse] = []
    # 步骤3：环境信息 - 6个小表块
    natural_function_zone: Optional[NaturalFunctionZoneResponse] = None
    environmental_risk_receptors: List[EnvironmentalRiskReceptorResponse] = []
    wastewater_management: Optional[WastewaterManagementResponse] = None
    waste_gas_management: Optional[WasteGasManagementResponse] = None
    noise_and_solid_waste: Optional[NoiseAndSolidWasteResponse] = None
    accident_prevention_facilities: Optional[AccidentPreventionFacilitiesResponse] = None
    # 步骤4：环保手续与管理制度
    environmental_permits_and_management: Optional[EnvironmentalPermitsAndManagementResponse] = None
    # 步骤5：应急管理与资源
    emergency_organization_and_contacts: Optional[EmergencyOrganizationAndContactsResponse] = None
    emergency_materials_and_equipment: Optional[EmergencyMaterialsAndEquipmentResponse] = None
    emergency_team_and_support: Optional[EmergencyTeamAndSupportResponse] = None
    drills_and_training_records: Optional[DrillsAndTrainingRecordsResponse] = None
    emergency_resource_survey_metadata: Optional[EmergencyResourceSurveyMetadataResponse] = None
    # 其他信息
    env_permits: Optional[EnvPermitsResponse] = None
    env_management: Optional[EnvManagementResponse] = None
    env_receptor_info: Optional[EnvReceptorResponse] = None
    env_pollutant_info: Optional[EnvPollutantResponse] = None
    env_prevention_facilities: Optional[EnvPreventionResponse] = None
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
    env_management: Optional[EnvManagementBase] = None
    env_receptor_info: Optional[EnvReceptorBase] = None
    env_pollutant_info: Optional[EnvPollutantBase] = None
    env_prevention_facilities: Optional[EnvPreventionBase] = None
    hazardous_materials: Optional[List[HazardousMaterialBase]] = None
    emergency_resources: Optional[List[EmergencyResourceBase]] = None
    emergency_orgs: Optional[List[EmergencyOrgBase]] = None
    external_emergency_contacts: Optional[List[ExternalEmergencyContactBase]] = None
    environmental_permits_and_management: Optional[EnvironmentalPermitsAndManagementBase] = None
    project_id: Optional[int] = None


class EnterpriseInfoList(BaseModel):
    """企业信息列表响应模式"""
    enterprise_infos: List[EnterpriseInfoResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EnterpriseDataRequest(BaseModel):
    """企业数据请求模型"""
    # 包含前端表单提交的所有字段，符合emergency_plan.json结构
    basic_info: Optional[dict] = Field(None, description="企业基本信息")
    production_process: Optional[dict] = Field(None, description="生产过程与风险物质")
    environment_info: Optional[dict] = Field(None, description="环境信息")
    compliance_info: Optional[dict] = Field(None, description="环保手续与管理制度")
    emergency_resources: Optional[dict] = Field(None, description="应急资源信息")
    # 可以包含其他需要覆盖或补充的字段
    additional_data: Optional[dict] = Field(None, description="额外的数据")


class DocumentData(BaseModel):
    """文档数据模型"""
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="HTML内容")
    word_count: int = Field(..., description="字数统计")


class DocumentGenerationResponse(BaseModel):
    """文档生成响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")