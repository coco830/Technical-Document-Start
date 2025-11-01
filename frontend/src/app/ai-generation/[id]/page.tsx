'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AIGenerationResult } from '@/components/ai-generation/AIGenerationResult'
import { AIGenerationStatus } from '@/components/ai-generation/AIGenerationStatus'
import { RouteGuard } from '@/components/auth/route-guard'
import { aiGenerationApi } from '@/lib/api'
import { AIGenerationWithDetails, AIGenerationStatus as AIGenerationStatusEnum } from '@/types'

function AIGenerationDetailPageContent() {
  const router = useRouter()
  const params = useParams()
  const generationId = parseInt(params.id as string)
  
  const [generation, setGeneration] = useState<AIGenerationWithDetails | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    if (generationId) {
      fetchGeneration()
    }
  }, [generationId])

  const fetchGeneration = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await aiGenerationApi.getAIGeneration(generationId)
      
      if (response.success && response.data) {
        setGeneration(response.data)
      } else {
        setError(response.error || '获取生成记录失败')
      }
    } catch (err) {
      setError('获取生成记录失败')
      console.error('Failed to fetch generation:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEdit = () => {
    router.push(`/ai-generation/${generationId}/edit`)
  }

  const handleDelete = async () => {
    if (!confirm('确定要删除这个生成记录吗？此操作不可撤销。')) {
      return
    }

    setIsDeleting(true)
    try {
      const response = await aiGenerationApi.deleteAIGeneration(generationId)
      
      if (response.success) {
        router.push('/ai-generation')
      } else {
        setError(response.error || '删除生成记录失败')
      }
    } catch (err) {
      setError('删除生成记录失败')
      console.error('Failed to delete generation:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleCopy = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      // 这里可以添加成功提示
    } catch (err) {
      console.error('Failed to copy content:', err)
      // 这里可以添加失败提示
    }
  }

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const handleRegenerate = (id: number) => {
    router.push(`/ai-generation/new?regenerate=${id}`)
  }

  const handleBack = () => {
    router.back()
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    )
  }

  if (error || !generation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-red-600 mb-4">
                {error || '生成记录不存在'}
              </div>
              <div className="space-x-2">
                <Button variant="outline" onClick={handleBack}>
                  返回
                </Button>
                <Button onClick={fetchGeneration}>
                  重试
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* 页面标题和操作按钮 */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI生成详情 #{generation.id}
              </h1>
              <p className="mt-2 text-gray-600">
                查看和管理AI生成记录的详细信息
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                onClick={handleBack}
              >
                返回
              </Button>
              <Button
                variant="outline"
                onClick={handleEdit}
                disabled={generation.status === AIGenerationStatusEnum.PROCESSING}
              >
                编辑
              </Button>
              <Button
                variant="outline"
                onClick={handleDelete}
                disabled={isDeleting || generation.status === AIGenerationStatusEnum.PROCESSING}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                {isDeleting ? '删除中...' : '删除'}
              </Button>
            </div>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          {/* 生成状态 */}
          {generation.status === AIGenerationStatusEnum.PENDING || 
           generation.status === AIGenerationStatusEnum.PROCESSING ? (
            <div className="mb-8">
              <AIGenerationStatus
                generationId={generation.id}
                onComplete={() => fetchGeneration()}
                onFailed={() => fetchGeneration()}
              />
            </div>
          ) : null}

          {/* 生成结果 */}
          <AIGenerationResult
            generation={generation}
            onCopy={handleCopy}
            onDownload={handleDownload}
            onRegenerate={handleRegenerate}
          />

          {/* 相关操作 */}
          <div className="mt-8">
            <Card>
              <CardHeader>
                <CardTitle>相关操作</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button
                    variant="outline"
                    onClick={() => router.push('/ai-generation/new')}
                    className="w-full"
                  >
                    创建新生成
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => router.push('/ai-generation/history')}
                    className="w-full"
                  >
                    查看历史记录
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function AIGenerationDetailPage() {
  return (
    <RouteGuard requireAuth={true}>
      <AIGenerationDetailPageContent />
    </RouteGuard>
  )
}