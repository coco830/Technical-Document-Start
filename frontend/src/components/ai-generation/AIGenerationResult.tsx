'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { AIGenerationWithDetails, AIGenerationStatus } from '@/types'
import { formatDistanceToNow } from '@/utils'

interface AIGenerationResultProps {
  generation: AIGenerationWithDetails
  onCopy?: (content: string) => void
  onDownload?: (content: string, filename: string) => void
  onRegenerate?: (id: number) => void
  showActions?: boolean
}

export function AIGenerationResult({ 
  generation, 
  onCopy, 
  onDownload, 
  onRegenerate,
  showActions = true 
}: AIGenerationResultProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isCopying, setIsCopying] = useState(false)

  const statusColors = {
    [AIGenerationStatus.PENDING]: 'bg-gray-100 text-gray-800',
    [AIGenerationStatus.PROCESSING]: 'bg-blue-100 text-blue-800',
    [AIGenerationStatus.COMPLETED]: 'bg-green-100 text-green-800',
    [AIGenerationStatus.FAILED]: 'bg-red-100 text-red-800',
  }

  const statusLabels = {
    [AIGenerationStatus.PENDING]: '等待中',
    [AIGenerationStatus.PROCESSING]: '生成中',
    [AIGenerationStatus.COMPLETED]: '已完成',
    [AIGenerationStatus.FAILED]: '失败',
  }

  const handleCopy = async () => {
    if (!generation.generated_content || !onCopy) return
    
    setIsCopying(true)
    try {
      await onCopy(generation.generated_content)
    } finally {
      setIsCopying(false)
    }
  }

  const handleDownload = () => {
    if (!generation.generated_content || !onDownload) return
    
    const filename = `ai-generation-${generation.id}-${new Date().toISOString().slice(0, 10)}.txt`
    onDownload(generation.generated_content, filename)
  }

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(generation.id)
    }
  }

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  const contentPreview = generation.generated_content
    ? generation.generated_content.length > 500 && !isExpanded
      ? generation.generated_content.slice(0, 500) + '...'
      : generation.generated_content
    : ''

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold">
              AI生成结果 #{generation.id}
            </CardTitle>
            <div className="flex items-center space-x-2 mt-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[generation.status]}`}>
                {statusLabels[generation.status]}
              </span>
              {generation.processing_time && (
                <span className="text-sm text-gray-500">
                  耗时 {generation.processing_time}秒
                </span>
              )}
            </div>
          </div>
          {showActions && (
            <div className="flex items-center space-x-2">
              {generation.status === AIGenerationStatus.COMPLETED && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopy}
                    disabled={isCopying || !generation.generated_content}
                  >
                    {isCopying ? '复制中...' : '复制'}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleDownload}
                    disabled={!generation.generated_content}
                  >
                    下载
                  </Button>
                </>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={handleRegenerate}
                disabled={generation.status === AIGenerationStatus.PROCESSING}
              >
                重新生成
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 元信息 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">文档ID:</span>
              <span className="ml-2 font-medium">{generation.document_id}</span>
            </div>
            <div>
              <span className="text-gray-500">用户:</span>
              <span className="ml-2 font-medium">{generation.user_name || '未知'}</span>
            </div>
            <div>
              <span className="text-gray-500">创建时间:</span>
              <span className="ml-2 font-medium">
                {formatDistanceToNow(new Date(generation.created_at))}
              </span>
            </div>
            {generation.completed_at && (
              <div>
                <span className="text-gray-500">完成时间:</span>
                <span className="ml-2 font-medium">
                  {formatDistanceToNow(new Date(generation.completed_at))}
                </span>
              </div>
            )}
          </div>

          {/* 提示词 */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">提示词:</h4>
            <div className="p-3 bg-gray-50 rounded-md text-sm">
              {generation.prompt}
            </div>
          </div>

          {/* 生成配置 */}
          {generation.generation_config && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">生成配置:</h4>
              <div className="p-3 bg-gray-50 rounded-md">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">模型:</span>
                    <span className="ml-2">{generation.generation_config.model}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">温度:</span>
                    <span className="ml-2">{generation.generation_config.temperature}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">最大令牌:</span>
                    <span className="ml-2">{generation.generation_config.max_tokens}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">核采样:</span>
                    <span className="ml-2">{generation.generation_config.top_p}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 生成内容 */}
          {generation.generated_content && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-medium text-gray-700">生成内容:</h4>
                {generation.generated_content.length > 500 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={toggleExpanded}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    {isExpanded ? '收起' : '展开全部'}
                  </Button>
                )}
              </div>
              <div className="p-3 bg-blue-50 rounded-md">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed">
                  {contentPreview}
                </pre>
              </div>
            </div>
          )}

          {/* 错误信息 */}
          {generation.status === AIGenerationStatus.FAILED && (
            <div>
              <h4 className="text-sm font-medium text-red-700 mb-2">错误信息:</h4>
              <div className="p-3 bg-red-50 rounded-md text-sm text-red-800">
                {generation.metadata?.error || '生成失败，请重试'}
              </div>
            </div>
          )}

          {/* 元数据 */}
          {generation.metadata && Object.keys(generation.metadata).length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">元数据:</h4>
              <div className="p-3 bg-gray-50 rounded-md">
                <pre className="text-xs text-gray-600 overflow-x-auto">
                  {JSON.stringify(generation.metadata, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}