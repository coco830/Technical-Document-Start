'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { mockDocuments } from '@/utils/mock-data'
import { useAuth } from '@/hooks/use-auth-simple'

export default function SimpleDocumentsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    setTimeout(() => {
      setDocuments(mockDocuments)
      setLoading(false)
    }, 500)
  }, [isAuthenticated, router])

  const filteredDocuments = documents.filter(doc =>
    doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.content.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
      draft: { label: '草稿', variant: 'secondary' },
      reviewing: { label: '审查中', variant: 'default' },
      completed: { label: '已完成', variant: 'outline' }
    }
    const config = statusMap[status] || { label: status, variant: 'outline' }
    return <Badge variant={config.variant}>{config.label}</Badge>
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
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">文档管理</h2>
            <p className="mt-2 text-sm text-gray-600">
              管理和编辑您的文档内容
            </p>
          </div>
          <Button onClick={() => alert('这是演示版本，创建功能暂时不可用')}>
            创建文档
          </Button>
        </div>

        <div className="mb-6">
          <Input
            type="text"
            placeholder="搜索文档..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-lg text-gray-600">加载中...</div>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-lg text-gray-600 mb-4">
              {searchTerm ? '没有找到匹配的文档' : '您还没有任何文档'}
            </div>
            {!searchTerm && (
              <Button onClick={() => alert('这是演示版本，创建功能暂时不可用')}>
                创建第一个文档
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDocuments.map((doc) => (
              <Card key={doc.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{doc.title}</CardTitle>
                      <CardDescription className="mt-2 line-clamp-2">
                        {doc.content.substring(0, 100)}...
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3">
                    {getStatusBadge(doc.status)}
                    <Badge variant="outline">{doc.format}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>所属项目:</span>
                      <span className="text-gray-900">{doc.project?.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>字数:</span>
                      <span className="text-gray-900">{doc.word_count.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>更新:</span>
                      <span className="text-gray-900">
                        {new Date(doc.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => alert(`查看文档 ${doc.id} (演示版本)`)}
                    >
                      查看
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => alert(`编辑文档 ${doc.id} (演示版本)`)}
                    >
                      编辑
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
