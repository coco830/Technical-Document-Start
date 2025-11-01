'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentWithDetails, ExportFormat } from '@/types'
import { documentApi } from '@/lib/api'
import { formatDateTime, formatDistanceToNow } from '@/lib/utils'
import { 
  ArrowLeft, 
  Edit, 
  Trash2, 
  Download, 
  History,
  Eye,
  FileText,
  Calendar,
  User
} from 'lucide-react'

export default function DocumentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const documentId = parseInt(params.id as string)
  
  const [document, setDocument] = useState<DocumentWithDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'preview' | 'raw'>('preview')

  useEffect(() => {
    if (documentId) {
      fetchDocument()
    }
  }, [documentId])

  const fetchDocument = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await documentApi.getDocument(documentId)
      
      if (response.success && response.data) {
        setDocument(response.data)
      }
    } catch (err) {
      console.error('获取文档详情失败:', err)
      setError('获取文档详情失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleEdit = () => {
    router.push(`/documents/${documentId}/edit`)
  }

  const handleDelete = async () => {
    if (window.confirm('确定要删除这个文档吗？此操作不可撤销。')) {
      try {
        await documentApi.deleteDocument(documentId)
        router.push('/documents')
      } catch (err) {
        console.error('删除文档失败:', err)
        alert('删除文档失败，请稍后重试')
      }
    }
  }

  const handleExport = async (format: 'pdf' | 'docx' | 'html' | 'markdown') => {
    const exportFormat: ExportFormat =
      format === 'docx'
        ? ExportFormat.WORD
        : format === 'pdf'
          ? ExportFormat.PDF
          : format === 'html'
            ? ExportFormat.HTML
            : ExportFormat.MARKDOWN

    try {
      await documentApi.exportDocument(documentId, { format: exportFormat })
    } catch (err) {
      console.error('导出文档失败:', err)
      alert('导出文档失败，请稍后重试')
    }
  }

  const handleVersionHistory = () => {
    router.push(`/documents/${documentId}/versions`)
  }

  const renderContent = () => {
    if (!document) return null

    if (viewMode === 'raw') {
      return (
        <div className="bg-gray-50 p-4 rounded-lg">
          <pre className="whitespace-pre-wrap text-sm text-gray-700">
            {document.content || '无内容'}
          </pre>
        </div>
      )
    }

    // 预览模式
    return (
      <div className="prose prose-sm sm:prose lg:prose-lg xl:prose-2xl max-w-none">
        {document.content ? (
          <div dangerouslySetInnerHTML={{ __html: document.content }} />
        ) : (
          <p className="text-gray-500">此文档暂无内容</p>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">
            {error || '文档不存在'}
          </h1>
          <Button onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 返回按钮 */}
      <div className="mb-6">
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          返回
        </Button>
      </div>

      {/* 文档信息 */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">{document.title}</CardTitle>
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <FileText className="h-4 w-4" />
                  <span>{document.format}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>创建于 {formatDateTime(new Date(document.created_at))}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>更新于 {formatDistanceToNow(new Date(document.updated_at))}</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'preview' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('preview')}
              >
                <Eye className="h-4 w-4 mr-2" />
                预览
              </Button>
              <Button
                variant={viewMode === 'raw' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('raw')}
              >
                <FileText className="h-4 w-4 mr-2" />
                源码
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-medium mb-2">项目信息</h4>
              <p className="text-gray-600">
                {document.project_name || `项目ID: ${document.project_id}`}
              </p>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">统计信息</h4>
              <div className="space-y-1 text-gray-600">
                <p>版本数: {document.versions_count || 0}</p>
                <p>AI生成次数: {document.ai_generations_count || 0}</p>
                <p>导出次数: {document.exports_count || 0}</p>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">操作</h4>
              <div className="flex flex-wrap gap-2">
                <Button size="sm" onClick={handleEdit}>
                  <Edit className="h-4 w-4 mr-2" />
                  编辑
                </Button>
                <Button size="sm" variant="outline" onClick={handleVersionHistory}>
                  <History className="h-4 w-4 mr-2" />
                  版本历史
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleExport('pdf')}>
                  <Download className="h-4 w-4 mr-2" />
                  导出
                </Button>
                <Button size="sm" variant="outline" onClick={handleDelete} className="text-red-600 hover:text-red-800">
                  <Trash2 className="h-4 w-4 mr-2" />
                  删除
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 文档内容 */}
      <Card>
        <CardHeader>
          <CardTitle>文档内容</CardTitle>
        </CardHeader>
        <CardContent>
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  )
}
