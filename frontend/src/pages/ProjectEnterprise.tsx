import React, { useState } from 'react'
import { useForm, useFieldArray, Controller } from 'react-hook-form'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '@/utils/api'
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
interface EnterpriseBasic {
  enterprise_name: string
  address: string
  industry: string
  legal_representative: string
  contact_phone: string
  fax: string
  email: string
  overview: string
  risk_level: string
}

interface EnvPermits {
  env_assessment_no: string
  acceptance_no: string
  discharge_permit_no: string
  has_emergency_plan: string
  emergency_plan_code: string
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
  enterprise_basic: EnterpriseBasic
  env_permits: EnvPermits
  hazardous_materials: HazardousMaterial[]
  emergency_resources: EmergencyResource[]
  emergency_orgs: EmergencyOrg[]
  external_emergency_contacts: ExternalEmergencyContact[]
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
      default: return 1
    }
  }

  const [currentStep, setCurrentStep] = useState(getStepFromParam(step))
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    permits: false,
    materials: false,
    resources: false,
    orgs: false,
    external_contacts: false
  })

  const steps = [
    { id: 1, title: '基本信息', key: 'basic' },
    { id: 2, title: '生产过程', key: 'production' },
    { id: 3, title: '环境信息', key: 'environment' },
    { id: 4, title: '环保手续', key: 'permits' }
  ]

  const handleStepChange = (stepId: number) => {
    setCurrentStep(stepId)
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
        materials: stepKey === 'permits',
        resources: stepKey === 'permits',
        orgs: stepKey === 'permits',
        external_contacts: stepKey === 'permits'
      })
    }
  }

  const handleNext = () => {
    if (currentStep < steps.length) {
      handleStepChange(currentStep + 1)
    } else {
      // 完成所有步骤，跳转到AI生成页面
      navigate(`/project/${id}/ai-generate`)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
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
      enterprise_basic: {
        enterprise_name: '',
        address: '',
        industry: '',
        legal_representative: '',
        contact_phone: '',
        fax: '',
        email: '',
        overview: '',
        risk_level: ''
      },
      env_permits: {
        env_assessment_no: '',
        acceptance_no: '',
        discharge_permit_no: '',
        has_emergency_plan: '',
        emergency_plan_code: ''
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

  // 表单提交
  const onSubmit = async (data: EnterpriseFormData) => {
    try {
      console.log('企业信息收集表单数据:', JSON.stringify(data, null, 2))

      // API调用保存企业信息
      await apiClient.post('/enterprise/info', {
        ...data,
        project_id: id
      })

      alert('企业信息保存成功！')

      // 跳转到下一步
      handleNext()
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败，请重试')
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

        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
            {/* 企业基本信息 */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                type="button"
                className="w-full px-6 py-4 bg-gray-50 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('basic')}
              >
                <h2 className="text-lg font-semibold text-gray-900">企业基本信息</h2>
                {expandedSections.basic ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>

              {expandedSections.basic && (
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        企业名称 <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.enterprise_name', { required: '企业名称为必填项' })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入企业名称"
                      />
                      {errors.enterprise_basic?.enterprise_name && (
                        <p className="mt-1 text-sm text-red-600">{errors.enterprise_basic.enterprise_name.message}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        所属行业 <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.industry', { required: '所属行业为必填项' })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入所属行业"
                      />
                      {errors.enterprise_basic?.industry && (
                        <p className="mt-1 text-sm text-red-600">{errors.enterprise_basic.industry.message}</p>
                      )}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      企业地址
                    </label>
                    <input
                      type="text"
                      {...register('enterprise_basic.address')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入企业地址"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        法定代表人
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.legal_representative')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入法定代表人姓名"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        联系电话
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.contact_phone')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入联系电话"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      企业概况
                    </label>
                    <textarea
                      {...register('enterprise_basic.overview')}
                      rows={6}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary resize-y"
                      placeholder="请输入企业概况"
                      style={{ scrollbarWidth: 'thin', scrollbarColor: '#888 #f1f1f1' }}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      风险级别
                    </label>
                    <select
                      {...register('enterprise_basic.risk_level')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    >
                      <option value="">请选择</option>
                      <option value="一般环境风险等级（L）">一般环境风险等级（L）</option>
                      <option value="较大环境风险等级（M）">较大环境风险等级（M）</option>
                      <option value="重大环境风险等级（H）">重大环境风险等级（H）</option>
                      <option value="特别重大环境风险等级（T）">特别重大环境风险等级（T）</option>
                    </select>
                  </div>
                </div>
              )}
            </div>

            {/* 步骤导航按钮 */}
            <div className="flex justify-between space-x-4 pt-6">
              <button
                type="button"
                onClick={handlePrevious}
                disabled={currentStep === 1}
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
                {currentStep === steps.length ? (
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
                    下一步
                  </button>
                )}
              </div>
            </div>
          </form>
        </div>
      </div>
    </ProjectLayout>
  )
}