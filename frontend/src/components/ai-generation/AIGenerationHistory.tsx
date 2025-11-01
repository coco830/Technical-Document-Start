'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AIGenerationWithDetails, AIGenerationStatus } from '@/types'
import { aiGenerationApi } from '@/lib/api'
import { formatDistanceToNow } from '@/utils'

interface AIGenerationHistoryProps {
  userId?: number
  documentId?: number
  onGenerationSelect?: (generation: AIGenerationWithDetails) => void
  showFilters?: boolean
  showPagination?: boolean
  pageSize?: number
}

export function AIGenerationHistory({ 
  userId,
  documentId,
  onGenerationSelect,
  showFilters = true,
  showPagination = true,
  pageSize = 10
}: AIGenerationHistoryProps) {
  const [generations, setGenerations] = useState<AIGenerationWithDetails[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [filters, setFilters] = useState({
    status: '' as AIGenerationStatus | '',
    search: '',
    order_by: 'created_at',
    order_desc: true,
  })

  useEffect(() => {
    fetchGenerations()
  }, [currentPage, filters, userId, documentId])

  const fetchGenerations = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const params = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
        ...(userId && { user_id: userId }),
        ...(documentId && { document_id: documentId }),
        ...(filters.status && { status: filters.status }),
        ...(filters.search && { search: filters.search }),
        order_by: filters.order_by,
        order_desc: filters.order_desc,
      }

      const response = await aiGenerationApi.getAIGenerations(params)
      
      if (response.success && response.data) {
        setGenerations(response.data.generations)
        setTotal(response.data.total)
        setTotalPages(Math.ceil(response.data.total / pageSize))
      } else {
        setError(response.error || '获取生成历史失败')
      }
    } catch (err) {
      setError('获取生成历史失败')
      console.error('Failed to fetch generations:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFilterChange = (field: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }))
    setCurrentPage(1) // 重置到第一页
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setCurrentPage(1)
    fetchGenerations()
  }

  const handleResetFilters = () => {
    setFilters({
      status: '',
      search: '',
      order_by: 'created_at',
      order_desc: true,
    })
    setCurrentPage(1)
  }

  const handleGenerationClick = (generation: AIGenerationWithDetails) => {
    if (onGenerationSelect) {
      onGenerationSelect(generation)
    }
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  const getStatusColor = (status: AIGenerationStatus) => {
    switch (status) {
      case AIGenerationStatus.PENDING:
        return 'bg-gray-100 text-gray-800'
      case AIGenerationStatus.PROCESSING:
        return 'bg-blue-100 text-blue-800'
      case AIGenerationStatus.COMPLETED:
        return 'bg-green-100 text-green-800'
      case AIGenerationStatus.FAILED:
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusLabel = (status: AIGenerationStatus) => {
    switch (status) {
      case AIGenerationStatus.PENDING:
        return '等待中'
      case AIGenerationStatus.PROCESSING:
        return '生成中'
      case AIGenerationStatus.COMPLETED:
        return '已完成'
      case AIGenerationStatus.FAILED:
        return '失败'
      default:
        return '未知'
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>生成历史</CardTitle>
          <div className="text-sm text-gray-600">
            共 {total} 条记录
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* 筛选器 */}
        {showFilters && (
          <div className="mb-6 space-y-4">
            <form onSubmit={handleSearch} className="flex space-x-2">
              <Input
                placeholder="搜索提示词或内容..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="flex-1"
              />
              <Button type="submit">搜索</Button>
              <Button type="button" variant="outline" onClick={handleResetFilters}>
                重置
              </Button>
            </form>

            <div className="flex flex-wrap gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  状态
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">全部状态</option>
                  <option value={AIGenerationStatus.PENDING}>等待中</option>
                  <option value={AIGenerationStatus.PROCESSING}>生成中</option>
                  <option value={AIGenerationStatus.COMPLETED}>已完成</option>
                  <option value={AIGenerationStatus.FAILED}>失败</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  排序
                </label>
                <select
                  value={`${filters.order_by}_${filters.order_desc ? 'desc' : 'asc'}`}
                  onChange={(e) => {
                    const [order_by, order_desc] = e.target.value.split('_')
                    handleFilterChange('order_by', order_by)
                    handleFilterChange('order_desc', order_desc === 'desc')
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="created_at_desc">创建时间 (新到旧)</option>
                  <option value="created_at_asc">创建时间 (旧到新)</option>
                  <option value="completed_at_desc">完成时间 (新到旧)</option>
                  <option value="completed_at_asc">完成时间 (旧到新)</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* 加载状态 */}
        {isLoading && (
          <div className="flex justify-center items-center py-8">
            <div className="text-gray-600">加载中...</div>
          </div>
        )}

        {/* 错误状态 */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="text-red-800">{error}</div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchGenerations}
              className="mt-2"
            >
              重试
            </Button>
          </div>
        )}

        {/* 生成记录列表 */}
        {!isLoading && !error && (
          <>
            {generations.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-600">
                  {filters.search || filters.status
                    ? '没有找到符合筛选条件的记录'
                    : '暂无生成记录'
                  }
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {generations.map((generation) => (
                  <div
                    key={generation.id}
                    className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleGenerationClick(generation)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="font-medium">#{generation.id}</span>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(generation.status)}`}>
                            {getStatusLabel(generation.status)}
                          </span>
                          {generation.processing_time && (
                            <span className="text-sm text-gray-500">
                              {generation.processing_time}秒
                            </span>
                          )}
                        </div>
                        
                        <div className="text-sm text-gray-600 mb-2 line-clamp-2">
                          {generation.prompt}
                        </div>
                        
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>
                            文档: {generation.document_title || generation.document_id}
                          </span>
                          <span>
                            用户: {generation.user_name || '未知'}
                          </span>
                          <span>
                            创建: {formatDistanceToNow(new Date(generation.created_at))}
                          </span>
                          {generation.completed_at && (
                            <span>
                              完成: {formatDistanceToNow(new Date(generation.completed_at))}
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <div className="ml-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleGenerationClick(generation)
                          }}
                        >
                          查看
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* 分页 */}
        {showPagination && totalPages > 1 && (
          <div className="flex justify-center items-center space-x-2 mt-6">
            <Button
              variant="outline"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              上一页
            </Button>
            
            <div className="flex items-center space-x-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                <Button
                  key={page}
                  variant={currentPage === page ? 'default' : 'outline'}
                  onClick={() => handlePageChange(page)}
                  className="w-10 h-10 p-0"
                >
                  {page}
                </Button>
              ))}
            </div>
            
            <Button
              variant="outline"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              下一页
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}