"""
企业信息数据模型
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EnterpriseInfo(Base):
    """企业基本信息表"""
    __tablename__ = "enterprise_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    
    # 企业基本信息 - 1.1 企业身份信息
    enterprise_name = Column(String(255), nullable=False, comment="企业名称（全称）")
    unified_social_credit_code = Column(String(50), comment="统一社会信用代码")
    group_company = Column(String(255), comment="所属集团/母公司（选填）")
    industry = Column(String(100), comment="所在行业")
    industry_subdivision = Column(Text, comment="行业细分说明")
    park_name = Column(String(255), comment="所在园区/工业区名称（选填）")
    risk_level = Column(String(50), comment="企业风险级别（一般/较大/重大）")
    
    # 企业基本信息 - 1.2 地址与空间信息
    province = Column(String(100), comment="所在省")
    city = Column(String(100), comment="所在市")
    district = Column(String(100), comment="所在区/县")
    detailed_address = Column(String(500), comment="详细地址")
    postal_code = Column(String(20), comment="邮编")
    fax = Column(String(50), comment="传真")
    longitude = Column(String(50), comment="企业中心点经度（WGS84）")
    latitude = Column(String(50), comment="企业中心点纬度（WGS84）")
    
    # 企业基本信息 - 1.3 联系人与职责
    legal_representative_name = Column(String(100), comment="法定代表人姓名")
    legal_representative_phone = Column(String(50), comment="法定代表人手机")
    env_officer_name = Column(String(100), comment="环保负责人姓名")
    env_officer_position = Column(String(100), comment="环保负责人职务/部门")
    env_officer_phone = Column(String(50), comment="环保负责人手机")
    emergency_contact_name = Column(String(100), comment="应急联系人姓名")
    emergency_contact_position = Column(String(100), comment="应急联系人职务")
    emergency_contact_phone = Column(String(50), comment="应急联系人手机")
    landline_phone = Column(String(50), comment="固定电话（总机或值班电话）")
    enterprise_email = Column(String(100), comment="企业联系邮箱")
    
    # 企业基本信息 - 1.4 企业运营概况
    establishment_date = Column(String(50), comment="成立时间（年月）")
    production_date = Column(String(50), comment="建成/投产时间（年月，选填）")
    production_status = Column(String(50), comment="企业在产状态（在产/停产/在建改扩建）")
    total_employees = Column(Integer, comment="员工总数（人）")
    production_staff = Column(Integer, comment="生产人员数量（人）")
    management_staff = Column(Integer, comment="管理及后勤人员数量（人，可选）")
    shift_system = Column(String(50), comment="班制（单班/两班/三班/其它）")
    daily_work_hours = Column(String(50), comment="日工作时间（小时/班）")
    annual_work_days = Column(Integer, comment="年运行天数（d/a）")
    land_area = Column(Integer, comment="占地面积（m²）")
    building_area = Column(Integer, comment="总建筑面积（m²）")
    total_investment = Column(Integer, comment="总投资额（万元）")
    env_investment = Column(Integer, comment="环保投资额（万元，选填）")
    business_types = Column(JSON, comment="主要业务/服务类型（多选+补充说明）")
    
    # 企业基本信息 - 1.5 企业简介文本
    enterprise_intro = Column(Text, comment="企业简介原文（多行文本）")
    
    # 步骤2：生产过程与风险物质 - 2.1 产品与产能
    products_info = Column(JSON, comment="产品列表信息")
    
    # 步骤2：生产过程与风险物质 - 2.2 原辅料与能源
    raw_materials_info = Column(JSON, comment="原辅材料列表信息")
    energy_usage = Column(JSON, comment="能源使用情况信息")
    
    # 步骤2：生产过程与风险物质 - 2.3 生产工艺与工序
    production_process = Column(JSON, comment="生产工艺与工序信息")
    
    # 步骤2：生产过程与风险物质 - 2.4 储存与装卸设施
    storage_facilities = Column(JSON, comment="储存单元列表信息")
    loading_operations = Column(JSON, comment="装卸作业信息")
    
    # 步骤2：生产过程与风险物质 - 2.5 危险化学品明细
    hazardous_chemicals = Column(JSON, comment="危险化学品明细信息")
    
    # 步骤2：生产过程与风险物质 - 2.6 危险废物与其他风险物质
    hazardous_waste = Column(JSON, comment="危险废物与其他风险物质信息")
    
    # 环保手续信息
    env_assessment_no = Column(String(255), comment="环评批复编号")
    acceptance_no = Column(String(255), comment="验收文件编号")
    discharge_permit_no = Column(String(255), comment="排污许可证编号")
    has_emergency_plan = Column(String(10), comment="是否有历史应急预案")  # 有/无
    emergency_plan_code = Column(String(100), comment="历史应急预案编号")  # 仅当有预案时填写
    
    # 步骤3：环境信息 - 3.1 自然与功能区信息
    administrative_division_code = Column(String(50), comment="行政区划代码")
    water_environment_function_zone = Column(String(255), comment="所属水环境功能区")
    atmospheric_environment_function_zone = Column(String(255), comment="所属大气环境功能区类别")
    watershed_name = Column(String(255), comment="所在流域名称")
    nearest_surface_water_body = Column(String(255), comment="最近地表水体名称")
    distance_to_surface_water = Column(String(50), comment="最近地表水体与厂界最短距离")
    surface_water_direction = Column(String(100), comment="最近地表水体相对方位")
    
    # 步骤3：环境信息 - 3.2 周边环境风险受体（动态数组）
    environmental_risk_receptors = Column(JSON, comment="周边环境风险受体列表")
    
    # 步骤3：环境信息 - 3.3 废水产生与治理
    drainage_system = Column(String(100), comment="排水体制")
    has_production_wastewater = Column(String(10), comment="是否存在生产废水")
    has_domestic_sewage = Column(String(10), comment="是否存在生活污水")
    wastewater_treatment_facilities = Column(JSON, comment="废水处理设施列表")
    wastewater_outlets = Column(JSON, comment="废水排口列表")
    
    # 步骤3：环境信息 - 3.4 废气产生与治理
    organized_waste_gas_sources = Column(JSON, comment="有组织废气源列表")
    unorganized_waste_gas = Column(JSON, comment="无组织废气源概况")
    
    # 步骤3：环境信息 - 3.5 噪声与固体废物
    main_noise_sources = Column(JSON, comment="主要噪声源列表")
    general_solid_wastes = Column(JSON, comment="一般固废列表")
    
    # 步骤3：环境信息 - 3.6 事故防控设施
    has_rain_sewage_diversion = Column(String(10), comment="是否设置事故雨污分流及切换设施")
    rain_sewage_diversion_description = Column(Text, comment="事故雨污分流描述")
    has_key_area_bunds = Column(String(10), comment="是否设置重点区域围堰")
    bunds_location = Column(String(255), comment="围堰位置")
    hazardous_chemicals_warehouse_seepage = Column(Text, comment="危险化学品库/危废间防渗结构说明")
    key_valves_and_shutoff_facilities = Column(Text, comment="关键阀门与切断设施说明")
    
    # 环境信息（保留原有字段以确保兼容性）
    env_receptor_info = Column(JSON, comment="环境受体信息")
    env_pollutant_info = Column(JSON, comment="污染物信息")
    env_prevention_facilities = Column(JSON, comment="防控设施信息")
    
    # 环境管理制度
    env_management_system = Column(String(50), comment="环境管理体系认证")
    env_officer = Column(String(100), comment="环保负责人")
    
    # 危险化学品信息 (JSON格式存储)
    hazardous_materials = Column(JSON, comment="危险化学品信息列表")
    
    # 应急资源信息 (JSON格式存储)
    emergency_resources = Column(JSON, comment="应急资源信息列表")
    
    # 应急组织信息 (JSON格式存储)
    emergency_orgs = Column(JSON, comment="应急组织信息列表")
    
    # 外部应急救援通讯方式 (JSON格式存储)
    external_emergency_contacts = Column(JSON, comment="外部应急救援通讯方式列表")
    
    # 步骤4：环保手续与管理制度
    
    # 4.1 环保手续（证照）- 环评文件
    eia_project_name = Column(String(255), comment="环评项目名称")
    eia_document_number = Column(String(255), comment="环评文号")
    eia_approval_date = Column(String(50), comment="批复日期")
    eia_consistency_status = Column(String(100), comment="与现状一致性")
    eia_report_upload = Column(String(255), comment="环评报告/报告表上传")
    eia_approval_upload = Column(String(255), comment="环评批复文件上传")
    
    # 4.1 环保手续（证照）- 竣工环保验收
    acceptance_type = Column(String(100), comment="验收类别")
    acceptance_document_number = Column(String(255), comment="验收文号")
    acceptance_date = Column(String(50), comment="验收日期")
    acceptance_report_upload = Column(String(255), comment="验收报告上传")
    acceptance_approval_upload = Column(String(255), comment="验收批复上传")
    
    # 4.1 环保手续（证照）- 排污许可证
    discharge_permit_number = Column(String(255), comment="排污许可证编号")
    issuing_authority = Column(String(255), comment="发证机关")
    permit_start_date = Column(String(50), comment="有效期起始日期")
    permit_end_date = Column(String(50), comment="有效期截止日期")
    permitted_pollutants = Column(Text, comment="许可排放的主要污染物")
    permit_scan_upload = Column(String(255), comment="证书扫描件上传")
    
    # 4.1 环保手续（证照）- 其他环保相关许可证（动态数组）
    other_env_certificates = Column(JSON, comment="其他环保相关许可证列表")
    
    # 4.2 危险废物/医废处置协议 - 危废处置协议
    hazardous_waste_agreement_unit = Column(String(255), comment="协议单位名称")
    hazardous_waste_unit_permit_number = Column(String(255), comment="单位许可证编号")
    hazardous_waste_agreement_start_date = Column(String(50), comment="协议起始日期")
    hazardous_waste_agreement_end_date = Column(String(50), comment="协议结束日期")
    hazardous_waste_categories = Column(Text, comment="涉及危废类别")
    hazardous_waste_agreement_upload = Column(String(255), comment="协议扫描件上传")
    
    # 4.2 危险废物/医废处置协议 - 医疗废物处置协议（如适用）
    medical_waste_agreement_unit = Column(String(255), comment="协议单位名称")
    medical_waste_unit_permit_number = Column(String(255), comment="单位许可证编号")
    medical_waste_agreement_start_date = Column(String(50), comment="协议起始日期")
    medical_waste_agreement_end_date = Column(String(50), comment="协议结束日期")
    medical_waste_categories = Column(Text, comment="涉及医废类别")
    medical_waste_agreement_upload = Column(String(255), comment="协议扫描件上传")
    
    # 4.3 环境应急预案备案情况
    has_emergency_plan = Column(String(10), comment="是否已编制突发环境事件应急预案")
    has_emergency_plan_filed = Column(String(10), comment="是否已备案")
    emergency_plan_filing_number = Column(String(255), comment="备案编号")
    emergency_plan_filing_date = Column(String(50), comment="备案日期")
    emergency_plan_filing_upload = Column(String(255), comment="备案回执/备案表上传")
    
    # 4.4 管理制度与处罚记录 - 管理制度情况
    has_risk_inspection_system = Column(String(10), comment="是否建立环境风险隐患排查制度")
    has_hazardous_chemicals_management_system = Column(String(10), comment="是否建立危险化学品安全管理制度")
    has_hazardous_waste_management_system = Column(String(10), comment="是否建立危险废物管理制度")
    has_emergency_drill_training_system = Column(String(10), comment="是否建立应急演练及培训制度")
    management_system_files_upload = Column(String(255), comment="相关制度文件打包上传")
    
    # 4.4 管理制度与处罚记录 - 近三年行政处罚/事故记录
    has_administrative_penalty = Column(String(10), comment="近三年是否受到生态环境部门行政处罚")
    administrative_penalty_details = Column(Text, comment="处罚日期、处罚决定文号、主要违法事实、整改情况")
    has_environmental_accident = Column(String(10), comment="近三年是否有较大及以上环境事故")
    environmental_accident_details = Column(Text, comment="简要说明，用于风险等级调整和案例编写")
    
    # 步骤5：应急管理与资源 - 5.1 应急组织机构与联络方式
    enterprise_24h_duty_phone = Column(String(50), comment="企业24小时值班电话")
    internal_emergency_contacts = Column(JSON, comment="内部应急通讯录，动态数组")
    external_emergency_unit_contacts = Column(JSON, comment="外部应急单位联系方式，动态数组")
    
    # 步骤5：应急管理与资源 - 5.2 应急物资与装备
    emergency_materials_list = Column(JSON, comment="自储应急物资清单，动态数组")
    emergency_warehouse_count = Column(Integer, comment="应急物资专用仓库数量")
    warehouse_total_area = Column(Integer, comment="应急物资仓库总面积")
    has_accident_pool = Column(String(10), comment="事故应急池是否存在")
    accident_pool_volume = Column(String(50), comment="事故池有效容积")
    emergency_vehicles = Column(JSON, comment="应急车辆数量及类型")
    
    # 步骤5：应急管理与资源 - 5.3 应急队伍与保障
    has_internal_rescue_team = Column(String(10), comment="是否建立企业内部应急救援队伍")
    rescue_team_size = Column(Integer, comment="应急队伍人数")
    team_composition_description = Column(Text, comment="队伍构成说明")
    has_emergency_budget = Column(String(10), comment="是否有应急经费专项预算")
    annual_emergency_budget = Column(String(50), comment="年度应急经费预算额度")
    
    # 步骤5：应急管理与资源 - 5.4 演练与培训记录
    has_conducted_drills = Column(String(10), comment="最近三年是否开展应急演练")
    drill_records = Column(JSON, comment="演练记录列表，动态数组")
    annual_emergency_training_count = Column(Integer, comment="年度应急培训次数")
    annual_environmental_training_count = Column(Integer, comment="年度环保培训次数")
    employee_coverage_rate = Column(String(50), comment="职工覆盖率")
    includes_hazardous_chemicals_safety = Column(String(10), comment="是否包含危化品安全和环境应急内容")
    
    # 步骤5：应急管理与资源 - 5.5 应急资源调查元数据
    emergency_resource_survey_year = Column(String(10), comment="本次应急资源调查基准年份")
    survey_start_date = Column(String(50), comment="调查工作开始日期")
    survey_end_date = Column(String(50), comment="调查工作结束日期")
    survey_leader_name = Column(String(100), comment="调查负责人姓名")
    survey_contact_phone = Column(String(50), comment="调查联系人及电话")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="enterprise_infos")
    project = relationship("Project", back_populates="enterprise_info")
    
    def __repr__(self):
        return f"<EnterpriseInfo(id={self.id}, enterprise_name='{self.enterprise_name}')>"