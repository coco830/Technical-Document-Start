import React, { useState } from 'react'
import { useForm, useFieldArray, Controller } from 'react-hook-form'
import { apiClient } from '@/utils/api'

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
  risk_level: string  // 风险级别
}

interface EnvPermits {
  env_assessment_no: string
  acceptance_no: string
  discharge_permit_no: string
  has_emergency_plan: string  // 有/无
  emergency_plan_code: string  // 仅当有预案时填写
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
  custom_resource_name: string  // 自定义应急物资名称
  quantity: string
  purpose: string
  storage_location: string
  custodian: string
  custodian_contact: string  // 保管人联系方式
}

interface EmergencyOrg {
  id: string
  org_name: string
  custom_org_name: string  // 自定义组织机构名称
  responsible_person: string
  contact_phone: string
  department: string  // 企业对应部门
  duty_phone: string  // 企业24小时值班电话
}

interface ExternalEmergencyContact {
  id: string
  unit_name: string  // 单位名称
  contact_method: string  // 通讯方式
  custom_contact_method: string  // 自定义通讯方式
  custom_unit_name: string  // 自定义单位名称
}

interface EnterpriseFormData {
  enterprise_basic: EnterpriseBasic
  env_permits: EnvPermits
  hazardous_materials: HazardousMaterial[]
  emergency_resources: EmergencyResource[]
  emergency_orgs: EmergencyOrg[]
  external_emergency_contacts: ExternalEmergencyContact[]
}

export default function EnterpriseInfo() {
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    permits: true,
    materials: true,
    resources: true,
    orgs: true,
    external_contacts: true
  })

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
  const onSubmit = (data: EnterpriseFormData) => {
    console.log('企业信息收集表单数据:', JSON.stringify(data, null, 2))
    
    // 这里预留API调用
    // fetch('/api/enterprise_info', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify(data),
    // })
    // .then(response => response.json())
    // .then(result => {
    //   console.log('提交成功:', result)
    // })
    // .catch(error => {
    //   console.error('提交失败:', error)
    // })
    
    alert('表单数据已输出到控制台，请查看console.log')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          {/* 页面标题 */}
          <div className="bg-primary px-6 py-4">
            <h1 className="text-2xl font-bold text-white">企业信息收集</h1>
            <p className="text-green-100 mt-1">请填写企业基本信息，为应急预案AI撰写提供数据支持</p>
          </div>

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
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        传真
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.fax')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入传真号码"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        电子邮箱
                      </label>
                      <input
                        type="email"
                        {...register('enterprise_basic.email')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入电子邮箱"
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

            {/* 环保手续信息 */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                type="button"
                className="w-full px-6 py-4 bg-gray-50 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('permits')}
              >
                <h2 className="text-lg font-semibold text-gray-900">环保手续信息</h2>
                {expandedSections.permits ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              {expandedSections.permits && (
                <div className="p-6 space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        环评批复编号
                      </label>
                      <input
                        type="text"
                        {...register('env_permits.env_assessment_no')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入环评批复编号"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        验收文件编号
                      </label>
                      <input
                        type="text"
                        {...register('env_permits.acceptance_no')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入验收文件编号"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        排污许可证编号
                      </label>
                      <input
                        type="text"
                        {...register('env_permits.discharge_permit_no')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入排污许可证编号"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        历史应急预案
                      </label>
                      <select
                        {...register('env_permits.has_emergency_plan')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择</option>
                        <option value="有">有</option>
                        <option value="无">无</option>
                      </select>
                    </div>
                    
                    {watch('env_permits.has_emergency_plan') === '有' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          历史应急预案编号
                        </label>
                        <input
                          type="text"
                          {...register('env_permits.emergency_plan_code')}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                          placeholder="请输入历史应急预案编号"
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 危险化学品信息 */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                type="button"
                className="w-full px-6 py-4 bg-gray-50 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('materials')}
              >
                <h2 className="text-lg font-semibold text-gray-900">危险化学品信息</h2>
                {expandedSections.materials ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              {expandedSections.materials && (
                <div className="p-6">
                  <div className="space-y-4">
                    {materialFields.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>暂无危险化学品信息</p>
                        <button
                          type="button"
                          onClick={addMaterial}
                          className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                        >
                          <PlusIcon className="h-4 w-4 mr-2" />
                          添加危险化学品
                        </button>
                      </div>
                    ) : (
                      <>
                        {materialFields.map((field, index) => (
                          <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-center mb-4">
                              <h3 className="text-md font-medium text-gray-900">危险化学品 {index + 1}</h3>
                              <button
                                type="button"
                                onClick={() => removeMaterial(index)}
                                className="text-red-600 hover:text-red-800"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  化学品名称
                                </label>
                                <input
                                  type="text"
                                  {...register(`hazardous_materials.${index}.name`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入化学品名称"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  最大储存量（吨）
                                </label>
                                <input
                                  type="text"
                                  {...register(`hazardous_materials.${index}.max_storage`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入最大储存量"
                                />
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  年使用量（吨）
                                </label>
                                <input
                                  type="text"
                                  {...register(`hazardous_materials.${index}.annual_usage`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入年使用量"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  储存位置
                                </label>
                                <input
                                  type="text"
                                  {...register(`hazardous_materials.${index}.storage_location`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入储存位置"
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        <button
                          type="button"
                          onClick={addMaterial}
                          className="w-full py-2 border-2 border-dashed border-gray-300 rounded-md text-gray-600 hover:border-primary hover:text-primary transition-colors"
                        >
                          <PlusIcon className="h-5 w-5 inline mr-2" />
                          添加危险化学品
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 应急资源信息 */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                type="button"
                className="w-full px-6 py-4 bg-gray-50 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('resources')}
              >
                <h2 className="text-lg font-semibold text-gray-900">应急资源信息</h2>
                {expandedSections.resources ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              {expandedSections.resources && (
                <div className="p-6">
                  <div className="space-y-4">
                    {resourceFields.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>暂无应急资源信息</p>
                        <button
                          type="button"
                          onClick={addResource}
                          className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                        >
                          <PlusIcon className="h-4 w-4 mr-2" />
                          添加应急资源
                        </button>
                      </div>
                    ) : (
                      <>
                        {resourceFields.map((field, index) => (
                          <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-center mb-4">
                              <h3 className="text-md font-medium text-gray-900">应急资源 {index + 1}</h3>
                              <button
                                type="button"
                                onClick={() => removeResource(index)}
                                className="text-red-600 hover:text-red-800"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  物资名称
                                </label>
                                <Controller
                                  name={`emergency_resources.${index}.name`}
                                  control={control}
                                  render={({ field }) => (
                                    <>
                                      <select
                                        value={field.value}
                                        onChange={(e) => {
                                          const value = e.target.value;
                                          field.onChange(value);
                                          // 如果选择固定选项，则清空自定义输入
                                          if (value !== '其他') {
                                            setValue(`emergency_resources.${index}.custom_resource_name`, '');
                                          }
                                        }}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                      >
                                        <option value="">请选择</option>
                                        <option value="应急照明灯">应急照明灯</option>
                                        <option value="防护服">防护服</option>
                                        <option value="防护头盔">防护头盔</option>
                                        <option value="防护鞋">防护鞋</option>
                                        <option value="反光背心">反光背心</option>
                                        <option value="防护手套">防护手套</option>
                                        <option value="防护腰带">防护腰带</option>
                                        <option value="急救箱">急救箱</option>
                                        <option value="水枪">水枪</option>
                                        <option value="呼吸器">呼吸器</option>
                                        <option value="呼吸面罩">呼吸面罩</option>
                                        <option value="消防水带">消防水带</option>
                                        <option value="安全带">安全带</option>
                                        <option value="灭火器">灭火器</option>
                                        <option value="消防沙">消防沙</option>
                                        <option value="其他">其他</option>
                                      </select>
                                      
                                      {/* 当选择"其他"时，显示自定义输入框 */}
                                      {field.value === '其他' && (
                                        <input
                                          type="text"
                                          {...register(`emergency_resources.${index}.custom_resource_name`)}
                                          className="w-full mt-2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                          placeholder="请输入自定义应急物资名称"
                                        />
                                      )}
                                    </>
                                  )}
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  数量（单位）
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_resources.${index}.quantity`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入数量"
                                />
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  用途
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_resources.${index}.purpose`)}
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
                                  {...register(`emergency_resources.${index}.storage_location`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入存放地点"
                                />
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  保管人
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_resources.${index}.custodian`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入保管人"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  保管人联系方式
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_resources.${index}.custodian_contact`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入保管人联系方式"
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        <button
                          type="button"
                          onClick={addResource}
                          className="w-full py-2 border-2 border-dashed border-gray-300 rounded-md text-gray-600 hover:border-primary hover:text-primary transition-colors"
                        >
                          <PlusIcon className="h-5 w-5 inline mr-2" />
                          添加应急资源
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 应急组织与通讯信息 */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                type="button"
                className="w-full px-6 py-4 bg-gray-50 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('orgs')}
              >
                <h2 className="text-lg font-semibold text-gray-900">应急组织与通讯信息</h2>
                {expandedSections.orgs ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              {expandedSections.orgs && (
                <div className="p-6">
                  <div className="space-y-4">
                    {orgFields.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>暂无应急组织信息</p>
                        <button
                          type="button"
                          onClick={addOrg}
                          className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                        >
                          <PlusIcon className="h-4 w-4 mr-2" />
                          添加应急组织
                        </button>
                      </div>
                    ) : (
                      <>
                        {orgFields.map((field, index) => (
                          <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-center mb-4">
                              <h3 className="text-md font-medium text-gray-900">应急组织 {index + 1}</h3>
                              <button
                                type="button"
                                onClick={() => removeOrg(index)}
                                className="text-red-600 hover:text-red-800"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  组织机构名称
                                </label>
                                <Controller
                                  name={`emergency_orgs.${index}.org_name`}
                                  control={control}
                                  render={({ field }) => (
                                    <>
                                      <select
                                        value={field.value}
                                        onChange={(e) => {
                                          const value = e.target.value;
                                          field.onChange(value);
                                          // 如果选择"其他"，则清空自定义输入
                                          if (value !== '其他') {
                                            setValue(`emergency_orgs.${index}.custom_org_name`, '');
                                          }
                                        }}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                      >
                                        <option value="">请选择</option>
                                        <option value="总指挥">总指挥</option>
                                        <option value="副总指挥">副总指挥</option>
                                        <option value="应急指挥办公室">应急指挥办公室</option>
                                        <option value="环境保护组">环境保护组</option>
                                        <option value="消防应急组">消防应急组</option>
                                        <option value="警戒疏散组">警戒疏散组</option>
                                        <option value="伤员救护组">伤员救护组</option>
                                        <option value="其他">其他</option>
                                      </select>
                                    
                                      {/* 当选择"其他"时，显示自定义输入框 */}
                                      {field.value === '其他' && (
                                        <input
                                          type="text"
                                          {...register(`emergency_orgs.${index}.custom_org_name`)}
                                          className="w-full mt-2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                          placeholder="请输入自定义组织机构名称"
                                        />
                                      )}
                                    </>
                                  )}
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  负责人
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_orgs.${index}.responsible_person`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入负责人"
                                />
                              </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  联系电话
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_orgs.${index}.contact_phone`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入联系电话"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  企业对应部门
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_orgs.${index}.department`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入企业对应部门"
                                />
                              </div>
                            </div>
                            
                            <div className="mt-4">
                              <label className="block text-sm font-medium text-gray-700 mb-1">
                                企业24小时值班电话
                              </label>
                              <input
                                type="text"
                                {...register(`emergency_orgs.${index}.duty_phone`)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                placeholder="请输入企业24小时值班电话"
                              />
                            </div>
                          </div>
                        ))}
                        
                        <button
                          type="button"
                          onClick={addOrg}
                          className="w-full py-2 border-2 border-dashed border-gray-300 rounded-md text-gray-600 hover:border-primary hover:text-primary transition-colors"
                        >
                          <PlusIcon className="h-5 w-5 inline mr-2" />
                          添加应急组织
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 外部应急救援通讯方式 */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                type="button"
                className="w-full px-6 py-4 bg-gray-50 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
                onClick={() => toggleSection('external_contacts')}
              >
                <h2 className="text-lg font-semibold text-gray-900">外部应急救援通讯方式</h2>
                {expandedSections.external_contacts ? (
                  <ChevronUpIcon className="h-5 w-5 text-gray-500" />
                ) : (
                  <ChevronDownIcon className="h-5 w-5 text-gray-500" />
                )}
              </button>
              
              {expandedSections.external_contacts && (
                <div className="p-6">
                  <div className="space-y-4">
                    {externalContactFields.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <p>暂无外部应急救援通讯方式信息</p>
                        <button
                          type="button"
                          onClick={addExternalContact}
                          className="mt-2 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                        >
                          <PlusIcon className="h-4 w-4 mr-2" />
                          添加外部应急救援通讯方式
                        </button>
                      </div>
                    ) : (
                      <>
                        {externalContactFields.map((field, index) => (
                          <div key={field.id} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-center mb-4">
                              <h3 className="text-md font-medium text-gray-900">外部应急救援通讯方式 {index + 1}</h3>
                              <button
                                type="button"
                                onClick={() => removeExternalContact(index)}
                                className="text-red-600 hover:text-red-800"
                              >
                                <TrashIcon className="h-5 w-5" />
                              </button>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  单位名称
                                </label>
                                <Controller
                                  name={`external_emergency_contacts.${index}.unit_name`}
                                  control={control}
                                  render={({ field }) => (
                                    <>
                                      <select
                                        value={field.value}
                                        onChange={(e) => {
                                          const value = e.target.value;
                                          field.onChange(value);
                                          // 根据选择的单位自动填充联系方式
                                          if (value === '消防') {
                                            setValue(`external_emergency_contacts.${index}.contact_method`, '119');
                                          } else if (value === '报警服务') {
                                            setValue(`external_emergency_contacts.${index}.contact_method`, '110');
                                          } else if (value === '医疗急救中心') {
                                            setValue(`external_emergency_contacts.${index}.contact_method`, '120');
                                          } else if (value === '环保举报热线') {
                                            setValue(`external_emergency_contacts.${index}.contact_method`, '12369');
                                          } else {
                                            setValue(`external_emergency_contacts.${index}.contact_method`, '');
                                          }
                                          // 清空自定义输入
                                          setValue(`external_emergency_contacts.${index}.custom_unit_name`, '');
                                        }}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                      >
                                        <option value="">请选择</option>
                                        <option value="消防">消防</option>
                                        <option value="报警服务">报警服务</option>
                                        <option value="医疗急救中心">医疗急救中心</option>
                                        <option value="环保举报热线">环保举报热线</option>
                                        <option value="其他">其他</option>
                                      </select>
                                      
                                      {/* 当选择"其他"时，显示自定义输入框 */}
                                      {field.value === '其他' && (
                                        <input
                                          type="text"
                                          {...register(`external_emergency_contacts.${index}.custom_unit_name`)}
                                          className="w-full mt-2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                          placeholder="请输入自定义单位名称"
                                        />
                                      )}
                                    </>
                                  )}
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  通讯方式
                                </label>
                                <input
                                  type="text"
                                  {...register(`external_emergency_contacts.${index}.contact_method`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入通讯方式"
                                  readOnly
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                        
                        <button
                          type="button"
                          onClick={addExternalContact}
                          className="w-full py-2 border-2 border-dashed border-gray-300 rounded-md text-gray-600 hover:border-primary hover:text-primary transition-colors"
                        >
                          <PlusIcon className="h-5 w-5 inline mr-2" />
                          添加外部应急救援通讯方式
                        </button>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 提交按钮 */}
            <div className="flex justify-end space-x-4 pt-6">
              <button
                type="button"
                className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                保存草稿
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-primary text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              >
                提交信息
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}