"""
企业信息相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from typing import List, Optional

from app.database import get_db
from app.models.enterprise import EnterpriseInfo
from app.models.user import User
from app.schemas.enterprise import (
    EnterpriseInfoCreate, EnterpriseInfoResponse, EnterpriseInfoUpdate,
    EnterpriseInfoList, EnterpriseBasicResponse, EnvPermitsResponse,
    EnvManagementResponse, EnvReceptorResponse, EnvPollutantResponse, EnvPreventionResponse,
    EnterpriseIdentityResponse, EnterpriseAddressResponse, EnterpriseContactsResponse,
    EnterpriseOperationResponse, EnterpriseIntroResponse,
    ProductInfoResponse, RawMaterialInfoResponse, EnergyUsageResponse,
    ProductionProcessResponse, StorageFacilityResponse, LoadingOperationResponse,
    HazardousChemicalResponse, HazardousWasteResponse,
    HazardousMaterialResponse, EmergencyResourceResponse, EmergencyOrgResponse,
    ExternalEmergencyContactResponse,
    # 步骤3：环境信息相关的响应模型
    NaturalFunctionZoneResponse, EnvironmentalRiskReceptorResponse,
    WastewaterManagementResponse, WasteGasManagementResponse,
    NoiseAndSolidWasteResponse, AccidentPreventionFacilitiesResponse,
    # 步骤4：环保手续与管理制度相关的响应模型
    EIAFileResponse, EnvironmentalAcceptanceResponse, DischargePermitResponse,
    OtherEnvCertificateResponse, HazardousWasteAgreementResponse, MedicalWasteAgreementResponse,
    EmergencyPlanFilingResponse, ManagementSystemResponse, PenaltyAccidentRecordResponse,
    EnvironmentalPermitsAndManagementResponse,
    # 步骤5：应急管理与资源相关的响应模型
    EmergencyOrganizationAndContactsResponse, EmergencyMaterialsAndEquipmentResponse,
    EmergencyTeamAndSupportResponse, DrillsAndTrainingRecordsResponse,
    EmergencyResourceSurveyMetadataResponse
)
from app.utils.auth import get_current_user
from app.utils.pagination import get_pagination_params, paginate_query
from app.utils.error_handler import handle_error, ErrorCategory

router = APIRouter(prefix="/enterprise", tags=["企业信息"])


def convert_enterprise_to_response(enterprise: EnterpriseInfo) -> EnterpriseInfoResponse:
    """将企业信息模型转换为响应模式"""
    # 处理企业身份信息
    enterprise_identity = None
    if enterprise.enterprise_name:
        enterprise_identity = EnterpriseIdentityResponse(
            enterprise_name=enterprise.enterprise_name,
            unified_social_credit_code=enterprise.unified_social_credit_code,
            group_company=enterprise.group_company,
            industry=enterprise.industry,
            industry_subdivision=enterprise.industry_subdivision,
            park_name=enterprise.park_name,
            risk_level=enterprise.risk_level
        )
    
    # 处理地址与空间信息
    enterprise_address = None
    if enterprise.province or enterprise.city:
        enterprise_address = EnterpriseAddressResponse(
            province=enterprise.province,
            city=enterprise.city,
            district=enterprise.district,
            detailed_address=enterprise.detailed_address,
            postal_code=enterprise.postal_code,
            fax=enterprise.fax,
            longitude=enterprise.longitude,
            latitude=enterprise.latitude
        )
    
    # 处理联系人与职责
    enterprise_contacts = None
    if enterprise.legal_representative_name or enterprise.env_officer_name:
        enterprise_contacts = EnterpriseContactsResponse(
            legal_representative_name=enterprise.legal_representative_name,
            legal_representative_phone=enterprise.legal_representative_phone,
            env_officer_name=enterprise.env_officer_name,
            env_officer_position=enterprise.env_officer_position,
            env_officer_phone=enterprise.env_officer_phone,
            emergency_contact_name=enterprise.emergency_contact_name,
            emergency_contact_position=enterprise.emergency_contact_position,
            emergency_contact_phone=enterprise.emergency_contact_phone,
            landline_phone=enterprise.landline_phone,
            enterprise_email=enterprise.enterprise_email
        )
    
    # 处理企业运营概况
    enterprise_operation = None
    if enterprise.establishment_date or enterprise.total_employees:
        enterprise_operation = EnterpriseOperationResponse(
            establishment_date=enterprise.establishment_date,
            production_date=enterprise.production_date,
            production_status=enterprise.production_status,
            total_employees=enterprise.total_employees,
            production_staff=enterprise.production_staff,
            management_staff=enterprise.management_staff,
            shift_system=enterprise.shift_system,
            daily_work_hours=enterprise.daily_work_hours,
            annual_work_days=enterprise.annual_work_days,
            land_area=enterprise.land_area,
            building_area=enterprise.building_area,
            total_investment=enterprise.total_investment,
            env_investment=enterprise.env_investment,
            business_types=enterprise.business_types
        )
    
    # 处理企业简介文本
    enterprise_intro = None
    if enterprise.enterprise_intro:
        enterprise_intro = EnterpriseIntroResponse(
            enterprise_intro=enterprise.enterprise_intro
        )
    
    # 处理步骤2：生产过程与风险物质 - 2.1 产品与产能
    products_info = []
    if enterprise.products_info:
        products_info = [ProductInfoResponse(**product) for product in enterprise.products_info]
    
    # 处理步骤2：生产过程与风险物质 - 2.2 原辅料与能源
    raw_materials_info = []
    if enterprise.raw_materials_info:
        raw_materials_info = [RawMaterialInfoResponse(**material) for material in enterprise.raw_materials_info]
    
    energy_usage = None
    if enterprise.energy_usage:
        energy_usage = EnergyUsageResponse(**enterprise.energy_usage)
    
    # 处理步骤2：生产过程与风险物质 - 2.3 生产工艺与工序
    production_process = None
    if enterprise.production_process:
        production_process = ProductionProcessResponse(**enterprise.production_process)
    
    # 处理步骤2：生产过程与风险物质 - 2.4 储存与装卸设施
    storage_facilities = []
    if enterprise.storage_facilities:
        storage_facilities = [StorageFacilityResponse(**facility) for facility in enterprise.storage_facilities]
    
    loading_operations = None
    if enterprise.loading_operations:
        loading_operations = LoadingOperationResponse(**enterprise.loading_operations)
    
    # 处理步骤2：生产过程与风险物质 - 2.5 危险化学品明细
    hazardous_chemicals = []
    if enterprise.hazardous_chemicals:
        hazardous_chemicals = [HazardousChemicalResponse(**chemical) for chemical in enterprise.hazardous_chemicals]
    
    # 处理步骤2：生产过程与风险物质 - 2.6 危险废物与其他风险物质
    hazardous_waste = []
    if enterprise.hazardous_waste:
        hazardous_waste = [HazardousWasteResponse(**waste) for waste in enterprise.hazardous_waste]
    
    # 处理环境管理制度
    env_management = None
    if enterprise.env_management_system or enterprise.env_officer:
        env_management = EnvManagementResponse(
            env_management_system=enterprise.env_management_system,
            env_officer=enterprise.env_officer
        )
    
    # 处理环境受体信息
    env_receptor_info = None
    if enterprise.env_receptor_info:
        env_receptor_info = EnvReceptorResponse(**enterprise.env_receptor_info)
    
    # 处理污染物信息
    env_pollutant_info = None
    if enterprise.env_pollutant_info:
        env_pollutant_info = EnvPollutantResponse(**enterprise.env_pollutant_info)
    
    # 处理防控设施信息
    env_prevention_facilities = None
    if enterprise.env_prevention_facilities:
        env_prevention_facilities = EnvPreventionResponse(**enterprise.env_prevention_facilities)
    
    # 处理步骤3：环境信息 - 3.1 自然与功能区信息
    natural_function_zone = None
    if enterprise.administrative_division_code or enterprise.water_environment_function_zone:
        natural_function_zone = NaturalFunctionZoneResponse(
            administrative_division_code=enterprise.administrative_division_code,
            water_environment_function_zone=enterprise.water_environment_function_zone,
            atmospheric_environment_function_zone=enterprise.atmospheric_environment_function_zone,
            watershed_name=enterprise.watershed_name,
            nearest_surface_water_body=enterprise.nearest_surface_water_body,
            distance_to_surface_water=enterprise.distance_to_surface_water,
            surface_water_direction=enterprise.surface_water_direction
        )
    
    # 处理步骤3：环境信息 - 3.2 周边环境风险受体
    environmental_risk_receptors = []
    if enterprise.environmental_risk_receptors:
        environmental_risk_receptors = [EnvironmentalRiskReceptorResponse(**receptor) for receptor in enterprise.environmental_risk_receptors]
    
    # 处理步骤3：环境信息 - 3.3 废水产生与治理
    wastewater_management = None
    if enterprise.drainage_system or enterprise.wastewater_treatment_facilities:
        wastewater_management = WastewaterManagementResponse(
            drainage_system=enterprise.drainage_system,
            has_production_wastewater=enterprise.has_production_wastewater,
            has_domestic_sewage=enterprise.has_domestic_sewage,
            wastewater_treatment_facilities=[facility for facility in (enterprise.wastewater_treatment_facilities or [])],
            wastewater_outlets=[outlet for outlet in (enterprise.wastewater_outlets or [])]
        )
    
    # 处理步骤3：环境信息 - 3.4 废气产生与治理
    waste_gas_management = None
    if enterprise.organized_waste_gas_sources or enterprise.unorganized_waste_gas:
        waste_gas_management = WasteGasManagementResponse(
            organized_waste_gas_sources=[source for source in (enterprise.organized_waste_gas_sources or [])],
            unorganized_waste_gas=enterprise.unorganized_waste_gas
        )
    
    # 处理步骤3：环境信息 - 3.5 噪声与固体废物
    noise_and_solid_waste = None
    if enterprise.main_noise_sources or enterprise.general_solid_wastes:
        noise_and_solid_waste = NoiseAndSolidWasteResponse(
            main_noise_sources=[source for source in (enterprise.main_noise_sources or [])],
            general_solid_wastes=[waste for waste in (enterprise.general_solid_wastes or [])]
        )
    
    # 处理步骤3：环境信息 - 3.6 事故防控设施
    accident_prevention_facilities = None
    if enterprise.has_rain_sewage_diversion or enterprise.hazardous_chemicals_warehouse_seepage:
        accident_prevention_facilities = AccidentPreventionFacilitiesResponse(
            has_rain_sewage_diversion=enterprise.has_rain_sewage_diversion,
            rain_sewage_diversion_description=enterprise.rain_sewage_diversion_description,
            has_key_area_bunds=enterprise.has_key_area_bunds,
            bunds_location=enterprise.bunds_location,
            hazardous_chemicals_warehouse_seepage=enterprise.hazardous_chemicals_warehouse_seepage,
            key_valves_and_shutoff_facilities=enterprise.key_valves_and_shutoff_facilities
        )
    
    # 处理步骤4：环保手续与管理制度
    environmental_permits_and_management = None
    if (enterprise.eia_project_name or enterprise.eia_document_number or
        enterprise.acceptance_type or enterprise.discharge_permit_number or
        enterprise.hazardous_waste_agreement_unit or enterprise.has_emergency_plan or
        enterprise.has_risk_inspection_system):
        
        # 4.1 环保手续（证照）- 环评文件
        eia_file = None
        if enterprise.eia_project_name or enterprise.eia_document_number:
            eia_file = EIAFileResponse(
                eia_project_name=enterprise.eia_project_name,
                eia_document_number=enterprise.eia_document_number,
                eia_approval_date=enterprise.eia_approval_date,
                eia_consistency_status=enterprise.eia_consistency_status,
                eia_report_upload=enterprise.eia_report_upload,
                eia_approval_upload=enterprise.eia_approval_upload
            )
        
        # 4.1 环保手续（证照）- 竣工环保验收
        environmental_acceptance = None
        if enterprise.acceptance_type or enterprise.acceptance_document_number:
            environmental_acceptance = EnvironmentalAcceptanceResponse(
                acceptance_type=enterprise.acceptance_type,
                acceptance_document_number=enterprise.acceptance_document_number,
                acceptance_date=enterprise.acceptance_date,
                acceptance_report_upload=enterprise.acceptance_report_upload,
                acceptance_approval_upload=enterprise.acceptance_approval_upload
            )
        
        # 4.1 环保手续（证照）- 排污许可证
        discharge_permit = None
        if enterprise.discharge_permit_number or enterprise.issuing_authority:
            discharge_permit = DischargePermitResponse(
                discharge_permit_number=enterprise.discharge_permit_number,
                issuing_authority=enterprise.issuing_authority,
                permit_start_date=enterprise.permit_start_date,
                permit_end_date=enterprise.permit_end_date,
                permitted_pollutants=enterprise.permitted_pollutants,
                permit_scan_upload=enterprise.permit_scan_upload
            )
        
        # 4.1 环保手续（证照）- 其他环保相关许可证
        other_env_certificates = []
        if enterprise.other_env_certificates:
            other_env_certificates = [OtherEnvCertificateResponse(**cert) for cert in enterprise.other_env_certificates]
        
        # 4.2 危险废物/医废处置协议 - 危废处置协议
        hazardous_waste_agreement = None
        if enterprise.hazardous_waste_agreement_unit or enterprise.hazardous_waste_unit_permit_number:
            hazardous_waste_agreement = HazardousWasteAgreementResponse(
                hazardous_waste_agreement_unit=enterprise.hazardous_waste_agreement_unit,
                hazardous_waste_unit_permit_number=enterprise.hazardous_waste_unit_permit_number,
                hazardous_waste_agreement_start_date=enterprise.hazardous_waste_agreement_start_date,
                hazardous_waste_agreement_end_date=enterprise.hazardous_waste_agreement_end_date,
                hazardous_waste_categories=enterprise.hazardous_waste_categories,
                hazardous_waste_agreement_upload=enterprise.hazardous_waste_agreement_upload
            )
        
        # 4.2 危险废物/医废处置协议 - 医疗废物处置协议
        medical_waste_agreement = None
        if enterprise.medical_waste_agreement_unit or enterprise.medical_waste_unit_permit_number:
            medical_waste_agreement = MedicalWasteAgreementResponse(
                medical_waste_agreement_unit=enterprise.medical_waste_agreement_unit,
                medical_waste_unit_permit_number=enterprise.medical_waste_unit_permit_number,
                medical_waste_agreement_start_date=enterprise.medical_waste_agreement_start_date,
                medical_waste_agreement_end_date=enterprise.medical_waste_agreement_end_date,
                medical_waste_categories=enterprise.medical_waste_categories,
                medical_waste_agreement_upload=enterprise.medical_waste_agreement_upload
            )
        
        # 4.3 环境应急预案备案情况
        emergency_plan_filing = None
        if enterprise.has_emergency_plan or enterprise.emergency_plan_filing_number:
            emergency_plan_filing = EmergencyPlanFilingResponse(
                has_emergency_plan=enterprise.has_emergency_plan,
                has_emergency_plan_filed=enterprise.has_emergency_plan_filed,
                emergency_plan_filing_number=enterprise.emergency_plan_filing_number,
                emergency_plan_filing_date=enterprise.emergency_plan_filing_date,
                emergency_plan_filing_upload=enterprise.emergency_plan_filing_upload
            )
        
        # 4.4 管理制度与处罚记录 - 管理制度情况
        management_system = None
        if enterprise.has_risk_inspection_system or enterprise.management_system_files_upload:
            management_system = ManagementSystemResponse(
                has_risk_inspection_system=enterprise.has_risk_inspection_system,
                has_hazardous_chemicals_management_system=enterprise.has_hazardous_chemicals_management_system,
                has_hazardous_waste_management_system=enterprise.has_hazardous_waste_management_system,
                has_emergency_drill_training_system=enterprise.has_emergency_drill_training_system,
                management_system_files_upload=enterprise.management_system_files_upload
            )
        
        # 4.4 管理制度与处罚记录 - 近三年行政处罚/事故记录
        penalty_accident_record = None
        if enterprise.has_administrative_penalty or enterprise.has_environmental_accident:
            penalty_accident_record = PenaltyAccidentRecordResponse(
                has_administrative_penalty=enterprise.has_administrative_penalty,
                administrative_penalty_details=enterprise.administrative_penalty_details,
                has_environmental_accident=enterprise.has_environmental_accident,
                environmental_accident_details=enterprise.environmental_accident_details
            )
        
        environmental_permits_and_management = EnvironmentalPermitsAndManagementResponse(
            eia_file=eia_file,
            environmental_acceptance=environmental_acceptance,
            discharge_permit=discharge_permit,
            other_env_certificates=other_env_certificates,
            hazardous_waste_agreement=hazardous_waste_agreement,
            medical_waste_agreement=medical_waste_agreement,
            emergency_plan_filing=emergency_plan_filing,
            management_system=management_system,
            penalty_accident_record=penalty_accident_record
        )
    
    # 处理步骤5：应急管理与资源 - 5.1 应急组织机构与联络方式
    emergency_organization_and_contacts = None
    if enterprise.enterprise_24h_duty_phone or enterprise.internal_emergency_contacts or enterprise.external_emergency_unit_contacts:
        internal_emergency_contacts = []
        if enterprise.internal_emergency_contacts:
            internal_emergency_contacts = [contact for contact in enterprise.internal_emergency_contacts]
        
        external_emergency_unit_contacts = []
        if enterprise.external_emergency_unit_contacts:
            external_emergency_unit_contacts = [contact for contact in enterprise.external_emergency_unit_contacts]
        
        emergency_organization_and_contacts = EmergencyOrganizationAndContactsResponse(
            enterprise_24h_duty_phone=enterprise.enterprise_24h_duty_phone,
            internal_emergency_contacts=internal_emergency_contacts,
            external_emergency_unit_contacts=external_emergency_unit_contacts
        )
    
    # 处理步骤5：应急管理与资源 - 5.2 应急物资与装备
    emergency_materials_and_equipment = None
    if enterprise.emergency_materials_list or enterprise.emergency_warehouse_count:
        emergency_materials_list = []
        if enterprise.emergency_materials_list:
            emergency_materials_list = [material for material in enterprise.emergency_materials_list]
        
        emergency_facilities = None
        if enterprise.emergency_warehouse_count or enterprise.warehouse_total_area:
            emergency_facilities = {
                'emergency_warehouse_count': enterprise.emergency_warehouse_count,
                'warehouse_total_area': enterprise.warehouse_total_area,
                'has_accident_pool': enterprise.has_accident_pool,
                'accident_pool_volume': enterprise.accident_pool_volume,
                'emergency_vehicles': enterprise.emergency_vehicles
            }
        
        emergency_materials_and_equipment = EmergencyMaterialsAndEquipmentResponse(
            emergency_materials_list=emergency_materials_list,
            emergency_facilities=emergency_facilities
        )
    
    # 处理步骤5：应急管理与资源 - 5.3 应急队伍与保障
    emergency_team_and_support = None
    if enterprise.has_internal_rescue_team or enterprise.rescue_team_size:
        emergency_team_and_support = EmergencyTeamAndSupportResponse(
            has_internal_rescue_team=enterprise.has_internal_rescue_team,
            rescue_team_size=enterprise.rescue_team_size,
            team_composition_description=enterprise.team_composition_description,
            has_emergency_budget=enterprise.has_emergency_budget,
            annual_emergency_budget=enterprise.annual_emergency_budget
        )
    
    # 处理步骤5：应急管理与资源 - 5.4 演练与培训记录
    drills_and_training_records = None
    if enterprise.has_conducted_drills or enterprise.annual_emergency_training_count:
        emergency_drills = None
        if enterprise.has_conducted_drills:
            drill_records = []
            if enterprise.drill_records:
                drill_records = [record for record in enterprise.drill_records]
            
            emergency_drills = {
                'has_conducted_drills': enterprise.has_conducted_drills,
                'drill_records': drill_records
            }
        
        emergency_training = None
        if enterprise.annual_emergency_training_count:
            emergency_training = {
                'annual_emergency_training_count': enterprise.annual_emergency_training_count,
                'annual_environmental_training_count': enterprise.annual_environmental_training_count,
                'employee_coverage_rate': enterprise.employee_coverage_rate,
                'includes_hazardous_chemicals_safety': enterprise.includes_hazardous_chemicals_safety
            }
        
        drills_and_training_records = DrillsAndTrainingRecordsResponse(
            emergency_drills=emergency_drills,
            emergency_training=emergency_training
        )
    
    # 处理步骤5：应急管理与资源 - 5.5 应急资源调查元数据
    emergency_resource_survey_metadata = None
    if enterprise.emergency_resource_survey_year or enterprise.survey_leader_name:
        emergency_resource_survey_metadata = EmergencyResourceSurveyMetadataResponse(
            emergency_resource_survey_year=enterprise.emergency_resource_survey_year,
            survey_start_date=enterprise.survey_start_date,
            survey_end_date=enterprise.survey_end_date,
            survey_leader_name=enterprise.survey_leader_name,
            survey_contact_phone=enterprise.survey_contact_phone
        )
    
    return EnterpriseInfoResponse(
        id=enterprise.id,
        user_id=enterprise.user_id,
        project_id=enterprise.project_id,
        # 企业基本信息 - 5个小表块
        enterprise_identity=enterprise_identity,
        enterprise_address=enterprise_address,
        enterprise_contacts=enterprise_contacts,
        enterprise_operation=enterprise_operation,
        enterprise_intro=enterprise_intro,
        # 步骤2：生产过程与风险物质 - 6个小表块
        products_info=products_info,
        raw_materials_info=raw_materials_info,
        energy_usage=energy_usage,
        production_process=production_process,
        storage_facilities=storage_facilities,
        loading_operations=loading_operations,
        hazardous_chemicals=hazardous_chemicals,
        hazardous_waste=hazardous_waste,
        # 步骤3：环境信息 - 6个小表块
        natural_function_zone=natural_function_zone,
        environmental_risk_receptors=environmental_risk_receptors,
        wastewater_management=wastewater_management,
        waste_gas_management=waste_gas_management,
        noise_and_solid_waste=noise_and_solid_waste,
        accident_prevention_facilities=accident_prevention_facilities,
        # 步骤4：环保手续与管理制度
        environmental_permits_and_management=environmental_permits_and_management,
        # 步骤5：应急管理与资源
        emergency_organization_and_contacts=emergency_organization_and_contacts,
        emergency_materials_and_equipment=emergency_materials_and_equipment,
        emergency_team_and_support=emergency_team_and_support,
        drills_and_training_records=drills_and_training_records,
        emergency_resource_survey_metadata=emergency_resource_survey_metadata,
        # 其他信息
        env_permits=EnvPermitsResponse(
            env_assessment_no=enterprise.env_assessment_no,
            acceptance_no=enterprise.acceptance_no,
            discharge_permit_no=enterprise.discharge_permit_no,
            has_emergency_plan=enterprise.has_emergency_plan,
            emergency_plan_code=enterprise.emergency_plan_code
        ),
        env_management=env_management,
        env_receptor_info=env_receptor_info,
        env_pollutant_info=env_pollutant_info,
        env_prevention_facilities=env_prevention_facilities,
        hazardous_materials=[
            HazardousMaterialResponse(
                id=str(material.get('id', '')),
                name=material.get('name', ''),
                max_storage=material.get('max_storage', ''),
                annual_usage=material.get('annual_usage', ''),
                storage_location=material.get('storage_location', '')
            )
            for material in (enterprise.hazardous_materials or [])
        ],
        emergency_resources=[
            EmergencyResourceResponse(
                id=str(resource.get('id', '')),
                name=resource.get('name', ''),
                custom_resource_name=resource.get('custom_resource_name', ''),
                quantity=resource.get('quantity', ''),
                purpose=resource.get('purpose', ''),
                storage_location=resource.get('storage_location', ''),
                custodian=resource.get('custodian', ''),
                custodian_contact=resource.get('custodian_contact', '')
            )
            for resource in (enterprise.emergency_resources or [])
        ],
        emergency_orgs=[
            EmergencyOrgResponse(
                id=str(org.get('id', '')),
                org_name=org.get('org_name', ''),
                custom_org_name=org.get('custom_org_name', ''),
                responsible_person=org.get('responsible_person', ''),
                contact_phone=org.get('contact_phone', ''),
                department=org.get('department', ''),
                duty_phone=org.get('duty_phone', '')
            )
            for org in (enterprise.emergency_orgs or [])
        ],
        external_emergency_contacts=[
            ExternalEmergencyContactResponse(
                id=str(contact.get('id', '')),
                unit_name=contact.get('unit_name', ''),
                contact_method=contact.get('contact_method', ''),
                custom_contact_method=contact.get('custom_contact_method', ''),
                custom_unit_name=contact.get('custom_unit_name', '')
            )
            for contact in (enterprise.external_emergency_contacts or [])
        ],
        created_at=enterprise.created_at,
        updated_at=enterprise.updated_at
    )


@router.post("/info", response_model=EnterpriseInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise_info(
    enterprise_data: EnterpriseInfoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建企业信息
    """
    print(f"🏢 创建企业信息请求 - 用户: {current_user.email}, ID: {current_user.id}")
    print(f"📋 项目ID: {enterprise_data.project_id}")
    
    # 添加详细的调试日志
    print(f"🔍 企业身份信息: {enterprise_data.enterprise_identity}")
    print(f"🔍 企业名称: {enterprise_data.enterprise_identity.enterprise_name if enterprise_data.enterprise_identity else 'None'}")
    print(f"🔍 企业名称是否为空: {not enterprise_data.enterprise_identity or not enterprise_data.enterprise_identity.enterprise_name}")
    
    try:
        # 检查用户是否已有企业信息（可选限制）
        existing_info = db.query(EnterpriseInfo).filter(
            EnterpriseInfo.user_id == current_user.id
        ).first()
        
        # 如果需要限制每个用户只能有一条企业信息，可以取消下面的注释
        # if existing_info:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="用户已存在企业信息，请更新现有信息"
        #     )
        
        # 验证必填字段
        if not enterprise_data.enterprise_identity or not enterprise_data.enterprise_identity.enterprise_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="企业名称为必填项，请填写完整的企业身份信息"
            )
        
        # 创建新的企业信息
        db_enterprise = EnterpriseInfo(
            user_id=current_user.id,
            project_id=enterprise_data.project_id,
            
            # 企业基本信息 - 1.1 企业身份信息
            enterprise_name=enterprise_data.enterprise_identity.enterprise_name,
            unified_social_credit_code=enterprise_data.enterprise_identity.unified_social_credit_code,
            group_company=enterprise_data.enterprise_identity.group_company,
            industry=enterprise_data.enterprise_identity.industry,
            industry_subdivision=enterprise_data.enterprise_identity.industry_subdivision,
            park_name=enterprise_data.enterprise_identity.park_name,
            risk_level=enterprise_data.enterprise_identity.risk_level,
            
            # 企业基本信息 - 1.2 地址与空间信息
            province=enterprise_data.enterprise_address.province if enterprise_data.enterprise_address else None,
            city=enterprise_data.enterprise_address.city if enterprise_data.enterprise_address else None,
            district=enterprise_data.enterprise_address.district if enterprise_data.enterprise_address else None,
            detailed_address=enterprise_data.enterprise_address.detailed_address if enterprise_data.enterprise_address else None,
            postal_code=enterprise_data.enterprise_address.postal_code if enterprise_data.enterprise_address else None,
            fax=enterprise_data.enterprise_address.fax if enterprise_data.enterprise_address else None,
            longitude=enterprise_data.enterprise_address.longitude if enterprise_data.enterprise_address else None,
            latitude=enterprise_data.enterprise_address.latitude if enterprise_data.enterprise_address else None,
            
            # 企业基本信息 - 1.3 联系人与职责
            legal_representative_name=enterprise_data.enterprise_contacts.legal_representative_name if enterprise_data.enterprise_contacts else None,
            legal_representative_phone=enterprise_data.enterprise_contacts.legal_representative_phone if enterprise_data.enterprise_contacts else None,
            env_officer_name=enterprise_data.enterprise_contacts.env_officer_name if enterprise_data.enterprise_contacts else None,
            env_officer_position=enterprise_data.enterprise_contacts.env_officer_position if enterprise_data.enterprise_contacts else None,
            env_officer_phone=enterprise_data.enterprise_contacts.env_officer_phone if enterprise_data.enterprise_contacts else None,
            emergency_contact_name=enterprise_data.enterprise_contacts.emergency_contact_name if enterprise_data.enterprise_contacts else None,
            emergency_contact_position=enterprise_data.enterprise_contacts.emergency_contact_position if enterprise_data.enterprise_contacts else None,
            emergency_contact_phone=enterprise_data.enterprise_contacts.emergency_contact_phone if enterprise_data.enterprise_contacts else None,
            landline_phone=enterprise_data.enterprise_contacts.landline_phone if enterprise_data.enterprise_contacts else None,
            enterprise_email=enterprise_data.enterprise_contacts.enterprise_email if enterprise_data.enterprise_contacts else None,
            
            # 企业基本信息 - 1.4 企业运营概况
            establishment_date=enterprise_data.enterprise_operation.establishment_date if enterprise_data.enterprise_operation else None,
            production_date=enterprise_data.enterprise_operation.production_date if enterprise_data.enterprise_operation else None,
            production_status=enterprise_data.enterprise_operation.production_status if enterprise_data.enterprise_operation else None,
            total_employees=enterprise_data.enterprise_operation.total_employees if enterprise_data.enterprise_operation else None,
            production_staff=enterprise_data.enterprise_operation.production_staff if enterprise_data.enterprise_operation else None,
            management_staff=enterprise_data.enterprise_operation.management_staff if enterprise_data.enterprise_operation else None,
            shift_system=enterprise_data.enterprise_operation.shift_system if enterprise_data.enterprise_operation else None,
            daily_work_hours=enterprise_data.enterprise_operation.daily_work_hours if enterprise_data.enterprise_operation else None,
            annual_work_days=enterprise_data.enterprise_operation.annual_work_days if enterprise_data.enterprise_operation else None,
            land_area=enterprise_data.enterprise_operation.land_area if enterprise_data.enterprise_operation else None,
            building_area=enterprise_data.enterprise_operation.building_area if enterprise_data.enterprise_operation else None,
            total_investment=enterprise_data.enterprise_operation.total_investment if enterprise_data.enterprise_operation else None,
            env_investment=enterprise_data.enterprise_operation.env_investment if enterprise_data.enterprise_operation else None,
            business_types=enterprise_data.enterprise_operation.business_types if enterprise_data.enterprise_operation else None,
            
            # 企业基本信息 - 1.5 企业简介文本
            enterprise_intro=enterprise_data.enterprise_intro.enterprise_intro if enterprise_data.enterprise_intro else None,
            
            # 步骤2：生产过程与风险物质 - 2.1 产品与产能
            products_info=[product.dict() for product in enterprise_data.products_info] if enterprise_data.products_info else None,
            
            # 步骤2：生产过程与风险物质 - 2.2 原辅料与能源
            raw_materials_info=[material.dict() for material in enterprise_data.raw_materials_info] if enterprise_data.raw_materials_info else None,
            energy_usage=enterprise_data.energy_usage.dict() if enterprise_data.energy_usage else None,
            
            # 步骤2：生产过程与风险物质 - 2.3 生产工艺与工序
            production_process=enterprise_data.production_process.dict() if enterprise_data.production_process else None,
            
            # 步骤2：生产过程与风险物质 - 2.4 储存与装卸设施
            storage_facilities=[facility.dict() for facility in enterprise_data.storage_facilities] if enterprise_data.storage_facilities else None,
            loading_operations=enterprise_data.loading_operations.dict() if enterprise_data.loading_operations else None,
            
            # 步骤2：生产过程与风险物质 - 2.5 危险化学品明细
            hazardous_chemicals=[chemical.dict() for chemical in enterprise_data.hazardous_chemicals] if enterprise_data.hazardous_chemicals else None,
            
            # 步骤2：生产过程与风险物质 - 2.6 危险废物与其他风险物质
            hazardous_waste=[waste.dict() for waste in enterprise_data.hazardous_waste] if enterprise_data.hazardous_waste else None,
            
            # 步骤3：环境信息 - 3.1 自然与功能区信息
            administrative_division_code=enterprise_data.natural_function_zone.administrative_division_code if enterprise_data.natural_function_zone else None,
            water_environment_function_zone=enterprise_data.natural_function_zone.water_environment_function_zone if enterprise_data.natural_function_zone else None,
            atmospheric_environment_function_zone=enterprise_data.natural_function_zone.atmospheric_environment_function_zone if enterprise_data.natural_function_zone else None,
            watershed_name=enterprise_data.natural_function_zone.watershed_name if enterprise_data.natural_function_zone else None,
            nearest_surface_water_body=enterprise_data.natural_function_zone.nearest_surface_water_body if enterprise_data.natural_function_zone else None,
            distance_to_surface_water=enterprise_data.natural_function_zone.distance_to_surface_water if enterprise_data.natural_function_zone else None,
            surface_water_direction=enterprise_data.natural_function_zone.surface_water_direction if enterprise_data.natural_function_zone else None,
            
            # 步骤3：环境信息 - 3.2 周边环境风险受体
            environmental_risk_receptors=[receptor.dict() for receptor in enterprise_data.environmental_risk_receptors] if enterprise_data.environmental_risk_receptors else None,
            
            # 步骤3：环境信息 - 3.3 废水产生与治理
            drainage_system=enterprise_data.wastewater_management.drainage_system if enterprise_data.wastewater_management else None,
            has_production_wastewater=enterprise_data.wastewater_management.has_production_wastewater if enterprise_data.wastewater_management else None,
            has_domestic_sewage=enterprise_data.wastewater_management.has_domestic_sewage if enterprise_data.wastewater_management else None,
            wastewater_treatment_facilities=[facility.dict() for facility in enterprise_data.wastewater_management.wastewater_treatment_facilities] if enterprise_data.wastewater_management and enterprise_data.wastewater_management.wastewater_treatment_facilities else None,
            wastewater_outlets=[outlet.dict() for outlet in enterprise_data.wastewater_management.wastewater_outlets] if enterprise_data.wastewater_management and enterprise_data.wastewater_management.wastewater_outlets else None,
            
            # 步骤3：环境信息 - 3.4 废气产生与治理
            organized_waste_gas_sources=[source.dict() for source in enterprise_data.waste_gas_management.organized_waste_gas_sources] if enterprise_data.waste_gas_management and enterprise_data.waste_gas_management.organized_waste_gas_sources else None,
            unorganized_waste_gas=enterprise_data.waste_gas_management.unorganized_waste_gas.dict() if enterprise_data.waste_gas_management and enterprise_data.waste_gas_management.unorganized_waste_gas else None,
            
            # 步骤3：环境信息 - 3.5 噪声与固体废物
            main_noise_sources=[source.dict() for source in enterprise_data.noise_and_solid_waste.main_noise_sources] if enterprise_data.noise_and_solid_waste and enterprise_data.noise_and_solid_waste.main_noise_sources else None,
            general_solid_wastes=[waste.dict() for waste in enterprise_data.noise_and_solid_waste.general_solid_wastes] if enterprise_data.noise_and_solid_waste and enterprise_data.noise_and_solid_waste.general_solid_wastes else None,
            
            # 步骤3：环境信息 - 3.6 事故防控设施
            has_rain_sewage_diversion=enterprise_data.accident_prevention_facilities.has_rain_sewage_diversion if enterprise_data.accident_prevention_facilities else None,
            rain_sewage_diversion_description=enterprise_data.accident_prevention_facilities.rain_sewage_diversion_description if enterprise_data.accident_prevention_facilities else None,
            has_key_area_bunds=enterprise_data.accident_prevention_facilities.has_key_area_bunds if enterprise_data.accident_prevention_facilities else None,
            bunds_location=enterprise_data.accident_prevention_facilities.bunds_location if enterprise_data.accident_prevention_facilities else None,
            hazardous_chemicals_warehouse_seepage=enterprise_data.accident_prevention_facilities.hazardous_chemicals_warehouse_seepage if enterprise_data.accident_prevention_facilities else None,
            key_valves_and_shutoff_facilities=enterprise_data.accident_prevention_facilities.key_valves_and_shutoff_facilities if enterprise_data.accident_prevention_facilities else None,
            
            # 步骤4：环保手续与管理制度
            # 4.1 环保手续（证照）- 环评文件
            eia_project_name=enterprise_data.environmental_permits_and_management.eia_file.eia_project_name if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.eia_file else None,
            eia_document_number=enterprise_data.environmental_permits_and_management.eia_file.eia_document_number if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.eia_file else None,
            eia_approval_date=enterprise_data.environmental_permits_and_management.eia_file.eia_approval_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.eia_file else None,
            eia_consistency_status=enterprise_data.environmental_permits_and_management.eia_file.eia_consistency_status if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.eia_file else None,
            eia_report_upload=enterprise_data.environmental_permits_and_management.eia_file.eia_report_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.eia_file else None,
            eia_approval_upload=enterprise_data.environmental_permits_and_management.eia_file.eia_approval_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.eia_file else None,
            
            # 4.1 环保手续（证照）- 竣工环保验收
            acceptance_type=enterprise_data.environmental_permits_and_management.environmental_acceptance.acceptance_type if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.environmental_acceptance else None,
            acceptance_document_number=enterprise_data.environmental_permits_and_management.environmental_acceptance.acceptance_document_number if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.environmental_acceptance else None,
            acceptance_date=enterprise_data.environmental_permits_and_management.environmental_acceptance.acceptance_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.environmental_acceptance else None,
            acceptance_report_upload=enterprise_data.environmental_permits_and_management.environmental_acceptance.acceptance_report_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.environmental_acceptance else None,
            acceptance_approval_upload=enterprise_data.environmental_permits_and_management.environmental_acceptance.acceptance_approval_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.environmental_acceptance else None,
            
            # 4.1 环保手续（证照）- 排污许可证
            discharge_permit_number=enterprise_data.environmental_permits_and_management.discharge_permit.discharge_permit_number if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.discharge_permit else None,
            issuing_authority=enterprise_data.environmental_permits_and_management.discharge_permit.issuing_authority if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.discharge_permit else None,
            permit_start_date=enterprise_data.environmental_permits_and_management.discharge_permit.permit_start_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.discharge_permit else None,
            permit_end_date=enterprise_data.environmental_permits_and_management.discharge_permit.permit_end_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.discharge_permit else None,
            permitted_pollutants=enterprise_data.environmental_permits_and_management.discharge_permit.permitted_pollutants if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.discharge_permit else None,
            permit_scan_upload=enterprise_data.environmental_permits_and_management.discharge_permit.permit_scan_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.discharge_permit else None,
            
            # 4.1 环保手续（证照）- 其他环保相关许可证
            other_env_certificates=[cert.dict() for cert in enterprise_data.environmental_permits_and_management.other_env_certificates] if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.other_env_certificates else None,
            
            # 4.2 危险废物/医废处置协议 - 危废处置协议
            hazardous_waste_agreement_unit=enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.hazardous_waste_agreement_unit if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.hazardous_waste_agreement else None,
            hazardous_waste_unit_permit_number=enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.hazardous_waste_unit_permit_number if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.hazardous_waste_agreement else None,
            hazardous_waste_agreement_start_date=enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.hazardous_waste_agreement_start_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.hazardous_waste_agreement else None,
            hazardous_waste_agreement_end_date=enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.hazardous_waste_agreement_end_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.hazardous_waste_agreement else None,
            hazardous_waste_categories=enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.hazardous_waste_categories if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.hazardous_waste_agreement else None,
            hazardous_waste_agreement_upload=enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.hazardous_waste_agreement_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.hazardous_waste_agreement else None,
            
            # 4.2 危险废物/医废处置协议 - 医疗废物处置协议
            medical_waste_agreement_unit=enterprise_data.environmental_permits_and_management.medical_waste_agreement.medical_waste_agreement_unit if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.medical_waste_agreement else None,
            medical_waste_unit_permit_number=enterprise_data.environmental_permits_and_management.medical_waste_agreement.medical_waste_unit_permit_number if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.medical_waste_agreement else None,
            medical_waste_agreement_start_date=enterprise_data.environmental_permits_and_management.medical_waste_agreement.medical_waste_agreement_start_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.medical_waste_agreement else None,
            medical_waste_agreement_end_date=enterprise_data.environmental_permits_and_management.medical_waste_agreement.medical_waste_agreement_end_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.medical_waste_agreement else None,
            medical_waste_categories=enterprise_data.environmental_permits_and_management.medical_waste_agreement.medical_waste_categories if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.medical_waste_agreement else None,
            medical_waste_agreement_upload=enterprise_data.environmental_permits_and_management.medical_waste_agreement.medical_waste_agreement_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.medical_waste_agreement else None,
            
            # 4.3 环境应急预案备案情况
            has_emergency_plan=enterprise_data.environmental_permits_and_management.emergency_plan_filing.has_emergency_plan if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.emergency_plan_filing else None,
            has_emergency_plan_filed=enterprise_data.environmental_permits_and_management.emergency_plan_filing.has_emergency_plan_filed if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.emergency_plan_filing else None,
            emergency_plan_filing_number=enterprise_data.environmental_permits_and_management.emergency_plan_filing.emergency_plan_filing_number if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.emergency_plan_filing else None,
            emergency_plan_filing_date=enterprise_data.environmental_permits_and_management.emergency_plan_filing.emergency_plan_filing_date if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.emergency_plan_filing else None,
            emergency_plan_filing_upload=enterprise_data.environmental_permits_and_management.emergency_plan_filing.emergency_plan_filing_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.emergency_plan_filing else None,
            
            # 4.4 管理制度与处罚记录 - 管理制度情况
            has_risk_inspection_system=enterprise_data.environmental_permits_and_management.management_system.has_risk_inspection_system if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.management_system else None,
            has_hazardous_chemicals_management_system=enterprise_data.environmental_permits_and_management.management_system.has_hazardous_chemicals_management_system if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.management_system else None,
            has_hazardous_waste_management_system=enterprise_data.environmental_permits_and_management.management_system.has_hazardous_waste_management_system if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.management_system else None,
            has_emergency_drill_training_system=enterprise_data.environmental_permits_and_management.management_system.has_emergency_drill_training_system if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.management_system else None,
            management_system_files_upload=enterprise_data.environmental_permits_and_management.management_system.management_system_files_upload if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.management_system else None,
            
            # 4.4 管理制度与处罚记录 - 近三年行政处罚/事故记录
            has_administrative_penalty=enterprise_data.environmental_permits_and_management.penalty_accident_record.has_administrative_penalty if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.penalty_accident_record else None,
            administrative_penalty_details=enterprise_data.environmental_permits_and_management.penalty_accident_record.administrative_penalty_details if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.penalty_accident_record else None,
            has_environmental_accident=enterprise_data.environmental_permits_and_management.penalty_accident_record.has_environmental_accident if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.penalty_accident_record else None,
            environmental_accident_details=enterprise_data.environmental_permits_and_management.penalty_accident_record.environmental_accident_details if enterprise_data.environmental_permits_and_management and enterprise_data.environmental_permits_and_management.penalty_accident_record else None,
            
            # 环保手续信息
            env_assessment_no=enterprise_data.env_permits.env_assessment_no,
            acceptance_no=enterprise_data.env_permits.acceptance_no,
            discharge_permit_no=enterprise_data.env_permits.discharge_permit_no,
            # 注意：has_emergency_plan 已在步骤4中设置，这里不重复设置
            emergency_plan_code=enterprise_data.env_permits.emergency_plan_code,
            
            # 环境管理制度
            env_management_system=enterprise_data.env_management.env_management_system if enterprise_data.env_management else None,
            env_officer=enterprise_data.env_management.env_officer if enterprise_data.env_management else None,
            
            # 环境信息
            env_receptor_info=enterprise_data.env_receptor_info.dict() if enterprise_data.env_receptor_info else None,
            env_pollutant_info=enterprise_data.env_pollutant_info.dict() if enterprise_data.env_pollutant_info else None,
            env_prevention_facilities=enterprise_data.env_prevention_facilities.dict() if enterprise_data.env_prevention_facilities else None,
            
            # JSON数据
            hazardous_materials=[material.dict() for material in enterprise_data.hazardous_materials],
            emergency_resources=[resource.dict() for resource in enterprise_data.emergency_resources],
            emergency_orgs=[org.dict() for org in enterprise_data.emergency_orgs],
            external_emergency_contacts=[contact.dict() for contact in enterprise_data.external_emergency_contacts],
            
            # 步骤5：应急管理与资源 - 5.1 应急组织机构与联络方式
            enterprise_24h_duty_phone=enterprise_data.emergency_organization_and_contacts.enterprise_24h_duty_phone if enterprise_data.emergency_organization_and_contacts else None,
            internal_emergency_contacts=[contact.dict() for contact in enterprise_data.emergency_organization_and_contacts.internal_emergency_contacts] if enterprise_data.emergency_organization_and_contacts and enterprise_data.emergency_organization_and_contacts.internal_emergency_contacts else None,
            external_emergency_unit_contacts=[contact.dict() for contact in enterprise_data.emergency_organization_and_contacts.external_emergency_unit_contacts] if enterprise_data.emergency_organization_and_contacts and enterprise_data.emergency_organization_and_contacts.external_emergency_unit_contacts else None,
            
            # 步骤5：应急管理与资源 - 5.2 应急物资与装备
            emergency_materials_list=[material.dict() for material in enterprise_data.emergency_materials_and_equipment.emergency_materials_list] if enterprise_data.emergency_materials_and_equipment and enterprise_data.emergency_materials_and_equipment.emergency_materials_list else None,
            emergency_warehouse_count=enterprise_data.emergency_materials_and_equipment.emergency_facilities.emergency_warehouse_count if enterprise_data.emergency_materials_and_equipment and enterprise_data.emergency_materials_and_equipment.emergency_facilities else None,
            warehouse_total_area=enterprise_data.emergency_materials_and_equipment.emergency_facilities.warehouse_total_area if enterprise_data.emergency_materials_and_equipment and enterprise_data.emergency_materials_and_equipment.emergency_facilities else None,
            has_accident_pool=enterprise_data.emergency_materials_and_equipment.emergency_facilities.has_accident_pool if enterprise_data.emergency_materials_and_equipment and enterprise_data.emergency_materials_and_equipment.emergency_facilities else None,
            accident_pool_volume=enterprise_data.emergency_materials_and_equipment.emergency_facilities.accident_pool_volume if enterprise_data.emergency_materials_and_equipment and enterprise_data.emergency_materials_and_equipment.emergency_facilities else None,
            emergency_vehicles=enterprise_data.emergency_materials_and_equipment.emergency_facilities.emergency_vehicles if enterprise_data.emergency_materials_and_equipment and enterprise_data.emergency_materials_and_equipment.emergency_facilities else None,
            
            # 步骤5：应急管理与资源 - 5.3 应急队伍与保障
            has_internal_rescue_team=enterprise_data.emergency_team_and_support.has_internal_rescue_team if enterprise_data.emergency_team_and_support else None,
            rescue_team_size=enterprise_data.emergency_team_and_support.rescue_team_size if enterprise_data.emergency_team_and_support else None,
            team_composition_description=enterprise_data.emergency_team_and_support.team_composition_description if enterprise_data.emergency_team_and_support else None,
            has_emergency_budget=enterprise_data.emergency_team_and_support.has_emergency_budget if enterprise_data.emergency_team_and_support else None,
            annual_emergency_budget=enterprise_data.emergency_team_and_support.annual_emergency_budget if enterprise_data.emergency_team_and_support else None,
            
            # 步骤5：应急管理与资源 - 5.4 演练与培训记录
            has_conducted_drills=enterprise_data.drills_and_training_records.emergency_drills.has_conducted_drills if enterprise_data.drills_and_training_records and enterprise_data.drills_and_training_records.emergency_drills else None,
            drill_records=[record.dict() for record in enterprise_data.drills_and_training_records.emergency_drills.drill_records] if enterprise_data.drills_and_training_records and enterprise_data.drills_and_training_records.emergency_drills and enterprise_data.drills_and_training_records.emergency_drills.drill_records else None,
            annual_emergency_training_count=enterprise_data.drills_and_training_records.emergency_training.annual_emergency_training_count if enterprise_data.drills_and_training_records and enterprise_data.drills_and_training_records.emergency_training else None,
            annual_environmental_training_count=enterprise_data.drills_and_training_records.emergency_training.annual_environmental_training_count if enterprise_data.drills_and_training_records and enterprise_data.drills_and_training_records.emergency_training else None,
            employee_coverage_rate=enterprise_data.drills_and_training_records.emergency_training.employee_coverage_rate if enterprise_data.drills_and_training_records and enterprise_data.drills_and_training_records.emergency_training else None,
            includes_hazardous_chemicals_safety=enterprise_data.drills_and_training_records.emergency_training.includes_hazardous_chemicals_safety if enterprise_data.drills_and_training_records and enterprise_data.drills_and_training_records.emergency_training else None,
            
            # 步骤5：应急管理与资源 - 5.5 应急资源调查元数据
            emergency_resource_survey_year=enterprise_data.emergency_resource_survey_metadata.emergency_resource_survey_year if enterprise_data.emergency_resource_survey_metadata else None,
            survey_start_date=enterprise_data.emergency_resource_survey_metadata.survey_start_date if enterprise_data.emergency_resource_survey_metadata else None,
            survey_end_date=enterprise_data.emergency_resource_survey_metadata.survey_end_date if enterprise_data.emergency_resource_survey_metadata else None,
            survey_leader_name=enterprise_data.emergency_resource_survey_metadata.survey_leader_name if enterprise_data.emergency_resource_survey_metadata else None,
            survey_contact_phone=enterprise_data.emergency_resource_survey_metadata.survey_contact_phone if enterprise_data.emergency_resource_survey_metadata else None
        )
        
        db.add(db_enterprise)
        db.commit()
        db.refresh(db_enterprise)
        
        return convert_enterprise_to_response(db_enterprise)
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "operation": "create_enterprise_info"},
            user_message="创建企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.get("/info", response_model=EnterpriseInfoList)
async def get_enterprise_infos(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的企业信息列表
    """
    try:
        # 构建查询
        query = db.query(EnterpriseInfo).filter(EnterpriseInfo.user_id == current_user.id)
        
        # 搜索过滤
        if search:
            query = query.filter(
                or_(
                    EnterpriseInfo.enterprise_name.contains(search),
                    EnterpriseInfo.address.contains(search),
                    EnterpriseInfo.industry.contains(search)
                )
            )
        
        # 按创建时间倒序排列
        query = query.order_by(desc(EnterpriseInfo.created_at))
        
        # 分页
        pagination = get_pagination_params(page, page_size)
        paginated_query = paginate_query(query, pagination)
        
        enterprise_infos = paginated_query.all()
        total = query.count()
        
        return EnterpriseInfoList(
            enterprise_infos=[convert_enterprise_to_response(info) for info in enterprise_infos],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size
        )
        
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "operation": "get_enterprise_infos"},
            user_message="获取企业信息列表失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.get("/info/{info_id}", response_model=EnterpriseInfoResponse)
async def get_enterprise_info(
    info_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取特定企业信息
    """
    try:
        enterprise = db.query(EnterpriseInfo).filter(
            and_(EnterpriseInfo.id == info_id, EnterpriseInfo.user_id == current_user.id)
        ).first()
        
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业信息不存在"
            )
        
        return convert_enterprise_to_response(enterprise)
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "info_id": info_id, "operation": "get_enterprise_info"},
            user_message="获取企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.put("/info/{info_id}", response_model=EnterpriseInfoResponse)
async def update_enterprise_info(
    info_id: int,
    enterprise_data: EnterpriseInfoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新企业信息
    """
    try:
        enterprise = db.query(EnterpriseInfo).filter(
            and_(EnterpriseInfo.id == info_id, EnterpriseInfo.user_id == current_user.id)
        ).first()
        
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业信息不存在"
            )
        
        # 更新企业基本信息 - 1.1 企业身份信息
        if enterprise_data.enterprise_identity:
            for field, value in enterprise_data.enterprise_identity.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新企业基本信息 - 1.2 地址与空间信息
        if enterprise_data.enterprise_address:
            for field, value in enterprise_data.enterprise_address.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新企业基本信息 - 1.3 联系人与职责
        if enterprise_data.enterprise_contacts:
            for field, value in enterprise_data.enterprise_contacts.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新企业基本信息 - 1.4 企业运营概况
        if enterprise_data.enterprise_operation:
            for field, value in enterprise_data.enterprise_operation.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新企业基本信息 - 1.5 企业简介文本
        if enterprise_data.enterprise_intro:
            for field, value in enterprise_data.enterprise_intro.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤2：生产过程与风险物质 - 2.1 产品与产能
        if enterprise_data.products_info is not None:
            enterprise.products_info = [product.dict() for product in enterprise_data.products_info]
        
        # 更新步骤2：生产过程与风险物质 - 2.2 原辅料与能源
        if enterprise_data.raw_materials_info is not None:
            enterprise.raw_materials_info = [material.dict() for material in enterprise_data.raw_materials_info]
        
        if enterprise_data.energy_usage is not None:
            enterprise.energy_usage = enterprise_data.energy_usage.dict()
        
        # 更新步骤2：生产过程与风险物质 - 2.3 生产工艺与工序
        if enterprise_data.production_process is not None:
            enterprise.production_process = enterprise_data.production_process.dict()
        
        # 更新步骤2：生产过程与风险物质 - 2.4 储存与装卸设施
        if enterprise_data.storage_facilities is not None:
            enterprise.storage_facilities = [facility.dict() for facility in enterprise_data.storage_facilities]
        
        if enterprise_data.loading_operations is not None:
            enterprise.loading_operations = enterprise_data.loading_operations.dict()
        
        # 更新步骤2：生产过程与风险物质 - 2.5 危险化学品明细
        if enterprise_data.hazardous_chemicals is not None:
            enterprise.hazardous_chemicals = [chemical.dict() for chemical in enterprise_data.hazardous_chemicals]
        
        # 更新步骤2：生产过程与风险物质 - 2.6 危险废物与其他风险物质
        if enterprise_data.hazardous_waste is not None:
            enterprise.hazardous_waste = [waste.dict() for waste in enterprise_data.hazardous_waste]
        
        # 更新步骤3：环境信息 - 3.1 自然与功能区信息
        if enterprise_data.natural_function_zone:
            for field, value in enterprise_data.natural_function_zone.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤3：环境信息 - 3.2 周边环境风险受体
        if enterprise_data.environmental_risk_receptors is not None:
            enterprise.environmental_risk_receptors = [receptor.dict() for receptor in enterprise_data.environmental_risk_receptors]
        
        # 更新步骤3：环境信息 - 3.3 废水产生与治理
        if enterprise_data.wastewater_management:
            for field, value in enterprise_data.wastewater_management.dict(exclude_unset=True).items():
                if field == 'wastewater_treatment_facilities' and value is not None:
                    enterprise.wastewater_treatment_facilities = [facility.dict() for facility in value]
                elif field == 'wastewater_outlets' and value is not None:
                    enterprise.wastewater_outlets = [outlet.dict() for outlet in value]
                elif hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤3：环境信息 - 3.4 废气产生与治理
        if enterprise_data.waste_gas_management:
            for field, value in enterprise_data.waste_gas_management.dict(exclude_unset=True).items():
                if field == 'organized_waste_gas_sources' and value is not None:
                    enterprise.organized_waste_gas_sources = [source.dict() for source in value]
                elif field == 'unorganized_waste_gas' and value is not None:
                    enterprise.unorganized_waste_gas = value.dict()
                elif hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤3：环境信息 - 3.5 噪声与固体废物
        if enterprise_data.noise_and_solid_waste:
            for field, value in enterprise_data.noise_and_solid_waste.dict(exclude_unset=True).items():
                if field == 'main_noise_sources' and value is not None:
                    enterprise.main_noise_sources = [source.dict() for source in value]
                elif field == 'general_solid_wastes' and value is not None:
                    enterprise.general_solid_wastes = [waste.dict() for waste in value]
                elif hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤3：环境信息 - 3.6 事故防控设施
        if enterprise_data.accident_prevention_facilities:
            for field, value in enterprise_data.accident_prevention_facilities.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤4：环保手续与管理制度
        if enterprise_data.environmental_permits_and_management:
            # 4.1 环保手续（证照）- 环评文件
            if enterprise_data.environmental_permits_and_management.eia_file:
                for field, value in enterprise_data.environmental_permits_and_management.eia_file.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.1 环保手续（证照）- 竣工环保验收
            if enterprise_data.environmental_permits_and_management.environmental_acceptance:
                for field, value in enterprise_data.environmental_permits_and_management.environmental_acceptance.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.1 环保手续（证照）- 排污许可证
            if enterprise_data.environmental_permits_and_management.discharge_permit:
                for field, value in enterprise_data.environmental_permits_and_management.discharge_permit.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.1 环保手续（证照）- 其他环保相关许可证
            if enterprise_data.environmental_permits_and_management.other_env_certificates is not None:
                enterprise.other_env_certificates = [cert.dict() for cert in enterprise_data.environmental_permits_and_management.other_env_certificates]
            
            # 4.2 危险废物/医废处置协议 - 危废处置协议
            if enterprise_data.environmental_permits_and_management.hazardous_waste_agreement:
                for field, value in enterprise_data.environmental_permits_and_management.hazardous_waste_agreement.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.2 危险废物/医废处置协议 - 医疗废物处置协议
            if enterprise_data.environmental_permits_and_management.medical_waste_agreement:
                for field, value in enterprise_data.environmental_permits_and_management.medical_waste_agreement.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.3 环境应急预案备案情况
            if enterprise_data.environmental_permits_and_management.emergency_plan_filing:
                for field, value in enterprise_data.environmental_permits_and_management.emergency_plan_filing.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.4 管理制度与处罚记录 - 管理制度情况
            if enterprise_data.environmental_permits_and_management.management_system:
                for field, value in enterprise_data.environmental_permits_and_management.management_system.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            # 4.4 管理制度与处罚记录 - 近三年行政处罚/事故记录
            if enterprise_data.environmental_permits_and_management.penalty_accident_record:
                for field, value in enterprise_data.environmental_permits_and_management.penalty_accident_record.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
        
        # 更新环保手续信息
        if enterprise_data.env_permits:
            for field, value in enterprise_data.env_permits.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新环境管理制度
        if enterprise_data.env_management:
            for field, value in enterprise_data.env_management.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新环境信息
        if enterprise_data.env_receptor_info is not None:
            enterprise.env_receptor_info = enterprise_data.env_receptor_info.dict()
        
        if enterprise_data.env_pollutant_info is not None:
            enterprise.env_pollutant_info = enterprise_data.env_pollutant_info.dict()
        
        if enterprise_data.env_prevention_facilities is not None:
            enterprise.env_prevention_facilities = enterprise_data.env_prevention_facilities.dict()
        
        # 更新JSON数据
        if enterprise_data.hazardous_materials is not None:
            enterprise.hazardous_materials = [material.dict() for material in enterprise_data.hazardous_materials]
        
        if enterprise_data.emergency_resources is not None:
            enterprise.emergency_resources = [resource.dict() for resource in enterprise_data.emergency_resources]
        
        if enterprise_data.emergency_orgs is not None:
            enterprise.emergency_orgs = [org.dict() for org in enterprise_data.emergency_orgs]
        
        if enterprise_data.external_emergency_contacts is not None:
            enterprise.external_emergency_contacts = [contact.dict() for contact in enterprise_data.external_emergency_contacts]
        
        # 更新步骤5：应急管理与资源 - 5.1 应急组织机构与联络方式
        if enterprise_data.emergency_organization_and_contacts:
            for field, value in enterprise_data.emergency_organization_and_contacts.dict(exclude_unset=True).items():
                if field == 'internal_emergency_contacts' and value is not None:
                    enterprise.internal_emergency_contacts = [contact.dict() for contact in value]
                elif field == 'external_emergency_unit_contacts' and value is not None:
                    enterprise.external_emergency_unit_contacts = [contact.dict() for contact in value]
                elif hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤5：应急管理与资源 - 5.2 应急物资与装备
        if enterprise_data.emergency_materials_and_equipment:
            if enterprise_data.emergency_materials_and_equipment.emergency_materials_list is not None:
                enterprise.emergency_materials_list = [material.dict() for material in enterprise_data.emergency_materials_and_equipment.emergency_materials_list]
            
            if enterprise_data.emergency_materials_and_equipment.emergency_facilities:
                for field, value in enterprise_data.emergency_materials_and_equipment.emergency_facilities.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
        
        # 更新步骤5：应急管理与资源 - 5.3 应急队伍与保障
        if enterprise_data.emergency_team_and_support:
            for field, value in enterprise_data.emergency_team_and_support.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新步骤5：应急管理与资源 - 5.4 演练与培训记录
        if enterprise_data.drills_and_training_records:
            if enterprise_data.drills_and_training_records.emergency_drills:
                for field, value in enterprise_data.drills_and_training_records.emergency_drills.dict(exclude_unset=True).items():
                    if field == 'drill_records' and value is not None:
                        enterprise.drill_records = [record.dict() for record in value]
                    elif hasattr(enterprise, field):
                        setattr(enterprise, field, value)
            
            if enterprise_data.drills_and_training_records.emergency_training:
                for field, value in enterprise_data.drills_and_training_records.emergency_training.dict(exclude_unset=True).items():
                    if hasattr(enterprise, field):
                        setattr(enterprise, field, value)
        
        # 更新步骤5：应急管理与资源 - 5.5 应急资源调查元数据
        if enterprise_data.emergency_resource_survey_metadata:
            for field, value in enterprise_data.emergency_resource_survey_metadata.dict(exclude_unset=True).items():
                if hasattr(enterprise, field):
                    setattr(enterprise, field, value)
        
        # 更新项目关联
        if enterprise_data.project_id is not None:
            enterprise.project_id = enterprise_data.project_id
        
        db.commit()
        db.refresh(enterprise)
        
        return convert_enterprise_to_response(enterprise)
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "info_id": info_id, "operation": "update_enterprise_info"},
            user_message="更新企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )


@router.delete("/info/{info_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enterprise_info(
    info_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除企业信息
    """
    try:
        enterprise = db.query(EnterpriseInfo).filter(
            and_(EnterpriseInfo.id == info_id, EnterpriseInfo.user_id == current_user.id)
        ).first()
        
        if not enterprise:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="企业信息不存在"
            )
        
        db.delete(enterprise)
        db.commit()
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        error_info = handle_error(
            e,
            context={"user_id": current_user.id, "info_id": info_id, "operation": "delete_enterprise_info"},
            user_message="删除企业信息失败"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_info.user_message
        )