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
  contact_person: string
  phone: string
  employee_count: string
  main_products: string
  annual_output: string
  description: string
}

interface EnvPermits {
  env_assessment_no: string
  acceptance_no: string
  discharge_permit_no: string
  env_dept: string
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
  quantity: string
  purpose: string
  storage_location: string
  custodian: string
}

interface EmergencyOrg {
  id: string
  org_name: string
  responsible_person: string
  contact_phone: string
  duties: string
}

interface EnterpriseFormData {
  enterprise_basic: EnterpriseBasic
  env_permits: EnvPermits
  hazardous_materials: HazardousMaterial[]
  emergency_resources: EmergencyResource[]
  emergency_orgs: EmergencyOrg[]
}

// 行业选项
const industryOptions = [
  '化工',
  '石化',
  '冶金',
  '电子',
  '纺织',
  '食品加工',
  '制药',
  '建材',
  '其他'
]

export default function EnterpriseInfo() {
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    permits: true,
    materials: true,
    resources: true,
    orgs: true
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
        contact_person: '',
        phone: '',
        employee_count: '',
        main_products: '',
        annual_output: '',
        description: ''
      },
      env_permits: {
        env_assessment_no: '',
        acceptance_no: '',
        discharge_permit_no: '',
        env_dept: ''
      },
      hazardous_materials: [],
      emergency_resources: [],
      emergency_orgs: []
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
      quantity: '',
      purpose: '',
      storage_location: '',
      custodian: ''
    })
  }

  const addOrg = () => {
    appendOrg({
      id: Date.now().toString(),
      org_name: '',
      responsible_person: '',
      contact_phone: '',
      duties: ''
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
                      <select
                        {...register('enterprise_basic.industry', { required: '所属行业为必填项' })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">请选择行业</option>
                        {industryOptions.map(option => (
                          <option key={option} value={option}>{option}</option>
                        ))}
                      </select>
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
                        联系人
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.contact_person')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入联系人姓名"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        联系电话
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.phone')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入联系电话"
                      />
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        员工人数
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.employee_count')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入员工人数"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        年产量
                      </label>
                      <input
                        type="text"
                        {...register('enterprise_basic.annual_output')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入年产量"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      主要产品
                    </label>
                    <input
                      type="text"
                      {...register('enterprise_basic.main_products')}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入主要产品"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      企业简介
                    </label>
                    <textarea
                      {...register('enterprise_basic.description')}
                      rows={4}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="请输入企业简介"
                    />
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
                        环保主管部门
                      </label>
                      <input
                        type="text"
                        {...register('env_permits.env_dept')}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                        placeholder="请输入环保主管部门"
                      />
                    </div>
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
                                <input
                                  type="text"
                                  {...register(`emergency_resources.${index}.name`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入物资名称"
                                />
                              </div>
                              
                              <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                  数量
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
                            
                            <div className="mt-4">
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
                                <input
                                  type="text"
                                  {...register(`emergency_orgs.${index}.org_name`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入组织机构名称"
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
                                  职责说明
                                </label>
                                <input
                                  type="text"
                                  {...register(`emergency_orgs.${index}.duties`)}
                                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                                  placeholder="请输入职责说明"
                                />
                              </div>
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