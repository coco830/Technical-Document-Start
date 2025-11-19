import React, { useState } from 'react'
import { useForm, useFieldArray, Controller } from 'react-hook-form'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import { useUserStore } from '@/store/userStore'
import ProjectLayout from '@/components/ProjectLayout'

// 简单的SVG图标组件
const ChevronDownIcon: React.FC<{ className?: string }> = ({ className = "h-5 w-5" }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
)

const ChevronUpIcon: React.FC<{ className?: string }> = ({ className = "h-5 w-5" }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
  </svg>
)

const PlusIcon: React.FC<{ className?: string }> = ({ className = "h-5 w-5" }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
)

const TrashIcon: React.FC<{ className?: string }> = ({ className = "h-5 w-5" }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
)

// 定义表单数据类型
interface EnterpriseIdentity {
  enterprise_name: string
  unified_social_credit_code: string
  group_company: string
  industry: string
  industry_subdivision: string
  park_name: string
  risk_level: string
}

interface EnterpriseAddress {
  province: string
  city: string
  district: string
  detailed_address: string
  postal_code: string
  fax: string
  longitude: string
  latitude: string
}

interface EnterpriseContacts {
  legal_representative_name: string
  legal_representative_phone: string
  env_officer_name: string
  env_officer_position: string
  env_officer_phone: string
  emergency_contact_name: string
  emergency_contact_position: string
  emergency_contact_phone: string
  landline_phone: string
  enterprise_email: string
}

interface EnterpriseOperation {
  establishment_date: string
  production_date: string
  production_status: string
  total_employees: number
  production_staff: number
  management_staff: number
  shift_system: string
  daily_work_hours: string
  annual_work_days: number
  land_area: number
  building_area: number
  total_investment: number
  env_investment: number
  business_types: string[]
}

interface EnterpriseIntro {
  enterprise_intro: string
}

// 步骤2：生产过程与风险物质 - 2.1 产品与产能
interface ProductInfo {
  product_name: string
  product_type: string
  design_capacity: string
  actual_annual_output: string
}

// 步骤2：生产过程与风险物质 - 2.2 原辅料与能源
interface RawMaterialInfo {
  material_name: string
  cas_number: string
  material_category: string
  is_hazardous: string
  hazard_categories: string[]
  annual_usage: string
  max_inventory: string
  main_process_equipment: string
  material_phase: string
}

interface EnergyUsage {
  water_usage: string
  industrial_water: string
  domestic_water: string
  electricity_usage: string
  other_energy: string[]
}

// 步骤2：生产过程与风险物质 - 2.3 生产工艺与工序
interface ProductionProcess {
  process_type: string
  process_description: string
  process_flow_file: string
  process_nodes: ProcessNode[]
}

interface ProcessNode {
  node_name: string
  node_function: string
  key_equipment: string
  involves_hazardous: string
}

// 步骤2：生产过程与风险物质 - 2.4 储存与装卸设施
interface StorageFacility {
  facility_name: string
  facility_type: string
  main_materials: string[]
  rated_capacity: string
  max_inventory: string
  storage_method: string
  has_bund: string
  anti_seep_measures: string
  location_description: string
}

interface LoadingOperation {
  has_loading: string
  main_materials: string[]
  loading_area_location: string
  leak_prevention: string
}

// 步骤2：生产过程与风险物质 - 2.5 危险化学品明细
interface HazardousChemical {
  chemical_name: string
  cas_number: string
  hazard_category: string
  location_unit: string
  max_inventory: string
  critical_quantity: string
  material_phase: string
  is_major_hazard: string
  msds_file: string
}

// 步骤2：生产过程与风险物质 - 2.6 危险废物与其他风险物质
interface HazardousWaste {
  waste_name: string
  waste_category: string
  waste_code: string
  source_process: string
  hazard_characteristics: string[]
  storage_location: string
  storage_method: string
  max_storage: string
  max_storage_days: string
  disposal_company: string
}

interface EnvPermits {
  env_assessment_no: string
  acceptance_no: string
  discharge_permit_no: string
  has_emergency_plan: string
  emergency_plan_code: string
}

interface EnvManagement {
  env_management_system: string
  env_officer: string
}

interface EnvReceptor {
  population_density: string
  sensitive_distance: string
}

interface EnvPollutant {
  main_pollutants: string
  discharge_method: string
}

interface EnvPrevention {
  wastewater_facility: string
  waste_gas_facility: string
}

interface HazardousMaterial {
  id: string
  name: string
  max_storage: string
  annual_usage: string
  storage_location: string
}

interface EmergencyResource {
  id: string
  name: string
  custom_resource_name: string
  quantity: string
  purpose: string
  storage_location: string
  custodian: string
  custodian_contact: string
}

interface EmergencyOrg {
  id: string
  org_name: string
  custom_org_name: string
  responsible_person: string
  contact_phone: string
  department: string
  duty_phone: string
}

interface ExternalEmergencyContact {
  id: string
  unit_name: string
  contact_method: string
  custom_contact_method: string
  custom_unit_name: string
}

interface EnterpriseFormData {
  enterprise_identity: EnterpriseIdentity
  enterprise_address: EnterpriseAddress
  enterprise_contacts: EnterpriseContacts
  enterprise_operation: EnterpriseOperation
  enterprise_intro: EnterpriseIntro
  // 步骤2：生产过程与风险物质
  products_info: ProductInfo[]
  raw_materials_info: RawMaterialInfo[]
  energy_usage: EnergyUsage
  production_process: ProductionProcess
  storage_facilities: StorageFacility[]
  loading_operations: LoadingOperation
  hazardous_chemicals: HazardousChemical[]
  hazardous_waste: HazardousWaste[]
  // 步骤3：环境信息
  natural_functional_area: NaturalFunctionalArea
  environment_risk_receptors: EnvironmentRiskReceptor[]
  wastewater_management: WastewaterManagement
  waste_gas_management: WasteGasManagement
  noise_and_solid_waste: NoiseAndSolidWaste
  accident_prevention_facilities: AccidentPreventionFacilities
  // 步骤4：环保手续与管理制度
  env_assessment_file: EnvAssessmentFile
  env_acceptance: EnvAcceptance
  discharge_permit: DischargePermit
  other_env_permits: OtherEnvPermit[]
  hazardous_waste_agreement: HazardousWasteAgreement
  medical_waste_agreement: MedicalWasteAgreement
  emergency_plan_filing: EmergencyPlanFiling
  management_systems: ManagementSystems
  penalty_accident_records: PenaltyAccidentRecords
  // 步骤5：应急管理与资源
  emergency_organization_and_contacts: EmergencyOrganizationAndContacts
  emergency_materials_and_equipment: EmergencyMaterialsAndEquipment
  emergency_team_and_support: EmergencyTeamAndSupport
  drills_and_training_records: DrillsAndTrainingRecords
  emergency_resource_survey_metadata: EmergencyResourceSurveyMetadata
  // 其他信息
  env_permits: EnvPermits
  env_management: EnvManagement
  env_receptor_info: EnvReceptor
  env_pollutant_info: EnvPollutant
  env_prevention_facilities: EnvPrevention
  hazardous_materials: HazardousMaterial[]
  emergency_resources: EmergencyResource[]
  emergency_orgs: EmergencyOrg[]
  external_emergency_contacts: ExternalEmergencyContact[]
}

// 步骤3：环境信息的接口定义
interface NaturalFunctionalArea {
  administrative_code: string
  water_environment_function_area: string
  atmospheric_environment_function_area: string
  basin_name: string
  nearest_surface_water: string
  shortest_distance_to_water: string
  relative_position_to_water: string
}

interface EnvironmentRiskReceptor {
  id: string
  environment_element: string
  receptor_type: string
  receptor_name: string
  relative_position: string
  distance_to_boundary: string
  function_and_scale: string
  environment_quality_target: string
}

interface WastewaterTreatment {
  facility_name: string
  service_scope: string
  process_type: string
  design_capacity: string
  actual_treatment_volume: string
  discharge_destination: string
}

interface WastewaterOutlet {
  outlet_name: string
  outlet_type: string
  discharge_destination: string
  has_online_monitoring: string
}

interface WastewaterManagement {
  drainage_system: string
  has_production_wastewater: string
  has_domestic_wastewater: string
  treatment_facilities: WastewaterTreatment[]
  has_accident_pool: string
  accident_pool_volume: string
  wastewater_outlets: WastewaterOutlet[]
}

interface OrganizedWasteGas {
  source_name: string
  corresponding_process: string
  main_pollutants: string[]
  treatment_facility_type: string
  exhaust_stack_number: string
  exhaust_stack_height: string
  discharge_destination: string
  has_online_monitoring: string
}

interface WasteGasManagement {
  has_obvious_unorganized_gas: string
  main_unorganized_areas: string
  existing_control_measures: string
  organized_waste_gas_sources: OrganizedWasteGas[]
}

interface NoiseSource {
  noise_source_name: string
  location: string
  noise_control_measures: string
}

interface GeneralSolidWaste {
  waste_name: string
  source_process: string
  waste_nature: string
  annual_generation: string
  storage_method: string
  disposal_method: string
  destination_unit: string
}

interface NoiseAndSolidWaste {
  noise_sources: NoiseSource[]
  general_solid_wastes: GeneralSolidWaste[]
}

interface AccidentPreventionFacilities {
  has_rain_sewage_diversion: string
  rain_sewage_diversion_description: string
  has_key_area_bund: string
  key_area_bund_location: string
  hazardous_chemical_warehouse_seepage_control: string
  key_valve_shut_off_facilities: string
}

// 步骤4：环保手续与管理制度的接口定义
// 4.1 环保手续（证照）
interface EnvAssessmentFile {
  eia_project_name: string
  eia_document_number: string
  eia_approval_date: string
  eia_consistency_status: string
  eia_report_upload: string
  eia_approval_upload: string
}

interface EnvAcceptance {
  acceptance_type: string
  acceptance_document_number: string
  acceptance_date: string
  acceptance_report_upload: string
  acceptance_approval_upload: string
}

interface DischargePermit {
  discharge_permit_number: string
  issuing_authority: string
  permit_start_date: string
  permit_end_date: string
  permitted_pollutants: string
  permit_scan_upload: string
}

interface OtherEnvPermit {
  certificate_type: string
  certificate_number: string
  issuing_authority: string
  validity_period: string
  scan_file_upload: string
}

// 4.2 危险废物/医废处置协议
interface HazardousWasteAgreement {
  hazardous_waste_agreement_unit: string
  hazardous_waste_unit_permit_number: string
  hazardous_waste_agreement_start_date: string
  hazardous_waste_agreement_end_date: string
  hazardous_waste_categories: string
  hazardous_waste_agreement_upload: string
}

interface MedicalWasteAgreement {
  medical_waste_agreement_unit: string
  medical_waste_unit_permit_number: string
  medical_waste_agreement_start_date: string
  medical_waste_agreement_end_date: string
  medical_waste_categories: string
  medical_waste_agreement_upload: string
}

// 4.3 环境应急预案备案情况
interface EmergencyPlanFiling {
  has_emergency_plan: string
  has_emergency_plan_filed: string
  emergency_plan_filing_number: string
  emergency_plan_filing_date: string
  emergency_plan_filing_upload: string
}

// 4.4 管理制度与处罚记录
interface ManagementSystems {
  has_risk_inspection_system: string
  has_hazardous_chemicals_management_system: string
  has_hazardous_waste_management_system: string
  has_emergency_drill_training_system: string
  management_system_files_upload: string
}

interface PenaltyAccidentRecords {
  has_administrative_penalty: string
  administrative_penalty_details: string
  has_environmental_accident: string
  environmental_accident_details: string
}

// 步骤5：应急管理与资源的接口定义
// 5.1 应急组织机构与联络方式
interface InternalEmergencyContact {
  id: string
  organization_role: string
  department_name: string
  contact_name: string
  position: string
  mobile_phone: string
}

interface ExternalEmergencyUnit {
  id: string
  unit_category: string
  unit_name: string
  contact_phone: string
  emergency_capability_description: string
  has_cooperation_agreement: string
}

interface EmergencyOrganizationAndContacts {
  duty_phone_24h: string
  internal_emergency_contacts: InternalEmergencyContact[]
  external_emergency_units: ExternalEmergencyUnit[]
}

// 5.2 应急物资与装备
interface SelfStoredEmergencyMaterial {
  id: string
  material_name: string
  unit: string
  quantity: string
  purpose: string
  storage_location: string
  custodian_name: string
  custodian_phone: string
}

interface EmergencyMaterialsAndEquipment {
  self_stored_materials: SelfStoredEmergencyMaterial[]
  warehouse_count: string
  warehouse_total_area: string
  has_accident_pool: string
  accident_pool_effective_volume: string
  emergency_vehicle_count_and_type: string
}

// 5.3 应急队伍与保障
interface EmergencyTeamAndSupport {
  has_internal_rescue_team: string
  team_member_count: string
  team_composition_description: string
  has_special_emergency_budget: string
  annual_emergency_budget_amount: string
}

// 5.4 演练与培训记录
interface DrillRecord {
  id: string
  drill_date: string
  drill_type: string
  drill_description: string
  participants_count: string
  drill_effectiveness_evaluation: string
}

interface DrillsAndTrainingRecords {
  has_conducted_drills_recent_three_years: string
  drill_records: DrillRecord[]
  annual_emergency_training_count: string
  annual_environmental_training_count: string
  employee_coverage_rate: string
  includes_hazardous_chemical_safety: string
  includes_environmental_emergency: string
}

// 5.5 应急资源调查元数据
interface EmergencyResourceSurveyMetadata {
  survey_reference_year: string
  survey_start_date: string
  survey_end_date: string
  survey_leader_name: string
  survey_contact_person_and_phone: string
}

export default function ProjectEnterprise() {
  const { id, step } = useParams()
  const navigate = useNavigate()

  // 根据URL参数确定当前步骤
  const getStepFromParam = (stepParam?: string) => {
    switch (stepParam) {
      case 'production': return 2
      case 'environment': return 3
      case 'permits': return 4
      case 'emergency': return 5
      default: return 1
    }
  }

  const [currentStep, setCurrentStep] = useState(getStepFromParam(step))
  const [currentCard, setCurrentCard] = useState(1) // 当前卡片索引（1-5）
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    permits: false,
    materials: false,
    resources: false,
    orgs: false,
    external_contacts: false,
    environment: false
  })

  const steps = [
    { id: 1, title: '企业基本信息', key: 'basic', cards: 5 },
    { id: 2, title: '生产过程与风险物质', key: 'production', cards: 6 },
    { id: 3, title: '环境信息', key: 'environment', cards: 6 },
    { id: 4, title: '环保手续与管理制度', key: 'permits', cards: 4 },
    { id: 5, title: '应急管理与资源', key: 'emergency', cards: 5 }
  ]

  // 企业基本信息的5个卡片
  const enterpriseBasicCards = [
    { id: 1, title: '企业身份信息', icon: '🏢' },
    { id: 2, title: '地址与空间信息', icon: '📍' },
    { id: 3, title: '联系人与职责', icon: '👥' },
    { id: 4, title: '企业运营概况', icon: '📊' },
    { id: 5, title: '企业简介文本', icon: '📝' }
  ]

  // 步骤2：生产过程与风险物质的6个卡片
  const productionRiskCards = [
    { id: 1, title: '产品与产能', icon: '📦' },
    { id: 2, title: '原辅料与能源', icon: '⚡' },
    { id: 3, title: '生产工艺与工序', icon: '⚙️' },
    { id: 4, title: '储存与装卸设施', icon: '🏭' },
    { id: 5, title: '危险化学品明细', icon: '☢' },
    { id: 6, title: '危险废物与其他风险物质', icon: '🗑️' }
  ]

  // 步骤3：环境信息的6个卡片
  const environmentInfoCards = [
    { id: 1, title: '自然与功能区信息', icon: '🌍' },
    { id: 2, title: '周边环境风险受体', icon: '🏘️' },
    { id: 3, title: '废水产生与治理', icon: '💧' },
    { id: 4, title: '废气产生与治理', icon: '💨' },
    { id: 5, title: '噪声与固体废物', icon: '🔊' },
    { id: 6, title: '事故防控设施', icon: '🛡️' }
  ]

  // 步骤4：环保手续与管理制度的4个卡片
  const environmentalPermitsCards = [
    { id: 1, title: '环保手续（证照）', icon: '📋' },
    { id: 2, title: '危险废物/医废处置协议', icon: '🗑️' },
    { id: 3, title: '环境应急预案备案情况', icon: '📝' },
    { id: 4, title: '管理制度与处罚记录', icon: '⚖️' }
  ]

  // 步骤5：应急管理与资源的5个卡片
  const emergencyManagementCards = [
    { id: 1, title: '应急组织机构与联络方式', icon: '🚑' },
    { id: 2, title: '应急物资与装备', icon: '🛡️' },
    { id: 3, title: '应急队伍与保障', icon: '👥' },
    { id: 4, title: '演练与培训记录', icon: '📋' },
    { id: 5, title: '应急资源调查元数据', icon: '📊' }
  ]


  const handleStepChange = (stepId: number) => {
    setCurrentStep(stepId)
    setCurrentCard(1) // 切换步骤时重置为第一个卡片
    const stepKey = steps.find(s => s.id === stepId)?.key
    if (stepKey) {
      // 更新URL以反映当前步骤
      if (stepId === 1) {
        navigate(`/project/${id}/enterprise`, { replace: true })
      } else {
        navigate(`/project/${id}/enterprise/${stepKey}`, { replace: true })
      }
      
      setExpandedSections({
        basic: stepKey === 'basic',
        permits: stepKey === 'permits',
        materials: stepKey === 'production',
        resources: stepKey === 'emergency',
        orgs: stepKey === 'emergency',
        external_contacts: stepKey === 'emergency',
        environment: stepKey === 'environment'
      })
    }
  }

  const handleCardChange = (cardId: number) => {
    setCurrentCard(cardId)
  }

  const handleNext = () => {
    if (currentStep === 1 && currentCard < enterpriseBasicCards.length) {
      // 在企业基本信息步骤内，切换到下一个卡片
      setCurrentCard(currentCard + 1)
    } else if (currentStep === 1 && currentCard === enterpriseBasicCards.length) {
      // 企业基本信息完成，进入下一步
      handleStepChange(currentStep + 1)
    } else if (currentStep === 2 && currentCard < productionRiskCards.length) {
      // 在生产过程与风险物质步骤内，切换到下一个卡片
      setCurrentCard(currentCard + 1)
    } else if (currentStep === 2 && currentCard === productionRiskCards.length) {
      // 生产过程与风险物质完成，进入下一步
      handleStepChange(currentStep + 1)
    } else if (currentStep === 3 && currentCard < environmentInfoCards.length) {
      // 在环境信息步骤内，切换到下一个卡片
      setCurrentCard(currentCard + 1)
    } else if (currentStep === 3 && currentCard === environmentInfoCards.length) {
      // 环境信息完成，进入下一步
      handleStepChange(currentStep + 1)
    } else if (currentStep === 4 && currentCard < environmentalPermitsCards.length) {
      // 在环保手续与管理制度步骤内，切换到下一个卡片
      setCurrentCard(currentCard + 1)
    } else if (currentStep === 4 && currentCard === environmentalPermitsCards.length) {
      // 环保手续与管理制度完成，进入下一步
      handleStepChange(currentStep + 1)
    } else if (currentStep === 5 && currentCard < emergencyManagementCards.length) {
      // 在应急管理与资源步骤内，切换到下一个卡片
      setCurrentCard(currentCard + 1)
    } else if (currentStep === 5 && currentCard === emergencyManagementCards.length) {
      // 应急管理与资源完成，跳转到AI生成页面
      navigate(`/project/${id}/ai-generate`)
    } else if (currentStep < steps.length) {
      // 其他步骤直接进入下一步
      handleStepChange(currentStep + 1)
    } else {
      // 完成所有步骤，跳转到AI生成页面
      navigate(`/project/${id}/ai-generate`)
    }
  }

  const handlePrevious = () => {
    if (currentStep === 1 && currentCard > 1) {
      // 在企业基本信息步骤内，切换到上一个卡片
      setCurrentCard(currentCard - 1)
    } else if (currentStep === 1 && currentCard === 1) {
      // 在第一个卡片，不能后退
      return
    } else if (currentStep === 2 && currentCard > 1) {
      // 在生产过程与风险物质步骤内，切换到上一个卡片
      setCurrentCard(currentCard - 1)
    } else if (currentStep === 2 && currentCard === 1) {
      // 在第一个卡片，返回上一步骤
      handleStepChange(currentStep - 1)
    } else if (currentStep === 3 && currentCard > 1) {
      // 在环境信息步骤内，切换到上一个卡片
      setCurrentCard(currentCard - 1)
    } else if (currentStep === 3 && currentCard === 1) {
      // 在第一个卡片，返回上一步骤
      handleStepChange(currentStep - 1)
    } else if (currentStep === 4 && currentCard > 1) {
      // 在环保手续与管理制度步骤内，切换到上一个卡片
      setCurrentCard(currentCard - 1)
    } else if (currentStep === 4 && currentCard === 1) {
      // 在第一个卡片，返回上一步骤
      handleStepChange(currentStep - 1)
    } else if (currentStep === 5 && currentCard > 1) {
      // 在应急管理与资源步骤内，切换到上一个卡片
      setCurrentCard(currentCard - 1)
    } else if (currentStep === 5 && currentCard === 1) {
      // 在第一个卡片，返回上一步骤
      handleStepChange(currentStep - 1)
    } else if (currentStep > 1) {
      // 其他步骤，返回上一步骤
      handleStepChange(currentStep - 1)
    }
  }

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    getValues
  } = useForm<EnterpriseFormData>({
    defaultValues: {
      enterprise_identity: {
        enterprise_name: '',
        unified_social_credit_code: '',
        group_company: '',
        industry: '',
        industry_subdivision: '',
        park_name: '',
        risk_level: ''
      },
      enterprise_address: {
        province: '',
        city: '',
        district: '',
        detailed_address: '',
        postal_code: '',
        fax: '',
        longitude: '',
        latitude: ''
      },
      enterprise_contacts: {
        legal_representative_name: '',
        legal_representative_phone: '',
        env_officer_name: '',
        env_officer_position: '',
        env_officer_phone: '',
        emergency_contact_name: '',
        emergency_contact_position: '',
        emergency_contact_phone: '',
        landline_phone: '',
        enterprise_email: ''
      },
      enterprise_operation: {
        establishment_date: '',
        production_date: '',
        production_status: '',
        total_employees: 0,
        production_staff: 0,
        management_staff: 0,
        shift_system: '',
        daily_work_hours: '',
        annual_work_days: 0,
        land_area: 0,
        building_area: 0,
        total_investment: 0,
        env_investment: 0,
        business_types: []
      },
      enterprise_intro: {
        enterprise_intro: ''
      },
      // 步骤2：生产过程与风险物质
      products_info: [],
      raw_materials_info: [],
      energy_usage: {
        water_usage: '',
        industrial_water: '',
        domestic_water: '',
        electricity_usage: '',
        other_energy: []
      },
      production_process: {
        process_type: '',
        process_description: '',
        process_flow_file: '',
        process_nodes: []
      },
      storage_facilities: [],
      loading_operations: {
        has_loading: '',
        main_materials: [],
        loading_area_location: '',
        leak_prevention: ''
      },
      hazardous_chemicals: [],
      hazardous_waste: [],
      // 步骤3：环境信息
      natural_functional_area: {
        administrative_code: '',
        water_environment_function_area: '',
        atmospheric_environment_function_area: '',
        basin_name: '',
        nearest_surface_water: '',
        shortest_distance_to_water: '',
        relative_position_to_water: ''
      },
      environment_risk_receptors: [],
      wastewater_management: {
        drainage_system: '',
        has_production_wastewater: '',
        has_domestic_wastewater: '',
        treatment_facilities: [],
        has_accident_pool: '',
        accident_pool_volume: '',
        wastewater_outlets: []
      },
      waste_gas_management: {
        has_obvious_unorganized_gas: '',
        main_unorganized_areas: '',
        existing_control_measures: '',
        organized_waste_gas_sources: []
      },
      noise_and_solid_waste: {
        noise_sources: [],
        general_solid_wastes: []
      },
      accident_prevention_facilities: {
        has_rain_sewage_diversion: '',
        rain_sewage_diversion_description: '',
        has_key_area_bund: '',
        key_area_bund_location: '',
        hazardous_chemical_warehouse_seepage_control: '',
        key_valve_shut_off_facilities: ''
      },
      // 步骤4：环保手续与管理制度
      env_assessment_file: {
        eia_project_name: '',
        eia_document_number: '',
        eia_approval_date: '',
        eia_consistency_status: '',
        eia_report_upload: '',
        eia_approval_upload: ''
      },
      env_acceptance: {
        acceptance_type: '',
        acceptance_document_number: '',
        acceptance_date: '',
        acceptance_report_upload: '',
        acceptance_approval_upload: ''
      },
      discharge_permit: {
        discharge_permit_number: '',
        issuing_authority: '',
        permit_start_date: '',
        permit_end_date: '',
        permitted_pollutants: '',
        permit_scan_upload: ''
      },
      other_env_permits: [],
      hazardous_waste_agreement: {
        hazardous_waste_agreement_unit: '',
        hazardous_waste_unit_permit_number: '',
        hazardous_waste_agreement_start_date: '',
        hazardous_waste_agreement_end_date: '',
        hazardous_waste_categories: '',
        hazardous_waste_agreement_upload: ''
      },
      medical_waste_agreement: {
        medical_waste_agreement_unit: '',
        medical_waste_unit_permit_number: '',
        medical_waste_agreement_start_date: '',
        medical_waste_agreement_end_date: '',
        medical_waste_categories: '',
        medical_waste_agreement_upload: ''
      },
      emergency_plan_filing: {
        has_emergency_plan: '',
        has_emergency_plan_filed: '',
        emergency_plan_filing_number: '',
        emergency_plan_filing_date: '',
        emergency_plan_filing_upload: ''
      },
      management_systems: {
        has_risk_inspection_system: '',
        has_hazardous_chemicals_management_system: '',
        has_hazardous_waste_management_system: '',
        has_emergency_drill_training_system: '',
        management_system_files_upload: ''
      },
      penalty_accident_records: {
        has_administrative_penalty: '',
        administrative_penalty_details: '',
        has_environmental_accident: '',
        environmental_accident_details: ''
      },
      // 步骤5：应急管理与资源
      emergency_organization_and_contacts: {
        duty_phone_24h: '',
        internal_emergency_contacts: [],
        external_emergency_units: []
      },
      emergency_materials_and_equipment: {
        self_stored_materials: [],
        warehouse_count: '',
        warehouse_total_area: '',
        has_accident_pool: '',
        accident_pool_effective_volume: '',
        emergency_vehicle_count_and_type: ''
      },
      emergency_team_and_support: {
        has_internal_rescue_team: '',
        team_member_count: '',
        team_composition_description: '',
        has_special_emergency_budget: '',
        annual_emergency_budget_amount: ''
      },
      drills_and_training_records: {
        has_conducted_drills_recent_three_years: '',
        drill_records: [],
        annual_emergency_training_count: '',
        annual_environmental_training_count: '',
        employee_coverage_rate: '',
        includes_hazardous_chemical_safety: '',
        includes_environmental_emergency: ''
      },
      emergency_resource_survey_metadata: {
        survey_reference_year: '',
        survey_start_date: '',
        survey_end_date: '',
        survey_leader_name: '',
        survey_contact_person_and_phone: ''
      },
      // 其他信息
      env_permits: {
        env_assessment_no: '',
        acceptance_no: '',
        discharge_permit_no: '',
        has_emergency_plan: '',
        emergency_plan_code: ''
      },
      env_management: {
        env_management_system: '',
        env_officer: ''
      },
      env_receptor_info: {
        population_density: '',
        sensitive_distance: ''
      },
      env_pollutant_info: {
        main_pollutants: '',
        discharge_method: ''
      },
      env_prevention_facilities: {
        wastewater_facility: '',
        waste_gas_facility: ''
      },
      hazardous_materials: [],
      emergency_resources: [],
      emergency_orgs: [],
      external_emergency_contacts: []
    }
  })

  // 动态字段数组管理
  const {
    fields: materialFields,
    append: appendMaterial,
    remove: removeMaterial
  } = useFieldArray({
    control,
    name: 'hazardous_materials'
  })

  const {
    fields: resourceFields,
    append: appendResource,
    remove: removeResource
  } = useFieldArray({
    control,
    name: 'emergency_resources'
  })

  const {
    fields: orgFields,
    append: appendOrg,
    remove: removeOrg
  } = useFieldArray({
    control,
    name: 'emergency_orgs'
  })

  const {
    fields: externalContactFields,
    append: appendExternalContact,
    remove: removeExternalContact
  } = useFieldArray({
    control,
    name: 'external_emergency_contacts'
  })

  // 步骤2：生产过程与风险物质的动态字段数组管理
  const {
    fields: productFields,
    append: appendProduct,
    remove: removeProduct
  } = useFieldArray({
    control,
    name: 'products_info'
  })

  const {
    fields: rawMaterialFields,
    append: appendRawMaterial,
    remove: removeRawMaterial
  } = useFieldArray({
    control,
    name: 'raw_materials_info'
  })

  const {
    fields: storageFacilityFields,
    append: appendStorageFacility,
    remove: removeStorageFacility
  } = useFieldArray({
    control,
    name: 'storage_facilities'
  })

  const {
    fields: hazardousChemicalFields,
    append: appendHazardousChemical,
    remove: removeHazardousChemical
  } = useFieldArray({
    control,
    name: 'hazardous_chemicals'
  })

  const {
    fields: hazardousWasteFields,
    append: appendHazardousWaste,
    remove: removeHazardousWaste
  } = useFieldArray({
    control,
    name: 'hazardous_waste'
  })

  // 步骤3：环境信息的动态字段数组管理
  const {
    fields: environmentRiskReceptorFields,
    append: appendEnvironmentRiskReceptor,
    remove: removeEnvironmentRiskReceptor
  } = useFieldArray({
    control,
    name: 'environment_risk_receptors'
  })

  const {
    fields: wastewaterTreatmentFields,
    append: appendWastewaterTreatment,
    remove: removeWastewaterTreatment
  } = useFieldArray({
    control,
    name: 'wastewater_management.treatment_facilities'
  })

  const {
    fields: wastewaterOutletFields,
    append: appendWastewaterOutlet,
    remove: removeWastewaterOutlet
  } = useFieldArray({
    control,
    name: 'wastewater_management.wastewater_outlets'
  })

  const {
    fields: organizedWasteGasFields,
    append: appendOrganizedWasteGas,
    remove: removeOrganizedWasteGas
  } = useFieldArray({
    control,
    name: 'waste_gas_management.organized_waste_gas_sources'
  })

  const {
    fields: noiseSourceFields,
    append: appendNoiseSource,
    remove: removeNoiseSource
  } = useFieldArray({
    control,
    name: 'noise_and_solid_waste.noise_sources'
  })

  const {
    fields: generalSolidWasteFields,
    append: appendGeneralSolidWaste,
    remove: removeGeneralSolidWaste
  } = useFieldArray({
    control,
    name: 'noise_and_solid_waste.general_solid_wastes'
  })

  // 步骤4：环保手续与管理制度的动态字段数组管理
  const {
    fields: otherEnvPermitFields,
    append: appendOtherEnvPermit,
    remove: removeOtherEnvPermit
  } = useFieldArray({
    control,
    name: 'other_env_permits'
  })

  // 步骤5：应急管理与资源的动态字段数组管理
  const {
    fields: internalEmergencyContactFields,
    append: appendInternalEmergencyContact,
    remove: removeInternalEmergencyContact
  } = useFieldArray({
    control,
    name: 'emergency_organization_and_contacts.internal_emergency_contacts'
  })

  const {
    fields: externalEmergencyUnitFields,
    append: appendExternalEmergencyUnit,
    remove: removeExternalEmergencyUnit
  } = useFieldArray({
    control,
    name: 'emergency_organization_and_contacts.external_emergency_units'
  })

  const {
    fields: selfStoredEmergencyMaterialFields,
    append: appendSelfStoredEmergencyMaterial,
    remove: removeSelfStoredEmergencyMaterial
  } = useFieldArray({
    control,
    name: 'emergency_materials_and_equipment.self_stored_materials'
  })

  const {
    fields: drillRecordFields,
    append: appendDrillRecord,
    remove: removeDrillRecord
  } = useFieldArray({
    control,
    name: 'drills_and_training_records.drill_records'
  })

  // 切换折叠状态
  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  // 添加新行
  const addMaterial = () => {
    appendMaterial({
      id: Date.now().toString(),
      name: '',
      max_storage: '',
      annual_usage: '',
      storage_location: ''
    })
  }

  const addResource = () => {
    appendResource({
      id: Date.now().toString(),
      name: '',
      custom_resource_name: '',
      quantity: '',
      purpose: '',
      storage_location: '',
      custodian: '',
      custodian_contact: ''
    })
  }

  const addOrg = () => {
    appendOrg({
      id: Date.now().toString(),
      org_name: '',
      custom_org_name: '',
      responsible_person: '',
      contact_phone: '',
      department: '',
      duty_phone: ''
    })
  }

  const addExternalContact = () => {
    appendExternalContact({
      id: Date.now().toString(),
      unit_name: '',
      contact_method: '',
      custom_contact_method: '',
      custom_unit_name: ''
    })
  }

  // 步骤2：生产过程与风险物质的辅助函数
  const addProduct = () => {
    appendProduct({
      product_name: '',
      product_type: '',
      design_capacity: '',
      actual_annual_output: ''
    })
  }

  const addRawMaterial = () => {
    appendRawMaterial({
      material_name: '',
      cas_number: '',
      material_category: '',
      is_hazardous: '',
      hazard_categories: [],
      annual_usage: '',
      max_inventory: '',
      main_process_equipment: '',
      material_phase: ''
    })
  }

  const addStorageFacility = () => {
    appendStorageFacility({
      facility_name: '',
      facility_type: '',
      main_materials: [],
      rated_capacity: '',
      max_inventory: '',
      storage_method: '',
      has_bund: '',
      anti_seep_measures: '',
      location_description: ''
    })
  }

  const addHazardousChemical = () => {
    appendHazardousChemical({
      chemical_name: '',
      cas_number: '',
      hazard_category: '',
      location_unit: '',
      max_inventory: '',
      critical_quantity: '',
      material_phase: '',
      is_major_hazard: '',
      msds_file: ''
    })
  }

  const addHazardousWaste = () => {
    appendHazardousWaste({
      waste_name: '',
      waste_category: '',
      waste_code: '',
      source_process: '',
      hazard_characteristics: [],
      storage_location: '',
      storage_method: '',
      max_storage: '',
      max_storage_days: '',
      disposal_company: ''
    })
  }

  // 步骤3：环境信息的辅助函数
  const addEnvironmentRiskReceptor = () => {
    appendEnvironmentRiskReceptor({
      id: Date.now().toString(),
      environment_element: '',
      receptor_type: '',
      receptor_name: '',
      relative_position: '',
      distance_to_boundary: '',
      function_and_scale: '',
      environment_quality_target: ''
    })
  }

  const addWastewaterTreatment = () => {
    appendWastewaterTreatment({
      facility_name: '',
      service_scope: '',
      process_type: '',
      design_capacity: '',
      actual_treatment_volume: '',
      discharge_destination: ''
    })
  }

  const addWastewaterOutlet = () => {
    appendWastewaterOutlet({
      outlet_name: '',
      outlet_type: '',
      discharge_destination: '',
      has_online_monitoring: ''
    })
  }

  const addOrganizedWasteGas = () => {
    appendOrganizedWasteGas({
      source_name: '',
      corresponding_process: '',
      main_pollutants: [],
      treatment_facility_type: '',
      exhaust_stack_number: '',
      exhaust_stack_height: '',
      discharge_destination: '',
      has_online_monitoring: ''
    })
  }

  const addNoiseSource = () => {
    appendNoiseSource({
      noise_source_name: '',
      location: '',
      noise_control_measures: ''
    })
  }

  const addGeneralSolidWaste = () => {
    appendGeneralSolidWaste({
      waste_name: '',
      source_process: '',
      waste_nature: '',
      annual_generation: '',
      storage_method: '',
      disposal_method: '',
      destination_unit: ''
    })
  }

  // 步骤4：环保手续与管理制度的辅助函数
  const addOtherEnvPermit = () => {
    appendOtherEnvPermit({
      certificate_type: '',
      certificate_number: '',
      issuing_authority: '',
      validity_period: '',
      scan_file_upload: ''
    })
  }

  // 步骤5：应急管理与资源的辅助函数
  const addInternalEmergencyContact = () => {
    appendInternalEmergencyContact({
      id: Date.now().toString(),
      organization_role: '',
      department_name: '',
      contact_name: '',
      position: '',
      mobile_phone: ''
    })
  }

  const addExternalEmergencyUnit = () => {
    appendExternalEmergencyUnit({
      id: Date.now().toString(),
      unit_category: '',
      unit_name: '',
      contact_phone: '',
      emergency_capability_description: '',
      has_cooperation_agreement: ''
    })
  }

  const addSelfStoredEmergencyMaterial = () => {
    appendSelfStoredEmergencyMaterial({
      id: Date.now().toString(),
      material_name: '',
      unit: '',
      quantity: '',
      purpose: '',
      storage_location: '',
      custodian_name: '',
      custodian_phone: ''
    })
  }

  const addDrillRecord = () => {
    appendDrillRecord({
      id: Date.now().toString(),
      drill_date: '',
      drill_type: '',
      drill_description: '',
      participants_count: '',
      drill_effectiveness_evaluation: ''
    })
  }

  // 表单提交
  const onSubmit = async (data: EnterpriseFormData) => {
    try {
      console.log('📋 企业信息收集表单数据:', JSON.stringify(data, null, 2))
      
      // 添加详细的调试日志
      console.log('🔍 企业身份信息详情:', {
        enterprise_identity: data.enterprise_identity,
        enterprise_name: data.enterprise_identity?.enterprise_name,
        isEnterpriseNameEmpty: !data.enterprise_identity?.enterprise_name,
        isEnterpriseIdentityNull: !data.enterprise_identity
      })
      
      // 检查当前认证状态
      const token = useUserStore.getState().token
      console.log('🔍 当前认证状态:', {
        hasToken: !!token,
        tokenPreview: token ? `${token.substring(0, 20)}...` : 'null',
        isAuthenticated: useUserStore.getState().isAuthenticated
      })

      // 只在步骤1、步骤2、步骤3、步骤4或步骤5的最后一个卡片时才保存数据
      if ((currentStep === 1 && currentCard === enterpriseBasicCards.length) ||
          (currentStep === 2 && currentCard === productionRiskCards.length) ||
          (currentStep === 3 && currentCard === environmentInfoCards.length) ||
          (currentStep === 4 && currentCard === environmentalPermitsCards.length) ||
          (currentStep === 5 && currentCard === emergencyManagementCards.length)) {
        console.log('💾 开始保存企业信息...')
        
        // 添加数据验证
        if (!data.enterprise_identity || !data.enterprise_identity.enterprise_name) {
          console.error('❌ 企业名称为空，这可能导致422错误')
          alert('企业名称为必填项，请填写后再保存')
          return
        }
        
        // API调用保存企业信息
        const response = await apiClient.post('/enterprise/info', {
          ...data,
          project_id: id
        })
        
        console.log('✅ 企业信息保存成功:', response.data)
        alert('企业信息保存成功！')
      } else {
        console.log('⏭️ 跳过保存，直接进入下一步')
      }

      // 跳转到下一步
      handleNext()
    } catch (error) {
      console.error('❌ 保存失败:', error)
      console.error('❌ 错误详情:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data
      })
      alert(`保存失败: ${error.response?.data?.detail || error.message || '未知错误'}`)
    }
  }

  // 渲染企业基本信息卡片
  const renderEnterpriseBasicCard = () => {
    switch (currentCard) {
      case 1: // 企业身份信息
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🏢</span>
              <h2 className="text-xl font-bold text-gray-900">企业身份信息</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    企业名称（全称） <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_identity.enterprise_name', { required: '企业名称为必填项' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入企业名称"
                  />
                  {errors.enterprise_identity?.enterprise_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.enterprise_identity.enterprise_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    统一社会信用代码
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_identity.unified_social_credit_code')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入统一社会信用代码"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    所属集团 / 母公司（选填）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_identity.group_company')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入所属集团/母公司"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    所在行业 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_identity.industry', { required: '所在行业为必填项' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入所在行业"
                  />
                  {errors.enterprise_identity?.industry && (
                    <p className="mt-1 text-sm text-red-600">{errors.enterprise_identity.industry.message}</p>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  行业细分说明（自由文本，用来写"医疗机构、制药、危废处置、加油站"等）
                </label>
                <textarea
                  {...register('enterprise_identity.industry_subdivision')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请输入行业细分说明"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  所在园区 / 工业区名称（选填）
                </label>
                <input
                  type="text"
                  {...register('enterprise_identity.park_name')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请输入所在园区/工业区名称"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  企业风险级别（下拉：一般 / 较大 / 重大，允许先空，后端可计算再回填）
                </label>
                <select
                  {...register('enterprise_identity.risk_level')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">请选择</option>
                  <option value="一般">一般</option>
                  <option value="较大">较大</option>
                  <option value="重大">重大</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 2: // 地址与空间信息
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📍</span>
              <h2 className="text-xl font-bold text-gray-900">地址与空间信息</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    所在省
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.province')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入所在省"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    所在市
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.city')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入所在市"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    所在区 / 县
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.district')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入所在区/县"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    邮编
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.postal_code')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入邮编"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  详细地址
                </label>
                <input
                  type="text"
                  {...register('enterprise_address.detailed_address')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请输入详细地址"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    传真
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.fax')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入传真"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    企业中心点经度（WGS84）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.longitude')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入企业中心点经度"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    企业中心点纬度（WGS84）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_address.latitude')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入企业中心点纬度"
                  />
                </div>
              </div>
            </div>
          </div>
        )

      case 3: // 联系人与职责
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">👥</span>
              <h2 className="text-xl font-bold text-gray-900">联系人与职责</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    法定代表人姓名
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.legal_representative_name')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入法定代表人姓名"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    法定代表人手机
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.legal_representative_phone')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入法定代表人手机"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    环保负责人姓名
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.env_officer_name')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入环保负责人姓名"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    环保负责人职务 / 部门
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.env_officer_position')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入环保负责人职务/部门"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    环保负责人手机
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.env_officer_phone')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入环保负责人手机"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    应急联系人姓名
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.emergency_contact_name')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入应急联系人姓名"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    应急联系人职务
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.emergency_contact_position')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入应急联系人职务"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    应急联系人手机
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.emergency_contact_phone')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入应急联系人手机"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    固定电话（总机或值班电话）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_contacts.landline_phone')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入固定电话"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    企业联系邮箱
                  </label>
                  <input
                    type="email"
                    {...register('enterprise_contacts.enterprise_email')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入企业联系邮箱"
                  />
                </div>
              </div>
            </div>
          </div>
        )

      case 4: // 企业运营概况
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📊</span>
              <h2 className="text-xl font-bold text-gray-900">企业运营概况</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    成立时间（年月）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_operation.establishment_date')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入成立时间"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    建成 / 投产时间（年月，选填）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_operation.production_date')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入建成/投产时间"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    企业在产状态
                  </label>
                  <select
                    {...register('enterprise_operation.production_status')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="在产">在产</option>
                    <option value="停产">停产</option>
                    <option value="在建改扩建">在建改扩建</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    员工总数（人）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.total_employees', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入员工总数"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    生产人员数量（人）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.production_staff', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入生产人员数量"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    管理及后勤人员数量（人，可选）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.management_staff', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入管理及后勤人员数量"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    班制
                  </label>
                  <select
                    {...register('enterprise_operation.shift_system')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="单班">单班</option>
                    <option value="两班">两班</option>
                    <option value="三班">三班</option>
                    <option value="其它">其它</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    日工作时间（小时 / 班）
                  </label>
                  <input
                    type="text"
                    {...register('enterprise_operation.daily_work_hours')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入日工作时间"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    年运行天数（d/a）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.annual_work_days', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入年运行天数"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    占地面积（m²）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.land_area', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入占地面积"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    总建筑面积（m²）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.building_area', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入总建筑面积"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    总投资额（万元）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.total_investment', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入总投资额"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    环保投资额（万元，选填）
                  </label>
                  <input
                    type="number"
                    {...register('enterprise_operation.env_investment', { valueAsNumber: true })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入环保投资额"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  主要业务 / 服务类型（多选 + 补充说明）
                </label>
                <textarea
                  {...register('enterprise_operation.business_types')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请输入主要业务/服务类型"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>
            </div>
          </div>
        )

      case 5: // 企业简介文本
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📝</span>
              <h2 className="text-xl font-bold text-gray-900">企业简介文本（用于润色）</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  企业简介原文（多行文本，允许企业粘贴官网介绍）
                </label>
                <textarea
                  {...register('enterprise_intro.enterprise_intro')}
                  rows={8}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请输入企业简介原文"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  // 渲染步骤2：生产过程与风险物质的卡片
  const renderProductionRiskCard = () => {
    switch (currentCard) {
      case 1: // 产品与产能
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📦</span>
              <h2 className="text-xl font-bold text-gray-900">产品与产能</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">产品列表</h3>
                <button
                  type="button"
                  onClick={addProduct}
                  className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                >
                  <PlusIcon className="mr-1" />
                  添加产品
                </button>
              </div>
              
              {productFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-md font-medium text-gray-800">产品 {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeProduct(index)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        产品名称
                      </label>
                      <input
                        type="text"
                        {...register(`products_info.${index}.product_name`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入产品名称"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        产品类型
                      </label>
                      <select
                        {...register(`products_info.${index}.product_type`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="主产品">主产品</option>
                        <option value="副产品">副产品</option>
                        <option value="中间产品">中间产品</option>
                        <option value="副产物">副产物</option>
                        <option value="公用工程">公用工程</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        设计产能（单位 + 数值）
                      </label>
                      <input
                        type="text"
                        {...register(`products_info.${index}.design_capacity`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入设计产能"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        实际年产量（最近一年）
                      </label>
                      <input
                        type="text"
                        {...register(`products_info.${index}.actual_annual_output`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入实际年产量"
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              {productFields.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  暂无产品信息，请点击"添加产品"按钮添加
                </div>
              )}
            </div>
          </div>
        )

      case 2: // 原辅料与能源
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">⚡</span>
              <h2 className="text-xl font-bold text-gray-900">原辅料与能源</h2>
            </div>
            
            <div className="space-y-6">
              {/* 能源使用情况 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">能源使用情况</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      用水量（吨/年）
                    </label>
                    <input
                      type="text"
                      {...register('energy_usage.water_usage')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入用水量"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      其中工业用水量（吨/年）
                    </label>
                    <input
                      type="text"
                      {...register('energy_usage.industrial_water')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入工业用水量"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      其中生活用水量（吨/年）
                    </label>
                    <input
                      type="text"
                      {...register('energy_usage.domestic_water')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入生活用水量"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      用电量（度/年）
                    </label>
                    <input
                      type="text"
                      {...register('energy_usage.electricity_usage')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入用电量"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    其他能源使用（多选）
                  </label>
                  <textarea
                    {...register('energy_usage.other_energy')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                    placeholder="请输入其他能源使用情况"
                    style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                  />
                </div>
              </div>
              
              {/* 原辅料信息 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">原辅料信息</h3>
                  <button
                    type="button"
                    onClick={addRawMaterial}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加原辅料
                  </button>
                </div>
                
                {rawMaterialFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">原辅料 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeRawMaterial(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          原辅料名称
                        </label>
                        <input
                          type="text"
                          {...register(`raw_materials_info.${index}.material_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入原辅料名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          CAS号
                        </label>
                        <input
                          type="text"
                          {...register(`raw_materials_info.${index}.cas_number`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入CAS号"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          原辅料类别
                        </label>
                        <select
                          {...register(`raw_materials_info.${index}.material_category`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="原料">原料</option>
                          <option value="辅料">辅料</option>
                          <option value="催化剂">催化剂</option>
                          <option value="溶剂">溶剂</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          是否为危险化学品
                        </label>
                        <select
                          {...register(`raw_materials_info.${index}.is_hazardous`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="是">是</option>
                          <option value="否">否</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          年使用量（单位 + 数值）
                        </label>
                        <input
                          type="text"
                          {...register(`raw_materials_info.${index}.annual_usage`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入年使用量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          最大库存量（单位 + 数值）
                        </label>
                        <input
                          type="text"
                          {...register(`raw_materials_info.${index}.max_inventory`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入最大库存量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          主要工艺设备
                        </label>
                        <input
                          type="text"
                          {...register(`raw_materials_info.${index}.main_process_equipment`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入主要工艺设备"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          物料相态
                        </label>
                        <select
                          {...register(`raw_materials_info.${index}.material_phase`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="固态">固态</option>
                          <option value="液态">液态</option>
                          <option value="气态">气态</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
                
                {rawMaterialFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无原辅料信息，请点击"添加原辅料"按钮添加
                  </div>
                )}
              </div>
            </div>
          </div>
        )

      case 3: // 生产工艺与工序
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">⚙️</span>
              <h2 className="text-xl font-bold text-gray-900">生产工艺与工序</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  工艺类型
                </label>
                <select
                  {...register('production_process.process_type')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">请选择</option>
                  <option value="物理工艺">物理工艺</option>
                  <option value="化学工艺">化学工艺</option>
                  <option value="生物工艺">生物工艺</option>
                  <option value="混合工艺">混合工艺</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  工艺描述
                </label>
                <textarea
                  {...register('production_process.process_description')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请描述生产工艺流程"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  工艺流程文件
                </label>
                <input
                  type="text"
                  {...register('production_process.process_flow_file')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请上传或输入工艺流程文件路径"
                />
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">工艺节点信息</h3>
                <p className="text-gray-600 mb-4">请在此处描述各工艺节点的详细信息</p>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">
                    工艺节点包括：节点名称、节点功能、关键设备、是否涉及危险化学品等信息。
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    此部分可在后续版本中扩展为动态表单，目前可使用文本框描述。
                  </p>
                </div>
              </div>
            </div>
          </div>
        )

      case 4: // 储存与装卸设施
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🏭</span>
              <h2 className="text-xl font-bold text-gray-900">储存与装卸设施</h2>
            </div>
            
            <div className="space-y-6">
              {/* 储存设施 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">储存设施</h3>
                  <button
                    type="button"
                    onClick={addStorageFacility}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加储存设施
                  </button>
                </div>
                
                {storageFacilityFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">储存设施 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeStorageFacility(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          设施名称
                        </label>
                        <input
                          type="text"
                          {...register(`storage_facilities.${index}.facility_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入设施名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          设施类型
                        </label>
                        <select
                          {...register(`storage_facilities.${index}.facility_type`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="储罐">储罐</option>
                          <option value="仓库">仓库</option>
                          <option value="堆场">堆场</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          额定容量（单位 + 数值）
                        </label>
                        <input
                          type="text"
                          {...register(`storage_facilities.${index}.rated_capacity`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入额定容量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          最大库存量（单位 + 数值）
                        </label>
                        <input
                          type="text"
                          {...register(`storage_facilities.${index}.max_inventory`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入最大库存量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          储存方式
                        </label>
                        <select
                          {...register(`storage_facilities.${index}.storage_method`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="常温常压">常温常压</option>
                          <option value="低温">低温</option>
                          <option value="高压">高压</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          是否有围堰
                        </label>
                        <select
                          {...register(`storage_facilities.${index}.has_bund`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="是">是</option>
                          <option value="否">否</option>
                        </select>
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        防渗措施
                      </label>
                      <textarea
                        {...register(`storage_facilities.${index}.anti_seep_measures`)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                        placeholder="请描述防渗措施"
                        style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                      />
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        位置描述
                      </label>
                      <textarea
                        {...register(`storage_facilities.${index}.location_description`)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                        placeholder="请描述设施位置"
                        style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                      />
                    </div>
                  </div>
                ))}
                
                {storageFacilityFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无储存设施信息，请点击"添加储存设施"按钮添加
                  </div>
                )}
              </div>
              
              {/* 装卸操作 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">装卸操作</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否有装卸操作
                    </label>
                    <select
                      {...register('loading_operations.has_loading')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      装卸区域位置
                    </label>
                    <input
                      type="text"
                      {...register('loading_operations.loading_area_location')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入装卸区域位置"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      泄漏防范措施
                    </label>
                    <textarea
                      {...register('loading_operations.leak_prevention')}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请描述泄漏防范措施"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 5: // 危险化学品明细
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">☢️</span>
              <h2 className="text-xl font-bold text-gray-900">危险化学品明细</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">危险化学品列表</h3>
                <button
                  type="button"
                  onClick={addHazardousChemical}
                  className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                >
                  <PlusIcon className="mr-1" />
                  添加危险化学品
                </button>
              </div>
              
              {hazardousChemicalFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-md font-medium text-gray-800">危险化学品 {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeHazardousChemical(index)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        化学品名称
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_chemicals.${index}.chemical_name`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入化学品名称"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        CAS号
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_chemicals.${index}.cas_number`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入CAS号"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        危险性类别
                      </label>
                      <select
                        {...register(`hazardous_chemicals.${index}.hazard_category`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="爆炸品">爆炸品</option>
                        <option value="压缩气体和液化气体">压缩气体和液化气体</option>
                        <option value="易燃液体">易燃液体</option>
                        <option value="易燃固体">易燃固体</option>
                        <option value="自燃物品和遇湿易燃物品">自燃物品和遇湿易燃物品</option>
                        <option value="氧化剂和有机过氧化物">氧化剂和有机过氧化物</option>
                        <option value="有毒品">有毒品</option>
                        <option value="放射性物品">放射性物品</option>
                        <option value="腐蚀品">腐蚀品</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        所在单元/装置
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_chemicals.${index}.location_unit`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入所在单元/装置"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        最大存在量（单位 + 数值）
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_chemicals.${index}.max_inventory`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入最大存在量"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        临界量（单位 + 数值）
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_chemicals.${index}.critical_quantity`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入临界量"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        物料相态
                      </label>
                      <select
                        {...register(`hazardous_chemicals.${index}.material_phase`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="固态">固态</option>
                        <option value="液态">液态</option>
                        <option value="气态">气态</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        是否构成重大危险源
                      </label>
                      <select
                        {...register(`hazardous_chemicals.${index}.is_major_hazard`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="是">是</option>
                        <option value="否">否</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      MSDS文件
                    </label>
                    <input
                      type="text"
                      {...register(`hazardous_chemicals.${index}.msds_file`)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请上传或输入MSDS文件路径"
                    />
                  </div>
                </div>
              ))}
              
              {hazardousChemicalFields.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  暂无危险化学品信息，请点击"添加危险化学品"按钮添加
                </div>
              )}
            </div>
          </div>
        )

      case 6: // 危险废物与其他风险物质
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🗑️</span>
              <h2 className="text-xl font-bold text-gray-900">危险废物与其他风险物质</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">危险废物列表</h3>
                <button
                  type="button"
                  onClick={addHazardousWaste}
                  className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                >
                  <PlusIcon className="mr-1" />
                  添加危险废物
                </button>
              </div>
              
              {hazardousWasteFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-md font-medium text-gray-800">危险废物 {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeHazardousWaste(index)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        废物名称
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.waste_name`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入废物名称"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        废物类别
                      </label>
                      <select
                        {...register(`hazardous_waste.${index}.waste_category`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="HW01 医疗废物">HW01 医疗废物</option>
                        <option value="HW02 医药废物">HW02 医药废物</option>
                        <option value="HW03 废药物、药品">HW03 废药物、药品</option>
                        <option value="HW04 农药废物">HW04 农药废物</option>
                        <option value="HW05 木材防腐剂废物">HW05 木材防腐剂废物</option>
                        <option value="HW06 废有机溶剂与含有机溶剂废物">HW06 废有机溶剂与含有机溶剂废物</option>
                        <option value="HW07 废矿物油与含矿物油废物">HW07 废矿物油与含矿物油废物</option>
                        <option value="HW08 废矿物油与含矿物油废物">HW08 废矿物油与含矿物油废物</option>
                        <option value="HW09 油/水、烃/水混合物或乳化液">HW09 油/水、烃/水混合物或乳化液</option>
                        <option value="HW10 含多氯联苯废物">HW10 含多氯联苯废物</option>
                        <option value="HW11 精(蒸)馏残渣">HW11 精(蒸)馏残渣</option>
                        <option value="HW12 染料、涂料废物">HW12 染料、涂料废物</option>
                        <option value="HW13 有机树脂类废物">HW13 有机树脂类废物</option>
                        <option value="HW14 新化学药品废物">HW14 新化学药品废物</option>
                        <option value="HW15 爆炸性废物">HW15 爆炸性废物</option>
                        <option value="HW16 感光材料废物">HW16 感光材料废物</option>
                        <option value="HW17 表面处理废物">HW17 表面处理废物</option>
                        <option value="HW18 焚烧处置残渣">HW18 焚烧处置残渣</option>
                        <option value="HW19 含金属羰基化合物废物">HW19 含金属羰基化合物废物</option>
                        <option value="HW20 含铍废物">HW20 含铍废物</option>
                        <option value="HW21 含铬废物">HW21 含铬废物</option>
                        <option value="HW22 含铜废物">HW22 含铜废物</option>
                        <option value="HW23 含锌废物">HW23 含锌废物</option>
                        <option value="HW24 含砷废物">HW24 含砷废物</option>
                        <option value="HW25 含硒废物">HW25 含硒废物</option>
                        <option value="HW26 含镉废物">HW26 含镉废物</option>
                        <option value="HW27 含锑废物">HW27 含锑废物</option>
                        <option value="HW28 含碲废物">HW28 含碲废物</option>
                        <option value="HW29 含汞废物">HW29 含汞废物</option>
                        <option value="HW30 含铊废物">HW30 含铊废物</option>
                        <option value="HW31 含铅废物">HW31 含铅废物</option>
                        <option value="HW32 无机氟化物废物">HW32 无机氟化物废物</option>
                        <option value="HW33 无机氰化物废物">HW33 无机氰化物废物</option>
                        <option value="HW34 废酸">HW34 废酸</option>
                        <option value="HW35 废碱">HW35 废碱</option>
                        <option value="HW36 石棉废物">HW36 石棉废物</option>
                        <option value="HW37 有机磷化合物废物">HW37 有机磷化合物废物</option>
                        <option value="HW38 有机氰化物废物">HW38 有机氰化物废物</option>
                        <option value="HW39 含酚废物">HW39 含酚废物</option>
                        <option value="HW40 含醚废物">HW40 含醚废物</option>
                        <option value="HW41 废卤化有机溶剂">HW41 废卤化有机溶剂</option>
                        <option value="HW42 废有机溶剂">HW42 废有机溶剂</option>
                        <option value="HW43 含多氯苯并呋喃类废物">HW43 含多氯苯并呋喃类废物</option>
                        <option value="HW44 含多氯苯并二恶英废物">HW44 含多氯苯并二恶英废物</option>
                        <option value="HW45 含有机卤化物废物">HW45 含有机卤化物废物</option>
                        <option value="HW46 含镍废物">HW46 含镍废物</option>
                        <option value="HW47 含钡废物">HW47 含钡废物</option>
                        <option value="HW48 其他废物">HW48 其他废物</option>
                        <option value="HW49 其他废物">HW49 其他废物</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        废物代码
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.waste_code`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入废物代码"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        产生工序/来源
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.source_process`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入产生工序/来源"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        贮存位置
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.storage_location`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入贮存位置"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        贮存方式
                      </label>
                      <select
                        {...register(`hazardous_waste.${index}.storage_method`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="容器贮存">容器贮存</option>
                        <option value="仓库贮存">仓库贮存</option>
                        <option value="堆场贮存">堆场贮存</option>
                        <option value="其他">其他</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        最大贮存量（单位 + 数值）
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.max_storage`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入最大贮存量"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        最长贮存天数（天）
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.max_storage_days`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入最长贮存天数"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        处置单位
                      </label>
                      <input
                        type="text"
                        {...register(`hazardous_waste.${index}.disposal_company`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入处置单位"
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              {hazardousWasteFields.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  暂无危险废物信息，请点击"添加危险废物"按钮添加
                </div>
              )}
            </div>
          </div>
        )

      default:
        return null
    }
  }

  // 渲染步骤3：环境信息的卡片
  const renderEnvironmentInfoCard = () => {
    switch (currentCard) {
      case 1: // 自然与功能区信息
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🌍</span>
              <h2 className="text-xl font-bold text-gray-900">自然与功能区信息</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    行政区划代码
                  </label>
                  <input
                    type="text"
                    {...register('natural_functional_area.administrative_code')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入行政区划代码"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    水环境功能区
                  </label>
                  <select
                    {...register('natural_functional_area.water_environment_function_area')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="Ⅰ类">Ⅰ类</option>
                    <option value="Ⅱ类">Ⅱ类</option>
                    <option value="Ⅲ类">Ⅲ类</option>
                    <option value="Ⅳ类">Ⅳ类</option>
                    <option value="Ⅴ类">Ⅴ类</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    大气环境功能区
                  </label>
                  <select
                    {...register('natural_functional_area.atmospheric_environment_function_area')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="一类区">一类区</option>
                    <option value="二类区">二类区</option>
                    <option value="三类区">三类区</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    流域名称
                  </label>
                  <input
                    type="text"
                    {...register('natural_functional_area.basin_name')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入流域名称"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    最近地表水体
                  </label>
                  <input
                    type="text"
                    {...register('natural_functional_area.nearest_surface_water')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入最近地表水体"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    与水体最近距离（m）
                  </label>
                  <input
                    type="text"
                    {...register('natural_functional_area.shortest_distance_to_water')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入与水体最近距离"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  与水体相对位置
                </label>
                <select
                  {...register('natural_functional_area.relative_position_to_water')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">请选择</option>
                  <option value="上游">上游</option>
                  <option value="中游">中游</option>
                  <option value="下游">下游</option>
                  <option value="左岸">左岸</option>
                  <option value="右岸">右岸</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 2: // 周边环境风险受体
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🏘️</span>
              <h2 className="text-xl font-bold text-gray-900">周边环境风险受体</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">环境风险受体列表</h3>
                <button
                  type="button"
                  onClick={addEnvironmentRiskReceptor}
                  className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                >
                  <PlusIcon className="mr-1" />
                  添加风险受体
                </button>
              </div>
              
              {environmentRiskReceptorFields.map((field, index) => (
                <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="text-md font-medium text-gray-800">风险受体 {index + 1}</h4>
                    <button
                      type="button"
                      onClick={() => removeEnvironmentRiskReceptor(index)}
                      className="text-red-500 hover:text-red-700 transition-colors"
                    >
                      <TrashIcon />
                    </button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        环境要素
                      </label>
                      <select
                        {...register(`environment_risk_receptors.${index}.environment_element`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="大气环境">大气环境</option>
                        <option value="地表水环境">地表水环境</option>
                        <option value="地下水环境">地下水环境</option>
                        <option value="土壤环境">土壤环境</option>
                        <option value="声环境">声环境</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        受体类型
                      </label>
                      <select
                        {...register(`environment_risk_receptors.${index}.receptor_type`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="居民区">居民区</option>
                        <option value="学校">学校</option>
                        <option value="医院">医院</option>
                        <option value="饮用水源">饮用水源</option>
                        <option value="自然保护区">自然保护区</option>
                        <option value="农田">农田</option>
                        <option value="其他">其他</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        受体名称
                      </label>
                      <input
                        type="text"
                        {...register(`environment_risk_receptors.${index}.receptor_name`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入受体名称"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        相对位置
                      </label>
                      <input
                        type="text"
                        {...register(`environment_risk_receptors.${index}.relative_position`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入相对位置"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        距厂界距离（m）
                      </label>
                      <input
                        type="text"
                        {...register(`environment_risk_receptors.${index}.distance_to_boundary`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入距厂界距离"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        功能与规模
                      </label>
                      <input
                        type="text"
                        {...register(`environment_risk_receptors.${index}.function_and_scale`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入功能与规模"
                      />
                    </div>
                  </div>

                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      环境质量目标
                    </label>
                    <textarea
                      {...register(`environment_risk_receptors.${index}.environment_quality_target`)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请输入环境质量目标"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>
                </div>
              ))}
              
              {environmentRiskReceptorFields.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  暂无环境风险受体信息，请点击"添加风险受体"按钮添加
                </div>
              )}
            </div>
          </div>
        )

      case 3: // 废水产生与治理
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">💧</span>
              <h2 className="text-xl font-bold text-gray-900">废水产生与治理</h2>
            </div>
            
            <div className="space-y-6">
              {/* 基本情况 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">废水基本情况</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      排水体制
                    </label>
                    <select
                      {...register('wastewater_management.drainage_system')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="雨污分流">雨污分流</option>
                      <option value="雨污合流">雨污合流</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否有生产废水
                    </label>
                    <select
                      {...register('wastewater_management.has_production_wastewater')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否有生活废水
                    </label>
                    <select
                      {...register('wastewater_management.has_domestic_wastewater')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否有事故应急池
                    </label>
                    <select
                      {...register('wastewater_management.has_accident_pool')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      事故应急池容积（m³）
                    </label>
                    <input
                      type="text"
                      {...register('wastewater_management.accident_pool_volume')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入事故应急池容积"
                    />
                  </div>
                </div>
              </div>
              
              {/* 废水处理设施 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">废水处理设施</h3>
                  <button
                    type="button"
                    onClick={addWastewaterTreatment}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加处理设施
                  </button>
                </div>
                
                {wastewaterTreatmentFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">处理设施 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeWastewaterTreatment(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          设施名称
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.treatment_facilities.${index}.facility_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入设施名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          服务范围
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.treatment_facilities.${index}.service_scope`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入服务范围"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          处理工艺类型
                        </label>
                        <select
                          {...register(`wastewater_management.treatment_facilities.${index}.process_type`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="物化处理">物化处理</option>
                          <option value="生化处理">生化处理</option>
                          <option value="深度处理">深度处理</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          设计处理能力（m³/d）
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.treatment_facilities.${index}.design_capacity`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入设计处理能力"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          实际处理量（m³/d）
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.treatment_facilities.${index}.actual_treatment_volume`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入实际处理量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排放去向
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.treatment_facilities.${index}.discharge_destination`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入排放去向"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                {wastewaterTreatmentFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无废水处理设施信息，请点击"添加处理设施"按钮添加
                  </div>
                )}
              </div>
              
              {/* 废水排口 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">废水排口</h3>
                  <button
                    type="button"
                    onClick={addWastewaterOutlet}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加排口
                  </button>
                </div>
                
                {wastewaterOutletFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">废水排口 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeWastewaterOutlet(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排口名称
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.wastewater_outlets.${index}.outlet_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入排口名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排口类型
                        </label>
                        <select
                          {...register(`wastewater_management.wastewater_outlets.${index}.outlet_type`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="总排口">总排口</option>
                          <option value="车间排口">车间排口</option>
                          <option value="雨水排口">雨水排口</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排放去向
                        </label>
                        <input
                          type="text"
                          {...register(`wastewater_management.wastewater_outlets.${index}.discharge_destination`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入排放去向"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          是否有在线监测
                        </label>
                        <select
                          {...register(`wastewater_management.wastewater_outlets.${index}.has_online_monitoring`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="是">是</option>
                          <option value="否">否</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
                
                {wastewaterOutletFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无废水排口信息，请点击"添加排口"按钮添加
                  </div>
                )}
              </div>
            </div>
          </div>
        )

      case 4: // 废气产生与治理
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">💨</span>
              <h2 className="text-xl font-bold text-gray-900">废气产生与治理</h2>
            </div>
            
            <div className="space-y-6">
              {/* 基本情况 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">无组织废气概况</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否有明显无组织废气
                    </label>
                    <select
                      {...register('waste_gas_management.has_obvious_unorganized_gas')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      主要无组织废气区域
                    </label>
                    <textarea
                      {...register('waste_gas_management.main_unorganized_areas')}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请描述主要无组织废气区域"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      现有控制措施
                    </label>
                    <textarea
                      {...register('waste_gas_management.existing_control_measures')}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请描述现有控制措施"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>
                </div>
              </div>
              
              {/* 有组织废气源 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">有组织废气源</h3>
                  <button
                    type="button"
                    onClick={addOrganizedWasteGas}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加废气源
                  </button>
                </div>
                
                {organizedWasteGasFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">废气源 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeOrganizedWasteGas(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          废气源名称
                        </label>
                        <input
                          type="text"
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.source_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入废气源名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          对应工序
                        </label>
                        <input
                          type="text"
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.corresponding_process`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入对应工序"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          主要污染物
                        </label>
                        <textarea
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.main_pollutants`)}
                          rows={2}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                          placeholder="请输入主要污染物"
                          style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          处理设施类型
                        </label>
                        <select
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.treatment_facility_type`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="除尘设施">除尘设施</option>
                          <option value="脱硫设施">脱硫设施</option>
                          <option value="脱硝设施">脱硝设施</option>
                          <option value="VOCs处理设施">VOCs处理设施</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排气筒编号
                        </label>
                        <input
                          type="text"
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.exhaust_stack_number`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入排气筒编号"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排气筒高度（m）
                        </label>
                        <input
                          type="text"
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.exhaust_stack_height`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入排气筒高度"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          排放去向
                        </label>
                        <input
                          type="text"
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.discharge_destination`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入排放去向"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          是否有在线监测
                        </label>
                        <select
                          {...register(`waste_gas_management.organized_waste_gas_sources.${index}.has_online_monitoring`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="是">是</option>
                          <option value="否">否</option>
                        </select>
                      </div>
                    </div>
                  </div>
                ))}
                
                {organizedWasteGasFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无有组织废气源信息，请点击"添加废气源"按钮添加
                  </div>
                )}
              </div>
            </div>
          </div>
        )

      case 5: // 噪声与固体废物
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🔊</span>
              <h2 className="text-xl font-bold text-gray-900">噪声与固体废物</h2>
            </div>
            
            <div className="space-y-6">
              {/* 噪声源 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">主要噪声源</h3>
                  <button
                    type="button"
                    onClick={addNoiseSource}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加噪声源
                  </button>
                </div>
                
                {noiseSourceFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">噪声源 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeNoiseSource(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          噪声源名称
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.noise_sources.${index}.noise_source_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入噪声源名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          位置
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.noise_sources.${index}.location`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入位置"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          噪声控制措施
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.noise_sources.${index}.noise_control_measures`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入噪声控制措施"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                {noiseSourceFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无噪声源信息，请点击"添加噪声源"按钮添加
                  </div>
                )}
              </div>
              
              {/* 一般固体废物 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">一般固体废物</h3>
                  <button
                    type="button"
                    onClick={addGeneralSolidWaste}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加固体废物
                  </button>
                </div>
                
                {generalSolidWasteFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">固体废物 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeGeneralSolidWaste(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          废物名称
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.waste_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入废物名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          产生工序
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.source_process`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入产生工序"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          废物性质
                        </label>
                        <select
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.waste_nature`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="一般固体废物">一般固体废物</option>
                          <option value="可回收物">可回收物</option>
                          <option value="建筑垃圾">建筑垃圾</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          年产生量（单位 + 数值）
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.annual_generation`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入年产生量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          贮存方式
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.storage_method`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入贮存方式"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          处置方式
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.disposal_method`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入处置方式"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          去向单位
                        </label>
                        <input
                          type="text"
                          {...register(`noise_and_solid_waste.general_solid_wastes.${index}.destination_unit`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入去向单位"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                {generalSolidWasteFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无一般固体废物信息，请点击"添加固体废物"按钮添加
                  </div>
                )}
              </div>
            </div>
          </div>
        )

      case 6: // 事故防控设施
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🛡️</span>
              <h2 className="text-xl font-bold text-gray-900">事故防控设施</h2>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  是否有雨污分流设施
                </label>
                <select
                  {...register('accident_prevention_facilities.has_rain_sewage_diversion')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">请选择</option>
                  <option value="是">是</option>
                  <option value="否">否</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  雨污分流设施描述
                </label>
                <textarea
                  {...register('accident_prevention_facilities.rain_sewage_diversion_description')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请描述雨污分流设施情况"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  关键区域是否有围堰
                </label>
                <select
                  {...register('accident_prevention_facilities.has_key_area_bund')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">请选择</option>
                  <option value="是">是</option>
                  <option value="否">否</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  围堰位置
                </label>
                <input
                  type="text"
                  {...register('accident_prevention_facilities.key_area_bund_location')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请输入围堰位置"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  危险化学品仓库防渗结构
                </label>
                <select
                  {...register('accident_prevention_facilities.hazardous_chemical_warehouse_seepage_control')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">请选择</option>
                  <option value="有防渗">有防渗</option>
                  <option value="无防渗">无防渗</option>
                  <option value="部分防渗">部分防渗</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  关键阀门切断设施
                </label>
                <textarea
                  {...register('accident_prevention_facilities.key_valve_shut_off_facilities')}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请描述关键阀门切断设施情况"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  // 渲染步骤4：环保手续与管理制度的卡片
  const renderEnvironmentalPermitsCard = () => {
    switch (currentCard) {
      case 1: // 环保手续（证照）
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📋</span>
              <h2 className="text-xl font-bold text-gray-900">环保手续（证照）</h2>
            </div>
            
            <div className="space-y-6">
              {/* 环评文件 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">环评文件</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      环评项目名称
                    </label>
                    <input
                      type="text"
                      {...register('env_assessment_file.eia_project_name')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入环评项目名称"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      环评文号
                    </label>
                    <input
                      type="text"
                      {...register('env_assessment_file.eia_document_number')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入环评文号"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      批复日期
                    </label>
                    <input
                      type="date"
                      {...register('env_assessment_file.eia_approval_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      与现状一致性
                    </label>
                    <select
                      {...register('env_assessment_file.eia_consistency_status')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="一致">一致</option>
                      <option value="基本一致">基本一致</option>
                      <option value="不一致">不一致</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      批复机关
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入批复机关（暂不保存）"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      环评报告上传
                    </label>
                    <input
                      type="text"
                      {...register('env_assessment_file.eia_report_upload')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请上传环评报告文件"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      环评批复文件上传
                    </label>
                    <input
                      type="text"
                      {...register('env_assessment_file.eia_approval_upload')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请上传环评批复文件"
                    />
                  </div>
                </div>
              </div>

              {/* 竣工环保验收 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">竣工环保验收</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      验收类别
                    </label>
                    <select
                      {...register('env_acceptance.acceptance_type')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="验收监测">验收监测</option>
                      <option value="验收调查">验收调查</option>
                      <option value="其他">其他</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      验收文号
                    </label>
                    <input
                      type="text"
                      {...register('env_acceptance.acceptance_document_number')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入验收文号"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      验收日期
                    </label>
                    <input
                      type="date"
                      {...register('env_acceptance.acceptance_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      验收机关
                    </label>
                    <input
                      type="text"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入验收机关（暂不保存）"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      验收报告上传
                    </label>
                    <input
                      type="text"
                      {...register('env_acceptance.acceptance_report_upload')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请上传验收报告文件"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      验收批复上传
                    </label>
                    <input
                      type="text"
                      {...register('env_acceptance.acceptance_approval_upload')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请上传验收批复文件"
                    />
                  </div>
                </div>
              </div>

              {/* 排污许可证 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">排污许可证</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      排污许可证编号
                    </label>
                    <input
                      type="text"
                      {...register('discharge_permit.discharge_permit_number')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入排污许可证编号"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      发证机关
                    </label>
                    <input
                      type="text"
                      {...register('discharge_permit.issuing_authority')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入发证机关"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      有效期起始日期
                    </label>
                    <input
                      type="date"
                      {...register('discharge_permit.permit_start_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      有效期截止日期
                    </label>
                    <input
                      type="date"
                      {...register('discharge_permit.permit_end_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    许可排放的主要污染物
                  </label>
                  <textarea
                    {...register('discharge_permit.permitted_pollutants')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                    placeholder="请输入许可排放的主要污染物"
                    style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                  />
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    证书扫描件上传
                  </label>
                  <input
                    type="text"
                    {...register('discharge_permit.permit_scan_upload')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请上传证书扫描件"
                  />
                </div>
              </div>

              {/* 其他环保相关许可证 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">其他环保相关许可证</h3>
                  <button
                    type="button"
                    onClick={addOtherEnvPermit}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加许可证
                  </button>
                </div>
                
                {otherEnvPermitFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">许可证 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeOtherEnvPermit(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          证书类型
                        </label>
                        <input
                          type="text"
                          {...register(`other_env_permits.${index}.certificate_type`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入证书类型"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          证书编号
                        </label>
                        <input
                          type="text"
                          {...register(`other_env_permits.${index}.certificate_number`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入证书编号"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          发证机关
                        </label>
                        <input
                          type="text"
                          {...register(`other_env_permits.${index}.issuing_authority`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入发证机关"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          有效期
                        </label>
                        <input
                          type="text"
                          {...register(`other_env_permits.${index}.validity_period`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入有效期"
                        />
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        扫描件上传
                      </label>
                      <input
                        type="text"
                        {...register(`other_env_permits.${index}.scan_file_upload`)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请上传扫描件"
                      />
                    </div>
                  </div>
                ))}
                
                {otherEnvPermitFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无其他环保许可证信息，请点击"添加许可证"按钮添加
                  </div>
                )}
              </div>
            </div>
          </div>
        )

      case 2: // 危险废物/医废处置协议
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🗑️</span>
              <h2 className="text-xl font-bold text-gray-900">危险废物/医废处置协议</h2>
            </div>
            
            <div className="space-y-6">
              {/* 危废处置协议 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">危废处置协议</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      协议单位名称
                    </label>
                    <input
                      type="text"
                      {...register('hazardous_waste_agreement.hazardous_waste_agreement_unit')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入协议单位名称"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      单位许可证编号
                    </label>
                    <input
                      type="text"
                      {...register('hazardous_waste_agreement.hazardous_waste_unit_permit_number')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入单位许可证编号"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      协议起始日期
                    </label>
                    <input
                      type="date"
                      {...register('hazardous_waste_agreement.hazardous_waste_agreement_start_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      协议结束日期
                    </label>
                    <input
                      type="date"
                      {...register('hazardous_waste_agreement.hazardous_waste_agreement_end_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    涉及危废类别
                  </label>
                  <textarea
                    {...register('hazardous_waste_agreement.hazardous_waste_categories')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                    placeholder="请输入涉及危废类别"
                    style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                  />
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    协议扫描件上传
                  </label>
                  <input
                    type="text"
                    {...register('hazardous_waste_agreement.hazardous_waste_agreement_upload')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请上传协议扫描件"
                  />
                </div>
              </div>

              {/* 医疗废物处置协议 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">医疗废物处置协议</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      协议单位名称
                    </label>
                    <input
                      type="text"
                      {...register('medical_waste_agreement.medical_waste_agreement_unit')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入协议单位名称"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      单位许可证编号
                    </label>
                    <input
                      type="text"
                      {...register('medical_waste_agreement.medical_waste_unit_permit_number')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入单位许可证编号"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      协议起始日期
                    </label>
                    <input
                      type="date"
                      {...register('medical_waste_agreement.medical_waste_agreement_start_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      协议结束日期
                    </label>
                    <input
                      type="date"
                      {...register('medical_waste_agreement.medical_waste_agreement_end_date')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    涉及医废类别
                  </label>
                  <textarea
                    {...register('medical_waste_agreement.medical_waste_categories')}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                    placeholder="请输入涉及医废类别"
                    style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                  />
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    协议扫描件上传
                  </label>
                  <input
                    type="text"
                    {...register('medical_waste_agreement.medical_waste_agreement_upload')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请上传协议扫描件"
                  />
                </div>
              </div>
            </div>
          </div>
        )

      case 3: // 环境应急预案备案情况
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📝</span>
              <h2 className="text-xl font-bold text-gray-900">环境应急预案备案情况</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    是否已编制突发环境事件应急预案
                  </label>
                  <select
                    {...register('emergency_plan_filing.has_emergency_plan')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="是">是</option>
                    <option value="否">否</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    是否已备案
                  </label>
                  <select
                    {...register('emergency_plan_filing.has_emergency_plan_filed')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="是">是</option>
                    <option value="否">否</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    备案编号
                  </label>
                  <input
                    type="text"
                    {...register('emergency_plan_filing.emergency_plan_filing_number')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入备案编号"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    备案机关
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入备案机关（暂不保存）"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    备案日期
                  </label>
                  <input
                    type="date"
                    {...register('emergency_plan_filing.emergency_plan_filing_date')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  备案回执/备案表上传
                </label>
                <input
                  type="text"
                  {...register('emergency_plan_filing.emergency_plan_filing_upload')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请上传备案回执/备案表"
                />
              </div>
            </div>
          </div>
        )

      case 4: // 管理制度与处罚记录
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">⚖️</span>
              <h2 className="text-xl font-bold text-gray-900">管理制度与处罚记录</h2>
            </div>
            
            <div className="space-y-6">
              {/* 管理制度情况 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">管理制度情况</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      环境风险隐患排查制度
                    </label>
                    <select
                      {...register('management_systems.has_risk_inspection_system')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="有">有</option>
                      <option value="无">无</option>
                      <option value="部分有">部分有</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      危险化学品安全管理制度
                    </label>
                    <select
                      {...register('management_systems.has_hazardous_chemicals_management_system')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="有">有</option>
                      <option value="无">无</option>
                      <option value="部分有">部分有</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      危险废物管理制度
                    </label>
                    <select
                      {...register('management_systems.has_hazardous_waste_management_system')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="有">有</option>
                      <option value="无">无</option>
                      <option value="部分有">部分有</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      应急演练及培训制度
                    </label>
                    <select
                      {...register('management_systems.has_emergency_drill_training_system')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="有">有</option>
                      <option value="无">无</option>
                      <option value="部分有">部分有</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      相关制度文件打包上传
                    </label>
                    <input
                      type="text"
                      {...register('management_systems.management_system_files_upload')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请上传相关制度文件"
                    />
                  </div>
                </div>
              </div>

              {/* 近三年行政处罚/事故记录 */}
              <div className="border border-gray-200 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">近三年行政处罚/事故记录</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否受到生态环境部门行政处罚
                    </label>
                    <select
                      {...register('penalty_accident_records.has_administrative_penalty')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      处罚详情
                    </label>
                    <textarea
                      {...register('penalty_accident_records.administrative_penalty_details')}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请输入处罚详情"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否有较大及以上环境事故
                    </label>
                    <select
                      {...register('penalty_accident_records.has_environmental_accident')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      事故详情
                    </label>
                    <textarea
                      {...register('penalty_accident_records.environmental_accident_details')}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请输入事故详情"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  // 渲染步骤5：应急管理与资源的卡片
  const renderEmergencyManagementCard = () => {
    switch (currentCard) {
      case 1: // 应急组织机构与联络方式
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🚑</span>
              <h2 className="text-xl font-bold text-gray-900">应急组织机构与联络方式</h2>
            </div>
            
            <div className="space-y-6">
              {/* 24小时值班电话 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  企业24小时值班电话
                </label>
                <input
                  type="text"
                  {...register('emergency_organization_and_contacts.duty_phone_24h')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请输入企业24小时值班电话"
                />
              </div>

              {/* 内部应急通讯录 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">内部应急通讯录</h3>
                  <button
                    type="button"
                    onClick={addInternalEmergencyContact}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加联系人
                  </button>
                </div>
                
                {internalEmergencyContactFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">联系人 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeInternalEmergencyContact(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          组织机构角色
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.internal_emergency_contacts.${index}.organization_role`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入组织机构角色"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          对应部门名称
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.internal_emergency_contacts.${index}.department_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入对应部门名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          姓名
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.internal_emergency_contacts.${index}.contact_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入姓名"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          职务
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.internal_emergency_contacts.${index}.position`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入职务"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          手机号
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.internal_emergency_contacts.${index}.mobile_phone`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入手机号"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                {internalEmergencyContactFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无内部应急联系人，请点击"添加联系人"按钮添加
                  </div>
                )}
              </div>

              {/* 外部应急单位联系方式 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">外部应急单位联系方式</h3>
                  <button
                    type="button"
                    onClick={addExternalEmergencyUnit}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加应急单位
                  </button>
                </div>
                
                {externalEmergencyUnitFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">应急单位 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeExternalEmergencyUnit(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          单位类别
                        </label>
                        <select
                          {...register(`emergency_organization_and_contacts.external_emergency_units.${index}.unit_category`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="消防部门">消防部门</option>
                          <option value="公安部门">公安部门</option>
                          <option value="医疗部门">医疗部门</option>
                          <option value="环保部门">环保部门</option>
                          <option value="安监部门">安监部门</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          单位名称
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.external_emergency_units.${index}.unit_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入单位名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          联系电话
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_organization_and_contacts.external_emergency_units.${index}.contact_phone`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入联系电话"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          是否签订互助/协议
                        </label>
                        <select
                          {...register(`emergency_organization_and_contacts.external_emergency_units.${index}.has_cooperation_agreement`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="是">是</option>
                          <option value="否">否</option>
                        </select>
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        主要应急能力说明
                      </label>
                      <textarea
                        {...register(`emergency_organization_and_contacts.external_emergency_units.${index}.emergency_capability_description`)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                        placeholder="请描述主要应急能力"
                        style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                      />
                    </div>
                  </div>
                ))}
                
                {externalEmergencyUnitFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无外部应急单位，请点击"添加应急单位"按钮添加
                  </div>
                )}
              </div>
            </div>
          </div>
        )

      case 2: // 应急物资与装备
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">🛡️</span>
              <h2 className="text-xl font-bold text-gray-900">应急物资与装备</h2>
            </div>
            
            <div className="space-y-6">
              {/* 自储应急物资清单 */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">自储应急物资清单</h3>
                  <button
                    type="button"
                    onClick={addSelfStoredEmergencyMaterial}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加物资
                  </button>
                </div>
                
                {selfStoredEmergencyMaterialFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">物资 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeSelfStoredEmergencyMaterial(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          名称
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.material_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入物资名称"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          单位
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.unit`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入单位"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          数量
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.quantity`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入数量"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          用途
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.purpose`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入用途"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          存放地点
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.storage_location`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入存放地点"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          保管人姓名
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.custodian_name`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入保管人姓名"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          保管人电话
                        </label>
                        <input
                          type="text"
                          {...register(`emergency_materials_and_equipment.self_stored_materials.${index}.custodian_phone`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入保管人电话"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                
                {selfStoredEmergencyMaterialFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无应急物资，请点击"添加物资"按钮添加
                  </div>
                )}
              </div>

              {/* 关键应急设施 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">关键应急设施</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      应急物资专用仓库数量
                    </label>
                    <input
                      type="text"
                      {...register('emergency_materials_and_equipment.warehouse_count')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入应急物资专用仓库数量"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      应急物资仓库总面积（m²）
                    </label>
                    <input
                      type="text"
                      {...register('emergency_materials_and_equipment.warehouse_total_area')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入应急物资仓库总面积"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      事故应急池是否存在
                    </label>
                    <select
                      {...register('emergency_materials_and_equipment.has_accident_pool')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      事故池有效容积（m³）
                    </label>
                    <input
                      type="text"
                      {...register('emergency_materials_and_equipment.accident_pool_effective_volume')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入事故池有效容积"
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      应急车辆数量及类型
                    </label>
                    <textarea
                      {...register('emergency_materials_and_equipment.emergency_vehicle_count_and_type')}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请描述应急车辆数量及类型"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 3: // 应急队伍与保障
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">👥</span>
              <h2 className="text-xl font-bold text-gray-900">应急队伍与保障</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    是否建立企业内部应急救援队伍
                  </label>
                  <select
                    {...register('emergency_team_and_support.has_internal_rescue_team')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="是">是</option>
                    <option value="否">否</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    应急队伍人数
                  </label>
                  <input
                    type="text"
                    {...register('emergency_team_and_support.team_member_count')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入应急队伍人数"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    是否有应急经费专项预算
                  </label>
                  <select
                    {...register('emergency_team_and_support.has_special_emergency_budget')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  >
                    <option value="">请选择</option>
                    <option value="是">是</option>
                    <option value="否">否</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    年度应急经费预算额度（万元）
                  </label>
                  <input
                    type="text"
                    {...register('emergency_team_and_support.annual_emergency_budget_amount')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入年度应急经费预算额度"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  队伍构成说明
                </label>
                <textarea
                  {...register('emergency_team_and_support.team_composition_description')}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                  placeholder="请描述应急队伍的构成情况"
                  style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                />
              </div>
            </div>
          </div>
        )

      case 4: // 演练与培训记录
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📋</span>
              <h2 className="text-xl font-bold text-gray-900">演练与培训记录</h2>
            </div>
            
            <div className="space-y-6">
              {/* 应急演练 */}
              <div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      最近三年是否开展应急演练
                    </label>
                    <select
                      {...register('drills_and_training_records.has_conducted_drills_recent_three_years')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">演练记录列表</h3>
                  <button
                    type="button"
                    onClick={addDrillRecord}
                    className="flex items-center px-3 py-1 bg-primary text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                  >
                    <PlusIcon className="mr-1" />
                    添加演练记录
                  </button>
                </div>
                
                {drillRecordFields.map((field, index) => (
                  <div key={field.id} className="border border-gray-200 rounded-lg p-4 mb-4">
                    <div className="flex justify-between items-center mb-3">
                      <h4 className="text-md font-medium text-gray-800">演练记录 {index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeDrillRecord(index)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          演练日期
                        </label>
                        <input
                          type="date"
                          {...register(`drills_and_training_records.drill_records.${index}.drill_date`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          演练类型
                        </label>
                        <select
                          {...register(`drills_and_training_records.drill_records.${index}.drill_type`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        >
                          <option value="">请选择</option>
                          <option value="综合演练">综合演练</option>
                          <option value="专项演练">专项演练</option>
                          <option value="现场处置演练">现场处置演练</option>
                          <option value="其他">其他</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          参与人数
                        </label>
                        <input
                          type="text"
                          {...register(`drills_and_training_records.drill_records.${index}.participants_count`)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入参与人数"
                        />
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        演练描述
                      </label>
                      <textarea
                        {...register(`drills_and_training_records.drill_records.${index}.drill_description`)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                        placeholder="请描述演练内容"
                        style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                      />
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        演练效果评估
                      </label>
                      <textarea
                        {...register(`drills_and_training_records.drill_records.${index}.drill_effectiveness_evaluation`)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                        placeholder="请评估演练效果"
                        style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                      />
                    </div>
                  </div>
                ))}
                
                {drillRecordFields.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    暂无演练记录，请点击"添加演练记录"按钮添加
                  </div>
                )}
              </div>

              {/* 应急与环保培训 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">应急与环保培训</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      年度应急培训次数
                    </label>
                    <input
                      type="text"
                      {...register('drills_and_training_records.annual_emergency_training_count')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入年度应急培训次数"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      年度环保培训次数
                    </label>
                    <input
                      type="text"
                      {...register('drills_and_training_records.annual_environmental_training_count')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入年度环保培训次数"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      职工覆盖率（%）
                    </label>
                    <input
                      type="text"
                      {...register('drills_and_training_records.employee_coverage_rate')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入职工覆盖率"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否包含危化品安全内容
                    </label>
                    <select
                      {...register('drills_and_training_records.includes_hazardous_chemical_safety')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      是否包含环境应急内容
                    </label>
                    <select
                      {...register('drills_and_training_records.includes_environmental_emergency')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="是">是</option>
                      <option value="否">否</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 5: // 应急资源调查元数据
        return (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center mb-6">
              <span className="text-2xl mr-3">📊</span>
              <h2 className="text-xl font-bold text-gray-900">应急资源调查元数据</h2>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    本次应急资源调查基准年份
                  </label>
                  <input
                    type="text"
                    {...register('emergency_resource_survey_metadata.survey_reference_year')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入调查基准年份"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    调查负责人姓名
                  </label>
                  <input
                    type="text"
                    {...register('emergency_resource_survey_metadata.survey_leader_name')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="请输入调查负责人姓名"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    调查工作开始日期
                  </label>
                  <input
                    type="date"
                    {...register('emergency_resource_survey_metadata.survey_start_date')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    调查工作结束日期
                  </label>
                  <input
                    type="date"
                    {...register('emergency_resource_survey_metadata.survey_end_date')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  调查联系人及电话
                </label>
                <input
                  type="text"
                  {...register('emergency_resource_survey_metadata.survey_contact_person_and_phone')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="请输入调查联系人及电话"
                />
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <ProjectLayout title="企业信息收集">
      <div className="max-w-4xl mx-auto">
        {/* 步骤导航 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">企业信息收集</h1>

          <div className="flex items-center justify-between mb-8">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <button
                  onClick={() => handleStepChange(step.id)}
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-medium transition-colors ${
                    currentStep === step.id
                      ? 'bg-primary text-white'
                      : currentStep > step.id
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                  }`}
                >
                  {currentStep > step.id ? '✓' : step.id}
                </button>
                <span className={`ml-2 text-sm font-medium ${
                  currentStep === step.id ? 'text-primary' : 'text-gray-600'
                }`}>
                  {step.title}
                </span>
                {index < steps.length - 1 && (
                  <div className={`w-12 h-0.5 mx-4 ${
                    currentStep > step.id ? 'bg-green-500' : 'bg-gray-200'
                  }`}></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 卡片导航 */}
        {currentStep === 1 && (
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">企业基本信息</h3>
              <div className="flex space-x-2">
                {enterpriseBasicCards.map((card, index) => (
                  <button
                    key={card.id}
                    onClick={() => handleCardChange(card.id)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentCard === card.id
                        ? 'bg-primary text-white'
                        : currentCard > card.id
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {currentCard > card.id ? '✓' : card.id}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-2">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>当前：</span>
                <span className="font-medium text-primary">{enterpriseBasicCards[currentCard - 1]?.title}</span>
              </div>
            </div>
          </div>
        )}
        
        {currentStep === 2 && (
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">生产过程与风险物质</h3>
              <div className="flex space-x-2">
                {productionRiskCards.map((card, index) => (
                  <button
                    key={card.id}
                    onClick={() => handleCardChange(card.id)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentCard === card.id
                        ? 'bg-primary text-white'
                        : currentCard > card.id
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {currentCard > card.id ? '✓' : card.id}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-2">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>当前：</span>
                <span className="font-medium text-primary">{productionRiskCards[currentCard - 1]?.title}</span>
              </div>
            </div>
          </div>
        )}
        
        {currentStep === 3 && (
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">环境信息</h3>
              <div className="flex space-x-2">
                {environmentInfoCards.map((card, index) => (
                  <button
                    key={card.id}
                    onClick={() => handleCardChange(card.id)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentCard === card.id
                        ? 'bg-primary text-white'
                        : currentCard > card.id
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {currentCard > card.id ? '✓' : card.id}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-2">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>当前：</span>
                <span className="font-medium text-primary">{environmentInfoCards[currentCard - 1]?.title}</span>
              </div>
            </div>
          </div>
        )}
        
        {currentStep === 4 && (
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">环保手续与管理制度</h3>
              <div className="flex space-x-2">
                {environmentalPermitsCards.map((card, index) => (
                  <button
                    key={card.id}
                    onClick={() => handleCardChange(card.id)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentCard === card.id
                        ? 'bg-primary text-white'
                        : currentCard > card.id
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {currentCard > card.id ? '✓' : card.id}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-2">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>当前：</span>
                <span className="font-medium text-primary">{environmentalPermitsCards[currentCard - 1]?.title}</span>
              </div>
            </div>
          </div>
        )}
        
        {currentStep === 5 && (
          <div className="bg-white rounded-lg shadow-md p-4 mb-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">应急管理与资源</h3>
              <div className="flex space-x-2">
                {emergencyManagementCards.map((card, index) => (
                  <button
                    key={card.id}
                    onClick={() => handleCardChange(card.id)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      currentCard === card.id
                        ? 'bg-primary text-white'
                        : currentCard > card.id
                        ? 'bg-green-500 text-white'
                        : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    }`}
                  >
                    {currentCard > card.id ? '✓' : card.id}
                  </button>
                ))}
              </div>
            </div>
            <div className="mt-2">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>当前：</span>
                <span className="font-medium text-primary">{emergencyManagementCards[currentCard - 1]?.title}</span>
              </div>
            </div>
          </div>
        )}
        
        {/* 表单内容 */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {currentStep === 1 && renderEnterpriseBasicCard()}
          
          {currentStep === 2 && renderProductionRiskCard()}
          
          {currentStep === 3 && renderEnvironmentInfoCard()}
          
          {currentStep === 4 && renderEnvironmentalPermitsCard()}
          
          {currentStep === 5 && renderEmergencyManagementCard()}

          {/* 步骤导航按钮 */}
          <div className="flex justify-between space-x-4 pt-6">
            <button
              type="button"
              onClick={handlePrevious}
              disabled={currentStep === 1 && currentCard === 1}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              上一步
            </button>

            <div className="flex space-x-4">
              <button
                type="button"
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
              >
                保存草稿
              </button>
              {currentStep === steps.length && currentCard === enterpriseBasicCards.length ? (
                <button
                  type="submit"
                  className="px-6 py-2 bg-primary text-white rounded-md hover:bg-green-700 transition-colors"
                >
                  完成并进入AI生成
                </button>
              ) : (
                <button
                  type="submit"
                  className="px-6 py-2 bg-primary text-white rounded-md hover:bg-green-700 transition-colors"
                >
                  {currentStep === 1 && currentCard < enterpriseBasicCards.length ? '下一步' :
                   currentStep === 2 && currentCard < productionRiskCards.length ? '下一步' :
                   currentStep === 3 && currentCard < environmentInfoCards.length ? '下一步' :
                   currentStep === 4 && currentCard < environmentalPermitsCards.length ? '下一步' :
                   currentStep === 5 && currentCard < emergencyManagementCards.length ? '下一步' : '完成并进入AI生成'}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </ProjectLayout>
  )
}