'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { CompanyForm } from '@/components/companies/company-form'
import { CompanyCreate, CompanyUpdate } from '@/types'
import { companyApi } from '@/lib/api'

export default function NewCompanyPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // 处理表单提交
  const handleSubmit = async (data: CompanyCreate | CompanyUpdate) => {
    if (!('name' in data) || !data.name) {
      setError('企业名称不能为空')
      return
    }

    const payload: CompanyCreate = {
      name: data.name,
      unified_social_credit_code: data.unified_social_credit_code,
      legal_representative: data.legal_representative,
      contact_phone: data.contact_phone,
      contact_email: data.contact_email,
      address: data.address,
      industry: data.industry,
      business_scope: data.business_scope,
    }

    try {
      setLoading(true)
      setError(null)
      
      const response = await companyApi.createCompany(payload)
      if (response.success && response.data) {
        // 创建成功，跳转到企业详情页
        router.push(`/companies/${response.data.id}`)
      } else {
        setError(response.message || '创建企业失败')
      }
    } catch (err) {
      setError('创建企业失败')
      console.error('创建企业失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 处理取消
  const handleCancel = () => {
    router.push('/companies')
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">创建新企业</h1>
          <p className="text-gray-600 mt-1">填写企业基本信息</p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* 企业表单 */}
        <CompanyForm
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={loading}
        />
      </div>
    </div>
  )
}
