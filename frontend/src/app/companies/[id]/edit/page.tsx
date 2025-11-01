'use client'

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { CompanyForm } from '@/components/companies/company-form'
import { Company, CompanyUpdate } from '@/types'
import { companyApi } from '@/lib/api'

export default function EditCompanyPage() {
  const params = useParams()
  const router = useRouter()
  const companyId = parseInt(params.id as string)

  const [company, setCompany] = useState<Company | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fetchLoading, setFetchLoading] = useState(true)

  // 获取企业详情
  const fetchCompany = async () => {
    try {
      setFetchLoading(true)
      setError(null)
      
      const response = await companyApi.getCompany(companyId)
      if (response.success && response.data) {
        setCompany(response.data)
      } else {
        setError(response.message || '获取企业详情失败')
      }
    } catch (err) {
      setError('获取企业详情失败')
      console.error('获取企业详情失败:', err)
    } finally {
      setFetchLoading(false)
    }
  }

  // 初始加载
  useEffect(() => {
    if (companyId) {
      fetchCompany()
    }
  }, [companyId])

  // 处理表单提交
  const handleSubmit = async (data: CompanyUpdate) => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await companyApi.updateCompany(companyId, data)
      if (response.success && response.data) {
        // 更新成功，跳转到企业详情页
        router.push(`/companies/${companyId}`)
      } else {
        setError(response.message || '更新企业失败')
      }
    } catch (err) {
      setError('更新企业失败')
      console.error('更新企业失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 处理取消
  const handleCancel = () => {
    router.push(`/companies/${companyId}`)
  }

  if (fetchLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="text-lg text-gray-600">加载中...</div>
        </div>
      </div>
    )
  }

  if (error || !company) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error || '企业不存在'}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">编辑企业</h1>
          <p className="text-gray-600 mt-1">修改企业信息</p>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* 企业表单 */}
        <CompanyForm
          company={company}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={loading}
        />
      </div>
    </div>
  )
}