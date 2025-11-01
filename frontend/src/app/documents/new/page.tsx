'use client'

import { useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import DocumentForm from '@/components/documents/document-form'
import { DocumentCreate, DocumentUpdate, DocumentFormat, DocumentStatus } from '@/types'
import { documentApi } from '@/lib/api'
import { ArrowLeft } from 'lucide-react'

export default function NewDocumentPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const projectId = searchParams.get('projectId') ? parseInt(searchParams.get('projectId')!) : undefined
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (data: DocumentCreate | DocumentUpdate) => {
    if (!('project_id' in data) || typeof data.project_id !== 'number') {
      setError('请选择所属项目')
      return
    }

    if (!('title' in data) || !data.title) {
      setError('文档标题不能为空')
      return
    }

    const payload: DocumentCreate = {
      title: data.title,
      content: data.content ?? '',
      format: data.format ?? DocumentFormat.MARKDOWN,
      status: data.status ?? DocumentStatus.DRAFT,
      project_id: data.project_id,
      metadata: data.metadata ?? {},
    }

    try {
      setLoading(true)
      setError(null)
      
      const response = await documentApi.createDocument(payload)
      
      if (response.success && response.data) {
        router.push(`/documents/${response.data.id}`)
      }
    } catch (err) {
      console.error('创建文档失败:', err)
      setError('创建文档失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    router.back()
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 返回按钮 */}
      <div className="mb-6">
        <Button variant="outline" onClick={handleCancel}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          返回
        </Button>
      </div>

      {/* 页面标题 */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">创建新文档</h1>
        <p className="text-gray-600">填写以下信息创建新的文档</p>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* 表单 */}
      <div className="max-w-2xl mx-auto">
        <DocumentForm
          projectId={projectId}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
          isLoading={loading}
        />
      </div>
    </div>
  )
}
