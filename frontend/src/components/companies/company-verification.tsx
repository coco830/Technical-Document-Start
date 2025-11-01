'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { CompanyVerification, CompanyVerificationCreate, CompanyVerificationUpdate } from '@/types'

interface CompanyVerificationProps {
  companyId: number
  verifications: CompanyVerification[]
  onCreateVerification: (data: CompanyVerificationCreate) => void
  onUpdateVerification: (verificationId: number, data: CompanyVerificationUpdate) => void
  isLoading?: boolean
  className?: string
}

// 验证类型选项
const verificationTypes = [
  { value: 'basic', label: '基础验证', description: '企业基本信息验证' },
  { value: 'business_license', label: '营业执照验证', description: '验证企业营业执照信息' },
  { value: 'tax_certificate', label: '税务登记证验证', description: '验证企业税务登记信息' },
  { value: 'organization_code', label: '组织机构代码验证', description: '验证企业组织机构代码' },
  { value: 'bank_account', label: '银行账户验证', description: '验证企业银行账户信息' },
  { value: 'legal_representative', label: '法定代表人验证', description: '验证法定代表人身份信息' },
  { value: 'comprehensive', label: '综合验证', description: '全面验证企业各项信息' },
]

// 验证状态选项
const verificationStatuses = [
  { value: 'pending', label: '待验证', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'verified', label: '已验证', color: 'bg-green-100 text-green-800' },
  { value: 'rejected', label: '已拒绝', color: 'bg-red-100 text-red-800' },
  { value: 'expired', label: '已过期', color: 'bg-gray-100 text-gray-800' },
]

export function CompanyVerification({ 
  companyId, 
  verifications, 
  onCreateVerification, 
  onUpdateVerification, 
  isLoading = false,
  className = ''
}: CompanyVerificationProps) {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [formData, setFormData] = useState({
    verification_type: 'basic',
    verification_data: {} as Record<string, any>,
    notes: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // 清除错误
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleVerificationDataChange = (key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      verification_data: {
        ...prev.verification_data,
        [key]: value
      }
    }))
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.verification_type) {
      newErrors.verification_type = '请选择验证类型'
    }
    
    if (Object.keys(formData.verification_data).length === 0) {
      newErrors.verification_data = '请填写验证数据'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      onCreateVerification({
        company_id: companyId,
        verification_type: formData.verification_type,
        verification_data: formData.verification_data,
        notes: formData.notes,
      })
      
      // 重置表单
      setFormData({
        verification_type: 'basic',
        verification_data: {},
        notes: '',
      })
      setShowCreateForm(false)
    }
  }

  const handleStatusUpdate = (verificationId: number, status: string) => {
    onUpdateVerification(verificationId, {
      verification_status: status,
      verified_at: new Date().toISOString(),
    })
  }

  const selectedVerificationType = verificationTypes.find(type => type.value === formData.verification_type)

  return (
    <div className={className}>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>企业验证</CardTitle>
              <CardDescription>管理企业验证记录和状态</CardDescription>
            </div>
            <Button
              onClick={() => setShowCreateForm(!showCreateForm)}
              variant={showCreateForm ? "outline" : "default"}
            >
              {showCreateForm ? '取消' : '新建验证'}
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {showCreateForm && (
            <form onSubmit={handleSubmit} className="space-y-6 mb-6 p-4 border rounded-lg bg-gray-50">
              <div>
                <label htmlFor="verification_type" className="block text-sm font-medium text-gray-700 mb-2">
                  验证类型 <span className="text-red-500">*</span>
                </label>
                <select
                  id="verification_type"
                  name="verification_type"
                  value={formData.verification_type}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.verification_type ? 'border-red-500' : ''}`}
                >
                  {verificationTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
                {selectedVerificationType && (
                  <p className="mt-1 text-sm text-gray-500">{selectedVerificationType.description}</p>
                )}
                {errors.verification_type && (
                  <p className="mt-1 text-sm text-red-600">{errors.verification_type}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  验证数据 <span className="text-red-500">*</span>
                </label>
                <div className="space-y-2">
                  {formData.verification_type === 'basic' && (
                    <>
                      <Input
                        placeholder="企业名称"
                        value={formData.verification_data.company_name || ''}
                        onChange={(e) => handleVerificationDataChange('company_name', e.target.value)}
                      />
                      <Input
                        placeholder="统一社会信用代码"
                        value={formData.verification_data.unified_social_credit_code || ''}
                        onChange={(e) => handleVerificationDataChange('unified_social_credit_code', e.target.value)}
                      />
                    </>
                  )}
                  
                  {formData.verification_type === 'business_license' && (
                    <>
                      <Input
                        placeholder="营业执照编号"
                        value={formData.verification_data.license_number || ''}
                        onChange={(e) => handleVerificationDataChange('license_number', e.target.value)}
                      />
                      <Input
                        placeholder="发证机关"
                        value={formData.verification_data.issuing_authority || ''}
                        onChange={(e) => handleVerificationDataChange('issuing_authority', e.target.value)}
                      />
                      <Input
                        type="date"
                        placeholder="有效期至"
                        value={formData.verification_data.valid_until || ''}
                        onChange={(e) => handleVerificationDataChange('valid_until', e.target.value)}
                      />
                    </>
                  )}
                  
                  {formData.verification_type === 'legal_representative' && (
                    <>
                      <Input
                        placeholder="法定代表人姓名"
                        value={formData.verification_data.legal_representative_name || ''}
                        onChange={(e) => handleVerificationDataChange('legal_representative_name', e.target.value)}
                      />
                      <Input
                        placeholder="身份证号"
                        value={formData.verification_data.id_card_number || ''}
                        onChange={(e) => handleVerificationDataChange('id_card_number', e.target.value)}
                      />
                    </>
                  )}
                  
                  {formData.verification_type === 'bank_account' && (
                    <>
                      <Input
                        placeholder="银行账户"
                        value={formData.verification_data.bank_account || ''}
                        onChange={(e) => handleVerificationDataChange('bank_account', e.target.value)}
                      />
                      <Input
                        placeholder="开户行"
                        value={formData.verification_data.bank_name || ''}
                        onChange={(e) => handleVerificationDataChange('bank_name', e.target.value)}
                      />
                    </>
                  )}
                </div>
                {errors.verification_data && (
                  <p className="mt-1 text-sm text-red-600">{errors.verification_data}</p>
                )}
              </div>

              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
                  备注
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  value={formData.notes}
                  onChange={handleChange}
                  placeholder="请输入验证备注（可选）"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="flex justify-end space-x-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateForm(false)}
                  disabled={isLoading}
                >
                  取消
                </Button>
                <Button
                  type="submit"
                  disabled={isLoading}
                >
                  {isLoading ? '创建中...' : '创建验证'}
                </Button>
              </div>
            </form>
          )}

          <div className="space-y-4">
            {verifications.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>暂无验证记录</p>
                <p className="text-sm mt-1">点击"新建验证"按钮创建第一条验证记录</p>
              </div>
            ) : (
              verifications.map((verification) => {
                const statusInfo = verificationStatuses.find(status => status.value === verification.verification_status)
                const typeInfo = verificationTypes.find(type => type.value === verification.verification_type)
                
                return (
                  <div key={verification.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="font-medium">{typeInfo?.label || verification.verification_type}</h4>
                        <p className="text-sm text-gray-500">
                          创建时间: {verification.created_at ? new Date(verification.created_at).toLocaleString() : '未知'}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo?.color || 'bg-gray-100 text-gray-800'}`}>
                          {statusInfo?.label || verification.verification_status}
                        </span>
                        
                        {verification.verification_status === 'pending' && (
                          <div className="flex space-x-1">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusUpdate(verification.id!, 'verified')}
                              className="text-green-600 hover:text-green-700 hover:bg-green-50"
                            >
                              通过
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleStatusUpdate(verification.id!, 'rejected')}
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            >
                              拒绝
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {verification.verification_data && Object.keys(verification.verification_data).length > 0 && (
                      <div className="mb-3">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">验证数据:</h5>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                          {Object.entries(verification.verification_data).map(([key, value]) => (
                            <div key={key} className="flex">
                              <span className="font-medium text-gray-600 mr-2">{key}:</span>
                              <span className="text-gray-800">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {verification.notes && (
                      <div className="mb-3">
                        <h5 className="text-sm font-medium text-gray-700 mb-1">备注:</h5>
                        <p className="text-sm text-gray-600">{verification.notes}</p>
                      </div>
                    )}
                    
                    {verification.verified_at && (
                      <div className="text-xs text-gray-500">
                        验证时间: {new Date(verification.verified_at).toLocaleString()}
                        {verification.verified_by && (
                          <span> | 验证人: {verification.verified_by}</span>
                        )}
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
