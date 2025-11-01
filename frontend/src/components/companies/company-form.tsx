'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Company, CompanyCreate, CompanyUpdate } from '@/types'

interface CompanyFormProps {
  company?: Company
  onSubmit: (data: CompanyCreate | CompanyUpdate) => void | Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export function CompanyForm({ company, onSubmit, onCancel, isLoading = false }: CompanyFormProps) {
  const [formData, setFormData] = useState({
    name: company?.name || '',
    unified_social_credit_code: company?.unified_social_credit_code || '',
    legal_representative: company?.legal_representative || '',
    contact_phone: company?.contact_phone || '',
    contact_email: company?.contact_email || '',
    address: company?.address || '',
    industry: company?.industry || '',
    business_scope: company?.business_scope || '',
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

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.name.trim()) {
      newErrors.name = '企业名称不能为空'
    } else if (formData.name.length > 200) {
      newErrors.name = '企业名称不能超过200个字符'
    }
    
    if (formData.unified_social_credit_code && formData.unified_social_credit_code.length !== 18) {
      newErrors.unified_social_credit_code = '统一社会信用代码必须为18位'
    }
    
    if (formData.legal_representative && formData.legal_representative.length > 100) {
      newErrors.legal_representative = '法定代表人姓名不能超过100个字符'
    }
    
    if (formData.contact_phone && formData.contact_phone.length > 20) {
      newErrors.contact_phone = '联系电话不能超过20个字符'
    }
    
    if (formData.contact_email && formData.contact_email.length > 100) {
      newErrors.contact_email = '联系邮箱不能超过100个字符'
    } else if (formData.contact_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
      newErrors.contact_email = '请输入有效的邮箱地址'
    }
    
    if (formData.industry && formData.industry.length > 100) {
      newErrors.industry = '所属行业不能超过100个字符'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      // 如果是编辑模式，只提交有值的字段
      const submitData = company 
        ? Object.entries(formData).reduce<CompanyUpdate>((acc, [key, value]) => {
            if (value !== '') {
              acc[key as keyof CompanyUpdate] = value
            }
            return acc
          }, {})
        : formData

      await Promise.resolve(onSubmit(submitData))
    }
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>{company ? '编辑企业' : '创建企业'}</CardTitle>
        <CardDescription>
          {company ? '修改企业信息' : '填写企业基本信息'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              企业名称 <span className="text-red-500">*</span>
            </label>
            <Input
              id="name"
              name="name"
              type="text"
              value={formData.name}
              onChange={handleChange}
              placeholder="请输入企业名称"
              className={errors.name ? 'border-red-500' : ''}
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
          </div>

          <div>
            <label htmlFor="unified_social_credit_code" className="block text-sm font-medium text-gray-700 mb-2">
              统一社会信用代码
            </label>
            <Input
              id="unified_social_credit_code"
              name="unified_social_credit_code"
              type="text"
              value={formData.unified_social_credit_code}
              onChange={handleChange}
              placeholder="请输入18位统一社会信用代码"
              className={errors.unified_social_credit_code ? 'border-red-500' : ''}
            />
            {errors.unified_social_credit_code && (
              <p className="mt-1 text-sm text-red-600">{errors.unified_social_credit_code}</p>
            )}
          </div>

          <div>
            <label htmlFor="legal_representative" className="block text-sm font-medium text-gray-700 mb-2">
              法定代表人
            </label>
            <Input
              id="legal_representative"
              name="legal_representative"
              type="text"
              value={formData.legal_representative}
              onChange={handleChange}
              placeholder="请输入法定代表人姓名"
              className={errors.legal_representative ? 'border-red-500' : ''}
            />
            {errors.legal_representative && (
              <p className="mt-1 text-sm text-red-600">{errors.legal_representative}</p>
            )}
          </div>

          <div>
            <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700 mb-2">
              联系电话
            </label>
            <Input
              id="contact_phone"
              name="contact_phone"
              type="text"
              value={formData.contact_phone}
              onChange={handleChange}
              placeholder="请输入联系电话"
              className={errors.contact_phone ? 'border-red-500' : ''}
            />
            {errors.contact_phone && (
              <p className="mt-1 text-sm text-red-600">{errors.contact_phone}</p>
            )}
          </div>

          <div>
            <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700 mb-2">
              联系邮箱
            </label>
            <Input
              id="contact_email"
              name="contact_email"
              type="email"
              value={formData.contact_email}
              onChange={handleChange}
              placeholder="请输入联系邮箱"
              className={errors.contact_email ? 'border-red-500' : ''}
            />
            {errors.contact_email && (
              <p className="mt-1 text-sm text-red-600">{errors.contact_email}</p>
            )}
          </div>

          <div>
            <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-2">
              所属行业
            </label>
            <select
              id="industry"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.industry ? 'border-red-500' : ''}`}
            >
              <option value="">请选择行业</option>
              <option value="制造业">制造业</option>
              <option value="建筑业">建筑业</option>
              <option value="批发和零售业">批发和零售业</option>
              <option value="交通运输、仓储和邮政业">交通运输、仓储和邮政业</option>
              <option value="住宿和餐饮业">住宿和餐饮业</option>
              <option value="信息传输、软件和信息技术服务业">信息传输、软件和信息技术服务业</option>
              <option value="金融业">金融业</option>
              <option value="房地产业">房地产业</option>
              <option value="租赁和商务服务业">租赁和商务服务业</option>
              <option value="科学研究和技术服务业">科学研究和技术服务业</option>
              <option value="水利、环境和公共设施管理业">水利、环境和公共设施管理业</option>
              <option value="居民服务、修理和其他服务业">居民服务、修理和其他服务业</option>
              <option value="教育">教育</option>
              <option value="卫生和社会工作">卫生和社会工作</option>
              <option value="文化、体育和娱乐业">文化、体育和娱乐业</option>
              <option value="公共管理、社会保障和社会组织">公共管理、社会保障和社会组织</option>
              <option value="国际组织">国际组织</option>
              <option value="其他">其他</option>
            </select>
            {errors.industry && (
              <p className="mt-1 text-sm text-red-600">{errors.industry}</p>
            )}
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
              企业地址
            </label>
            <Input
              id="address"
              name="address"
              type="text"
              value={formData.address}
              onChange={handleChange}
              placeholder="请输入企业地址"
            />
          </div>

          <div>
            <label htmlFor="business_scope" className="block text-sm font-medium text-gray-700 mb-2">
              经营范围
            </label>
            <textarea
              id="business_scope"
              name="business_scope"
              value={formData.business_scope}
              onChange={handleChange}
              placeholder="请输入经营范围（可选）"
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex justify-end space-x-4 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? '保存中...' : (company ? '更新' : '创建')}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
