'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import RichTextEditor from '@/components/editor/RichTextEditor'
import EditorToolbar from '@/components/editor/EditorToolbar'
import EditorMenuBar from '@/components/editor/EditorMenuBar'
import AIWritingAssistant from '@/components/documents/AIWritingAssistant'
import { DocumentWithDetails, DocumentUpdate, DocumentFormat, ExportFormat } from '@/types'
import { documentApi } from '@/lib/api'
import { formatDateTime } from '@/lib/utils'
import { 
  ArrowLeft, 
  Save, 
  Eye,
  Loader2,
  Maximize2,
  Minimize2
} from 'lucide-react'

export default function DocumentEditPage() {
  const params = useParams()
  const router = useRouter()
  const documentId = parseInt(params.id as string)
  
  const [document, setDocument] = useState<DocumentWithDetails | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [content, setContent] = useState('')
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [showAIAssistant, setShowAIAssistant] = useState(false)
  const [autoSaveTimer, setAutoSaveTimer] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (documentId) {
      fetchDocument()
    }
    
    return () => {
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer)
      }
    }
  }, [documentId])

  useEffect(() => {
    if (document && content !== document.content) {
      setHasUnsavedChanges(true)
    } else {
      setHasUnsavedChanges(false)
    }
  }, [content, document])

  const fetchDocument = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await documentApi.getDocument(documentId)
      
      if (response.success && response.data) {
        setDocument(response.data)
        setContent(response.data.content || '')
      }
    } catch (err) {
      console.error('获取文档详情失败:', err)
      setError('获取文档详情失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = useCallback(async () => {
    if (!document) return

    try {
      setSaving(true)
      
      const updateData: DocumentUpdate = {
        content,
        format: document.format,
        status: document.status,
      }
      
      const response = await documentApi.updateDocument(documentId, updateData)
      
      if (response.success && response.data) {
        setDocument(response.data)
        setHasUnsavedChanges(false)
      }
    } catch (err) {
      console.error('保存文档失败:', err)
      alert('保存文档失败，请稍后重试')
    } finally {
      setSaving(false)
    }
  }, [document, content])

  const handleAutoSave = useCallback(async () => {
    if (!document || !hasUnsavedChanges) return

    try {
      const updateData: DocumentUpdate = {
        content,
        format: document.format,
        status: document.status,
      }
      
      await documentApi.autoSaveDocument(documentId, updateData)
    } catch (err) {
      console.error('自动保存失败:', err)
    }
  }, [document, content, hasUnsavedChanges])

  const handleContentChange = useCallback((newContent: string) => {
    setContent(newContent)
    
    // 设置自动保存定时器
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer)
    }
    
    const timer = setTimeout(() => {
      handleAutoSave()
    }, 2000) // 2秒后自动保存
    
    setAutoSaveTimer(timer)
  }, [autoSaveTimer, handleAutoSave])

  const handlePreview = () => {
    setShowPreview(!showPreview)
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
      await documentApi.exportDocument(documentId, {
        format: exportFormat,
      })
    } catch (err) {
      console.error('导出文档失败:', err)
    }
  }

  const handleVersionHistory = () => {
    router.push(`/documents/${documentId}/versions`)
  }

  const handleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  const handleBack = () => {
    if (hasUnsavedChanges) {
      if (window.confirm('有未保存的更改，确定要离开吗？')) {
        router.back()
      }
    } else {
      router.back()
    }
  }

  const handleView = () => {
    router.push(`/documents/${documentId}`)
  }

  const handleAIContentGenerated = (generatedContent: string) => {
    setContent(prev => prev + '\n\n' + generatedContent)
  }

  const handleInsertToEditor = (contentToInsert: string) => {
    setContent(prev => prev + '\n\n' + contentToInsert)
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
          <Button onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className={`h-screen flex flex-col ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}>
      {/* 编辑器菜单栏 */}
      <EditorMenuBar
        editor={null} // 这里需要传入实际的editor实例
        onSave={handleSave}
        onPreview={handlePreview}
        onExport={handleExport}
        onVersionHistory={handleVersionHistory}
        onFullscreen={handleFullscreen}
        isFullscreen={isFullscreen}
        isSaving={saving}
        hasUnsavedChanges={hasUnsavedChanges}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* 主编辑区域 */}
        <div className={`flex-1 flex flex-col ${showAIAssistant ? 'lg:flex-row' : ''}`}>
          {/* 工具栏 */}
          <EditorToolbar editor={null} /> {/* 这里需要传入实际的editor实例 */}
          
          {/* 编辑器 */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-auto p-4">
              <RichTextEditor
                content={content}
                onChange={handleContentChange}
                placeholder="开始编写您的文档..."
                editable={!showPreview}
                className="min-h-full"
              />
            </div>
          </div>
        </div>

        {/* AI写作助手 */}
        {showAIAssistant && (
          <div className="w-80 border-l overflow-hidden">
            <div className="h-full overflow-y-auto p-4">
              <AIWritingAssistant
                documentId={documentId}
                documentContent={content}
                onContentGenerated={handleAIContentGenerated}
                onInsertToEditor={handleInsertToEditor}
              />
            </div>
          </div>
        )}
      </div>

      {/* 底部操作栏 */}
      <div className="border-t bg-gray-50 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>
          
          <Button variant="outline" size="sm" onClick={handleView}>
            <Eye className="h-4 w-4 mr-2" />
            查看
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAIAssistant(!showAIAssistant)}
          >
            AI助手
          </Button>
        </div>
        
        <div className="text-sm text-gray-500">
          最后保存: {formatDateTime(new Date())}
        </div>
      </div>
    </div>
  )
}
