'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AIGenerationStatusInfo, AIGenerationStatus as AIGenerationStatusEnum } from '@/types'
import { formatDistanceToNow } from '@/utils'

interface AIGenerationStatusProps {
  generationId: number
  initialStatus?: AIGenerationStatusInfo
  onStatusChange?: (status: AIGenerationStatusInfo) => void
  onComplete?: (status: AIGenerationStatusInfo) => void
  onFailed?: (status: AIGenerationStatusInfo) => void
  autoRefresh?: boolean
  refreshInterval?: number
}

export function AIGenerationStatus({ 
  generationId,
  initialStatus,
  onStatusChange,
  onComplete,
  onFailed,
  autoRefresh = true,
  refreshInterval = 3000
}: AIGenerationStatusProps) {
  const [status, setStatus] = useState<AIGenerationStatusInfo | null>(initialStatus || null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  useEffect(() => {
    if (!status && generationId) {
      fetchStatus()
    }
  }, [generationId])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (autoRefresh && status && (
      status.status === AIGenerationStatusEnum.PENDING || 
      status.status === AIGenerationStatusEnum.PROCESSING
    )) {
      interval = setInterval(() => {
        fetchStatus()
      }, refreshInterval)
    }
    
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [autoRefresh, status?.status, refreshInterval, generationId])

  const fetchStatus = async () => {
    if (!generationId) return
    
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch(`/api/v1/ai-generations/${generationId}/status`)
      
      if (!response.ok) {
        throw new Error('获取状态失败')
      }
      
      const data = await response.json()
      const newStatus = data.data
      
      setStatus(newStatus)
      setLastUpdated(new Date())
      
      // 触发状态变化回调
      if (onStatusChange) {
        onStatusChange(newStatus)
      }
      
      // 触发完成回调
      if (newStatus.status === AIGenerationStatusEnum.COMPLETED && onComplete) {
        onComplete(newStatus)
      }
      
      // 触发失败回调
      if (newStatus.status === AIGenerationStatusEnum.FAILED && onFailed) {
        onFailed(newStatus)
      }
    } catch (err) {
      setError('获取状态失败')
      console.error('Failed to fetch status:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = () => {
    fetchStatus()
  }

  const getStatusColor = (status: AIGenerationStatusEnum) => {
    switch (status) {
      case AIGenerationStatusEnum.PENDING:
        return 'bg-gray-100 text-gray-800'
      case AIGenerationStatusEnum.PROCESSING:
        return 'bg-blue-100 text-blue-800'
      case AIGenerationStatusEnum.COMPLETED:
        return 'bg-green-100 text-green-800'
      case AIGenerationStatusEnum.FAILED:
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: AIGenerationStatusEnum) => {
    switch (status) {
      case AIGenerationStatusEnum.PENDING:
        return '⏳'
      case AIGenerationStatusEnum.PROCESSING:
        return '🔄'
      case AIGenerationStatusEnum.COMPLETED:
        return '✅'
      case AIGenerationStatusEnum.FAILED:
        return '❌'
      default:
        return '❓'
    }
  }

  const getStatusLabel = (status: AIGenerationStatusEnum) => {
    switch (status) {
      case AIGenerationStatusEnum.PENDING:
        return '等待中'
      case AIGenerationStatusEnum.PROCESSING:
        return '生成中'
      case AIGenerationStatusEnum.COMPLETED:
        return '已完成'
      case AIGenerationStatusEnum.FAILED:
        return '失败'
      default:
        return '未知'
    }
  }

  if (!status) {
    return (
      <Card className="w-full">
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-gray-600">加载状态中...</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            生成状态 #{generationId}
          </CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            {isLoading ? '刷新中...' : '刷新'}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 状态显示 */}
          <div className="flex items-center space-x-4">
            <div className="text-2xl">
              {getStatusIcon(status.status)}
            </div>
            <div className="flex-1">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status.status)}`}>
                {getStatusLabel(status.status)}
              </div>
              {status.progress !== undefined && (
                <div className="mt-2">
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-1">
                    <span>进度</span>
                    <span>{status.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${status.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 状态消息 */}
          {status.message && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">状态消息:</h4>
              <div className="p-3 bg-gray-50 rounded-md text-sm">
                {status.message}
              </div>
            </div>
          )}

          {/* 时间信息 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">创建时间:</span>
              <span className="ml-2 font-medium">
                {formatDistanceToNow(new Date(status.created_at))}
              </span>
            </div>
            <div>
              <span className="text-gray-500">更新时间:</span>
              <span className="ml-2 font-medium">
                {formatDistanceToNow(new Date(status.updated_at))}
              </span>
            </div>
          </div>

          {/* 错误信息 */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          {/* 自动刷新提示 */}
          {autoRefresh && (
            <div className="text-xs text-gray-500 text-center">
              最后更新: {formatDistanceToNow(lastUpdated)}
              {status.status === AIGenerationStatusEnum.PROCESSING && ' (自动刷新中...)'}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
