import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'

interface Document {
  id: number
  title: string
  content: string | null
  content_type: string
  project_id: number | null
  user_id: number
  version: int
  is_template: number
  metadata: Record<string, any> | null
  created_at: string
  updated_at: string
}

export default function EditorPage() {
  const navigate = useNavigate()
  const { documentId } = useParams<{ documentId: string }>()

  const [document, setDocument] = useState<Document | null>(null)
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const quillRef = useRef<ReactQuill>(null)
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null)

  // Quill 编辑器配置
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'font': [] }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      [{ 'align': [] }],
      ['blockquote', 'code-block'],
      ['link', 'image', 'video'],
      ['clean']
    ],
  }

  const formats = [
    'header', 'font', 'size',
    'bold', 'italic', 'underline', 'strike',
    'color', 'background',
    'script',
    'list', 'bullet', 'indent',
    'align',
    'blockquote', 'code-block',
    'link', 'image', 'video'
  ]

  // 加载文档
  useEffect(() => {
    if (documentId) {
      fetchDocument()
    } else {
      // 新建文档
      setLoading(false)
      setTitle('未命名文档')
      setContent('')
    }
  }, [documentId])

  // 自动保存（每30秒）
  useEffect(() => {
    if (hasUnsavedChanges && document) {
      autoSaveTimerRef.current = setTimeout(() => {
        handleAutoSave()
      }, 30000) // 30秒自动保存
    }

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current)
      }
    }
  }, [content, hasUnsavedChanges, document])

  // 防止未保存离开
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = '您有未保存的更改，确定要离开吗？'
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [hasUnsavedChanges])

  const fetchDocument = async () => {
    try {
      setLoading(true)
      setError(null)

      const res = await apiClient.get<Document>(`/documents/${documentId}`)
      const doc = res.data

      setDocument(doc)
      setTitle(doc.title)
      setContent(doc.content || '')
      setLastSaved(new Date(doc.updated_at))
    } catch (error: any) {
      console.error('加载文档失败:', error)
      setError(error.message || '加载文档失败')
    } finally {
      setLoading(false)
    }
  }

  const handleContentChange = (value: string) => {
    setContent(value)
    setHasUnsavedChanges(true)
  }

  const handleTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTitle(e.target.value)
    setHasUnsavedChanges(true)
  }

  const handleAutoSave = useCallback(async () => {
    if (!document || !hasUnsavedChanges) return

    try {
      setSaving(true)

      await apiClient.post(`/documents/${document.id}/autosave`, {
        content,
        version: document.version
      })

      setDocument({ ...document, version: document.version + 1 })
      setLastSaved(new Date())
      setHasUnsavedChanges(false)
    } catch (error: any) {
      console.error('自动保存失败:', error)

      if (error.response?.status === 409) {
        alert('文档已被其他用户修改，请刷新页面获取最新版本')
      }
    } finally {
      setSaving(false)
    }
  }, [document, content, hasUnsavedChanges])

  const handleSave = async () => {
    try {
      setSaving(true)
      setError(null)

      if (document) {
        // 更新现有文档
        const res = await apiClient.patch<Document>(`/documents/${document.id}`, {
          title,
          content,
          content_type: 'html'
        })

        setDocument(res.data)
        setLastSaved(new Date())
        setHasUnsavedChanges(false)
        alert('保存成功！')
      } else {
        // 创建新文档
        const res = await apiClient.post<Document>('/documents/', {
          title,
          content,
          content_type: 'html',
          is_template: 0
        })

        setDocument(res.data)
        setLastSaved(new Date())
        setHasUnsavedChanges(false)
        navigate(`/editor/${res.data.id}`)
        alert('文档创建成功！')
      }
    } catch (error: any) {
      console.error('保存失败:', error)
      setError(error.response?.data?.detail || '保存失败')
      alert(error.response?.data?.detail || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  const handleExport = () => {
    // 导出为 HTML 文件
    const blob = new Blob([content], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || '未命名文档'}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getWordCount = () => {
    const text = content.replace(/<[^>]*>/g, '').trim()
    return text.length
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部工具栏 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* 左侧 */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="text-gray-600 hover:text-primary"
              >
                ← 返回
              </button>
              <input
                type="text"
                value={title}
                onChange={handleTitleChange}
                className="text-xl font-semibold border-none focus:outline-none focus:ring-2 focus:ring-primary px-2 py-1 rounded"
                placeholder="输入文档标题..."
              />
              {hasUnsavedChanges && (
                <span className="text-sm text-yellow-600">● 未保存</span>
              )}
              {saving && (
                <span className="text-sm text-gray-500">保存中...</span>
              )}
              {lastSaved && !hasUnsavedChanges && !saving && (
                <span className="text-sm text-gray-500">
                  最后保存: {lastSaved.toLocaleTimeString('zh-CN')}
                </span>
              )}
            </div>

            {/* 右侧按钮 */}
            <div className="flex items-center space-x-2">
              <div className="text-sm text-gray-600">
                字数: {getWordCount()}
              </div>
              <button
                onClick={handleExport}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                disabled={!content}
              >
                导出 HTML
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !title.trim()}
                className="bg-primary text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {saving ? '保存中...' : document ? '保存' : '创建文档'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      {/* 编辑器区域 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm">
          <ReactQuill
            ref={quillRef}
            theme="snow"
            value={content}
            onChange={handleContentChange}
            modules={modules}
            formats={formats}
            placeholder="开始输入您的内容..."
            className="h-[calc(100vh-250px)]"
          />
        </div>
      </div>

      {/* 快捷键提示 */}
      <div className="fixed bottom-4 right-4 bg-white px-4 py-2 rounded-lg shadow-lg border text-sm text-gray-600">
        <div className="font-semibold mb-1">快捷键</div>
        <div>Ctrl+S: 保存文档</div>
        <div>Ctrl+B: 粗体</div>
        <div>Ctrl+I: 斜体</div>
        <div>Ctrl+U: 下划线</div>
      </div>
    </div>
  )
}
