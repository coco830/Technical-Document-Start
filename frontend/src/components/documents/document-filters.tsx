'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentSearch, DocumentStatus, DocumentFormat } from '@/types'
import { Search, Filter, RotateCcw } from 'lucide-react'

interface DocumentFiltersProps {
  filters: DocumentSearch
  onFiltersChange: (filters: DocumentSearch) => void
  onSearch: () => void
  onReset: () => void
  className?: string
}

export default function DocumentFilters({
  filters,
  onFiltersChange,
  onSearch,
  onReset,
  className
}: DocumentFiltersProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const handleInputChange = (field: keyof DocumentSearch, value: any) => {
    onFiltersChange({
      ...filters,
      [field]: value
    })
  }

  const handleDateChange = (field: 'created_after' | 'created_before' | 'updated_after' | 'updated_before', value: string) => {
    onFiltersChange({
      ...filters,
      [field]: value ? new Date(value).toISOString() : undefined
    })
  }

  const handleReset = () => {
    onReset()
    setIsExpanded(false)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">文档筛选</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <Filter className="h-4 w-4 mr-2" />
            {isExpanded ? '收起' : '展开'}
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* 基础搜索 */}
        <div className="flex gap-2">
          <div className="flex-1">
            <Input
              placeholder="搜索文档标题或内容..."
              value={filters.keyword || ''}
              onChange={(e) => handleInputChange('keyword', e.target.value)}
              className="w-full"
            />
          </div>
          <Button onClick={onSearch}>
            <Search className="h-4 w-4 mr-2" />
            搜索
          </Button>
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="h-4 w-4 mr-2" />
            重置
          </Button>
        </div>

        {/* 高级筛选 */}
        {isExpanded && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t">
            {/* 项目ID */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                项目ID
              </label>
              <Input
                type="number"
                placeholder="输入项目ID"
                value={filters.project_id || ''}
                onChange={(e) => handleInputChange('project_id', e.target.value ? parseInt(e.target.value) : undefined)}
              />
            </div>

            {/* 文档状态 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                文档状态
              </label>
              <select
                value={filters.status || ''}
                onChange={(e) => handleInputChange('status', e.target.value ? e.target.value as DocumentStatus : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">全部状态</option>
                <option value={DocumentStatus.DRAFT}>草稿</option>
                <option value={DocumentStatus.REVIEWING}>审核中</option>
                <option value={DocumentStatus.APPROVED}>已批准</option>
                <option value={DocumentStatus.PUBLISHED}>已发布</option>
              </select>
            </div>

            {/* 文档格式 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                文档格式
              </label>
              <select
                value={filters.format || ''}
                onChange={(e) => handleInputChange('format', e.target.value ? e.target.value as DocumentFormat : undefined)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">全部格式</option>
                <option value={DocumentFormat.MARKDOWN}>Markdown</option>
                <option value={DocumentFormat.HTML}>HTML</option>
                <option value={DocumentFormat.PLAIN_TEXT}>纯文本</option>
              </select>
            </div>

            {/* 创建时间范围 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                创建时间起始
              </label>
              <Input
                type="date"
                value={filters.created_after ? new Date(filters.created_after).toISOString().split('T')[0] : ''}
                onChange={(e) => handleDateChange('created_after', e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                创建时间结束
              </label>
              <Input
                type="date"
                value={filters.created_before ? new Date(filters.created_before).toISOString().split('T')[0] : ''}
                onChange={(e) => handleDateChange('created_before', e.target.value)}
              />
            </div>

            {/* 更新时间范围 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                更新时间起始
              </label>
              <Input
                type="date"
                value={filters.updated_after ? new Date(filters.updated_after).toISOString().split('T')[0] : ''}
                onChange={(e) => handleDateChange('updated_after', e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                更新时间结束
              </label>
              <Input
                type="date"
                value={filters.updated_before ? new Date(filters.updated_before).toISOString().split('T')[0] : ''}
                onChange={(e) => handleDateChange('updated_before', e.target.value)}
              />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}