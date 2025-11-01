'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentVersionWithDetails, DocumentVersion } from '@/types'
import { documentApi } from '@/lib/api'
import { formatDateTime, formatDistanceToNow } from '@/lib/utils'
import { 
  History, 
  Eye, 
  RotateCcw, 
  User, 
  Calendar,
  FileText,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

interface DocumentVersionHistoryProps {
  documentId: number
  onRestore?: (version: DocumentVersion) => void
  onView?: (version: DocumentVersion) => void
  className?: string
}

export default function DocumentVersionHistory({
  documentId,
  onRestore,
  onView,
  className
}: DocumentVersionHistoryProps) {
  const [versions, setVersions] = useState<DocumentVersionWithDetails[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedVersions, setExpandedVersions] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchVersions = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await documentApi.getDocumentVersions(documentId)
        if (response.success && response.data) {
          setVersions(response.data.versions)
        }
      } catch (err) {
        console.error('获取版本历史失败:', err)
        setError('获取版本历史失败，请稍后重试')
      } finally {
        setLoading(false)
      }
    }

    if (documentId) {
      fetchVersions()
    }
  }, [documentId])

  const toggleVersionExpansion = (versionId: number) => {
    const newExpanded = new Set(expandedVersions)
    if (newExpanded.has(versionId)) {
      newExpanded.delete(versionId)
    } else {
      newExpanded.add(versionId)
    }
    setExpandedVersions(newExpanded)
  }

  const handleRestore = async (version: DocumentVersion) => {
    if (window.confirm(`确定要恢复到版本 ${version.version_number} 吗？当前未保存的更改将丢失。`)) {
      try {
        const response = await documentApi.restoreDocumentVersion(documentId, version.id)
        if (response.success) {
          onRestore?.(version)
          // 刷新版本列表
          const versionsResponse = await documentApi.getDocumentVersions(documentId)
          if (versionsResponse.success && versionsResponse.data) {
            setVersions(versionsResponse.data.versions)
          }
        }
      } catch (err) {
        console.error('恢复版本失败:', err)
        alert('恢复版本失败，请稍后重试')
      }
    }
  }

  const handleView = (version: DocumentVersion) => {
    onView?.(version)
  }

  if (loading) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
            <p className="text-gray-500">加载版本历史中...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <History className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-red-500">{error}</p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-2"
              onClick={() => window.location.reload()}
            >
              重试
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (versions.length === 0) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center">
            <History className="h-12 w-12 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500">暂无版本历史</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5" />
          版本历史
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {versions.map((version) => (
            <div
              key={version.id}
              className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold text-lg">
                      版本 {version.version_number}
                    </span>
                    {version.version_number === 1 && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                        初始版本
                      </span>
                    )}
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      <span>
                        创建者: {version.created_by_name || `用户 ${version.created_by}`}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>
                        创建时间: {formatDateTime(new Date(version.created_at))}
                      </span>
                      <span className="text-gray-400">
                        ({formatDistanceToNow(new Date(version.created_at))})
                      </span>
                    </div>
                    {version.document_title && (
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span>文档: {version.document_title}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-1 ml-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleView(version)}
                    title="查看版本"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRestore(version)}
                    title="恢复到此版本"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => toggleVersionExpansion(version.id)}
                    title={expandedVersions.has(version.id) ? '收起详情' : '展开详情'}
                  >
                    {expandedVersions.has(version.id) ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
              
              {/* 版本详情 */}
              {expandedVersions.has(version.id) && (
                <div className="mt-4 pt-4 border-t">
                  <div className="space-y-3">
                    <div>
                      <h4 className="font-medium text-sm mb-2">变更摘要</h4>
                      {version.changes_summary ? (
                        <div className="bg-gray-50 p-3 rounded text-sm">
                          <pre className="whitespace-pre-wrap text-gray-700">
                            {JSON.stringify(version.changes_summary, null, 2)}
                          </pre>
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">无变更摘要</p>
                      )}
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm mb-2">内容预览</h4>
                      <div className="bg-gray-50 p-3 rounded max-h-40 overflow-y-auto">
                        <pre className="whitespace-pre-wrap text-sm text-gray-700">
                          {version.content.substring(0, 500)}
                          {version.content.length > 500 && '...'}
                        </pre>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}