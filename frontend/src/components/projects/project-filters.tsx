'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ProjectType, ProjectStatus } from '@/types'

interface ProjectFiltersProps {
  filters: {
    search?: string
    type?: ProjectType
    status?: ProjectStatus
  }
  onFiltersChange: (filters: {
    search?: string
    type?: ProjectType
    status?: ProjectStatus
  }) => void
  onReset: () => void
}

const typeLabels = {
  [ProjectType.EMERGENCY_PLAN]: '应急预案',
  [ProjectType.ENVIRONMENTAL_ASSESSMENT]: '环境评估',
}

const statusLabels = {
  [ProjectStatus.DRAFT]: '草稿',
  [ProjectStatus.GENERATING]: '生成中',
  [ProjectStatus.REVIEWING]: '审核中',
  [ProjectStatus.COMPLETED]: '已完成',
  [ProjectStatus.ARCHIVED]: '已归档',
}

export function ProjectFilters({ 
  filters, 
  onFiltersChange, 
  onReset 
}: ProjectFiltersProps) {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({
      ...filters,
      search: e.target.value || undefined
    })
  }

  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({
      ...filters,
      type: e.target.value ? e.target.value as ProjectType : undefined
    })
  }

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({
      ...filters,
      status: e.target.value ? e.target.value as ProjectStatus : undefined
    })
  }

  const hasActiveFilters = filters.search || filters.type || filters.status

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="text-lg">筛选项目</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              搜索
            </label>
            <Input
              id="search"
              type="text"
              placeholder="搜索项目名称或描述"
              value={filters.search || ''}
              onChange={handleSearchChange}
            />
          </div>

          <div>
            <label htmlFor="type" className="block text-sm font-medium text-gray-700 mb-2">
              项目类型
            </label>
            <select
              id="type"
              value={filters.type || ''}
              onChange={handleTypeChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">全部类型</option>
              {Object.entries(typeLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
              项目状态
            </label>
            <select
              id="status"
              value={filters.status || ''}
              onChange={handleStatusChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">全部状态</option>
              {Object.entries(statusLabels).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <Button
              variant="outline"
              onClick={onReset}
              disabled={!hasActiveFilters}
              className="w-full"
            >
              重置筛选
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}