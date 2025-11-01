'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { CompanySearch } from '@/types'

interface CompanyFiltersProps {
  onFiltersChange: (filters: CompanySearch) => void
  onReset: () => void
  className?: string
}

export function CompanyFilters({ onFiltersChange, onReset, className = '' }: CompanyFiltersProps) {
  const [filters, setFilters] = useState<CompanySearch>({
    keyword: '',
    industry: '',
    unified_social_credit_code: '',
    legal_representative: '',
    contact_phone: '',
    contact_email: '',
    address: '',
    created_after: '',
    created_before: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    const newFilters = {
      ...filters,
      [name]: value
    }
    setFilters(newFilters)
    onFiltersChange(newFilters)
  }

  const handleReset = () => {
    const resetFilters = {
      keyword: '',
      industry: '',
      unified_social_credit_code: '',
      legal_representative: '',
      contact_phone: '',
      contact_email: '',
      address: '',
      created_after: '',
      created_before: '',
    }
    setFilters(resetFilters)
    onReset()
  }

  const hasActiveFilters = Object.values(filters).some(value => value !== '')

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">企业筛选</CardTitle>
          {hasActiveFilters && (
            <Button variant="outline" size="sm" onClick={handleReset}>
              重置
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label htmlFor="keyword" className="block text-sm font-medium text-gray-700 mb-1">
              关键词搜索
            </label>
            <Input
              id="keyword"
              name="keyword"
              type="text"
              value={filters.keyword}
              onChange={handleChange}
              placeholder="企业名称、联系人等"
            />
          </div>

          <div>
            <label htmlFor="industry" className="block text-sm font-medium text-gray-700 mb-1">
              所属行业
            </label>
            <select
              id="industry"
              name="industry"
              value={filters.industry}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">全部行业</option>
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
          </div>

          <div>
            <label htmlFor="unified_social_credit_code" className="block text-sm font-medium text-gray-700 mb-1">
              统一社会信用代码
            </label>
            <Input
              id="unified_social_credit_code"
              name="unified_social_credit_code"
              type="text"
              value={filters.unified_social_credit_code}
              onChange={handleChange}
              placeholder="请输入统一社会信用代码"
            />
          </div>

          <div>
            <label htmlFor="legal_representative" className="block text-sm font-medium text-gray-700 mb-1">
              法定代表人
            </label>
            <Input
              id="legal_representative"
              name="legal_representative"
              type="text"
              value={filters.legal_representative}
              onChange={handleChange}
              placeholder="请输入法定代表人姓名"
            />
          </div>

          <div>
            <label htmlFor="contact_phone" className="block text-sm font-medium text-gray-700 mb-1">
              联系电话
            </label>
            <Input
              id="contact_phone"
              name="contact_phone"
              type="text"
              value={filters.contact_phone}
              onChange={handleChange}
              placeholder="请输入联系电话"
            />
          </div>

          <div>
            <label htmlFor="contact_email" className="block text-sm font-medium text-gray-700 mb-1">
              联系邮箱
            </label>
            <Input
              id="contact_email"
              name="contact_email"
              type="email"
              value={filters.contact_email}
              onChange={handleChange}
              placeholder="请输入联系邮箱"
            />
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-1">
              企业地址
            </label>
            <Input
              id="address"
              name="address"
              type="text"
              value={filters.address}
              onChange={handleChange}
              placeholder="请输入企业地址"
            />
          </div>

          <div>
            <label htmlFor="created_after" className="block text-sm font-medium text-gray-700 mb-1">
              创建时间起始
            </label>
            <Input
              id="created_after"
              name="created_after"
              type="date"
              value={filters.created_after}
              onChange={handleChange}
            />
          </div>

          <div>
            <label htmlFor="created_before" className="block text-sm font-medium text-gray-700 mb-1">
              创建时间结束
            </label>
            <Input
              id="created_before"
              name="created_before"
              type="date"
              value={filters.created_before}
              onChange={handleChange}
            />
          </div>
        </div>

        {hasActiveFilters && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex flex-wrap gap-2">
              {Object.entries(filters).map(([key, value]) => {
                if (value) {
                  const labelMap: Record<string, string> = {
                    keyword: '关键词',
                    industry: '行业',
                    unified_social_credit_code: '统一社会信用代码',
                    legal_representative: '法定代表人',
                    contact_phone: '联系电话',
                    contact_email: '联系邮箱',
                    address: '企业地址',
                    created_after: '创建时间起始',
                    created_before: '创建时间结束',
                  }
                  
                  return (
                    <span
                      key={key}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {labelMap[key]}: {value}
                    </span>
                  )
                }
                return null
              })}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// 简化版筛选器组件，用于页面顶部
interface CompanyQuickFiltersProps {
  onFiltersChange: (filters: Partial<CompanySearch>) => void
  className?: string
}

export function CompanyQuickFilters({ onFiltersChange, className = '' }: CompanyQuickFiltersProps) {
  const [quickFilters, setQuickFilters] = useState({
    keyword: '',
    industry: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    const newFilters = {
      ...quickFilters,
      [name]: value
    }
    setQuickFilters(newFilters)
    onFiltersChange(newFilters)
  }

  return (
    <div className={`flex flex-col sm:flex-row gap-4 ${className}`}>
      <div className="flex-1">
        <Input
          name="keyword"
          type="text"
          value={quickFilters.keyword}
          onChange={handleChange}
          placeholder="搜索企业名称、联系人..."
          className="w-full"
        />
      </div>
      <div className="w-full sm:w-48">
        <select
          name="industry"
          value={quickFilters.industry}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">全部行业</option>
          <option value="制造业">制造业</option>
          <option value="建筑业">建筑业</option>
          <option value="批发和零售业">批发和零售业</option>
          <option value="信息传输、软件和信息技术服务业">信息传输、软件和信息技术服务业</option>
          <option value="金融业">金融业</option>
          <option value="房地产业">房地产业</option>
          <option value="租赁和商务服务业">租赁和商务服务业</option>
          <option value="科学研究和技术服务业">科学研究和技术服务业</option>
          <option value="其他">其他</option>
        </select>
      </div>
    </div>
  )
}