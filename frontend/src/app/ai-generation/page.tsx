'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { mockAIGenerations } from '@/utils/mock-data'
import { useAuth } from '@/hooks/use-auth-simple'

export default function SimpleAIGenerationPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [generations, setGenerations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    setTimeout(() => {
      setGenerations(mockAIGenerations)
      setLoading(false)
    }, 500)
  }, [isAuthenticated, router])

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
      generating: { label: '生成中', variant: 'default' },
      completed: { label: '已完成', variant: 'outline' },
      failed: { label: '失败', variant: 'destructive' }
    }
    const config = statusMap[status] || { label: status, variant: 'outline' }
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  const getTypeIcon = (type: string) => {
    const iconMap: Record<string, string> = {
      emergency_plan: '🚨',
      environmental_assessment: '🌍',
      general: '📝'
    }
    return iconMap[type] || '📝'
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">悦恩人机共写平台</h1>
            <Button onClick={() => router.push('/dashboard')} variant="outline" size="sm">
              返回仪表盘
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            AI内容生成
          </h2>
          <p className="text-gray-600">
            使用AI技术生成专业内容，支持多种生成模式和配置选项
          </p>
        </div>

        {/* 生成选项 */}
        <div className="mb-8">
          <Card>
            <CardHeader>
              <CardTitle>选择生成类型</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                  <div className="text-4xl mb-4">📝</div>
                  <h3 className="text-lg font-semibold mb-2">通用内容生成</h3>
                  <p className="text-gray-600 mb-4">
                    根据自定义提示词生成各类专业内容
                  </p>
                  <Button onClick={() => alert('这是演示版本，生成功能暂时不可用')}>
                    开始生成
                  </Button>
                </div>

                <div className="text-center p-6 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                  <div className="text-4xl mb-4">🚨</div>
                  <h3 className="text-lg font-semibold mb-2">应急预案生成</h3>
                  <p className="text-gray-600 mb-4">
                    基于企业信息生成专业的应急预案文档
                  </p>
                  <Button onClick={() => alert('这是演示版本，生成功能暂时不可用')}>
                    生成预案
                  </Button>
                </div>

                <div className="text-center p-6 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
                  <div className="text-4xl mb-4">🌍</div>
                  <h3 className="text-lg font-semibold mb-2">环评报告生成</h3>
                  <p className="text-gray-600 mb-4">
                    根据项目信息生成环境影响评价报告
                  </p>
                  <Button onClick={() => alert('这是演示版本，生成功能暂时不可用')}>
                    生成报告
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 生成记录 */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">最近生成记录</h3>
            <Button variant="outline" onClick={() => alert('这是演示版本，查看全部功能暂时不可用')}>
              查看全部
            </Button>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="text-lg text-gray-600">加载中...</div>
            </div>
          ) : generations.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-lg text-gray-600 mb-4">
                您还没有任何生成记录
              </div>
              <Button onClick={() => alert('这是演示版本，生成功能暂时不可用')}>
                创建第一个生成任务
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {generations.map((gen) => (
                <Card key={gen.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-2xl">{getTypeIcon(gen.type)}</span>
                          <CardTitle className="text-lg">{gen.prompt}</CardTitle>
                        </div>
                        <CardDescription>
                          使用 {gen.model_used} · {gen.tokens_used} tokens
                        </CardDescription>
                      </div>
                      {getStatusBadge(gen.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    {gen.generated_content && (
                      <div className="mb-4 p-3 bg-gray-50 rounded text-sm">
                        <div className="line-clamp-3">
                          {gen.generated_content.substring(0, 200)}...
                        </div>
                      </div>
                    )}
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => alert(`查看生成 ${gen.id} (演示版本)`)}
                      >
                        查看详情
                      </Button>
                      {gen.status === 'completed' && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => alert(`复制生成内容 (演示版本)`)}
                          >
                            复制
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => alert(`下载生成内容 (演示版本)`)}
                          >
                            下载
                          </Button>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
