import { useState, useEffect, useCallback } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import { apiClient } from '@/utils/api'

interface Document {
  id: number
  title: string
  content: string | null
  content_type: string
  project_id: number | null
  user_id: number
  version: number
  is_template: number
  doc_metadata: Record<string, any> | null
  created_at: string
  updated_at: string
}

export default function EditorPage() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const templateId = searchParams.get('template')

  const [currentDoc, setCurrentDoc] = useState<Document | null>(null)
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [showTemplateModal, setShowTemplateModal] = useState(false)
  const [templates, setTemplates] = useState<Document[]>([])

  // TipTap 编辑器
  const editor = useEditor({
    extensions: [
      StarterKit,
      Image.configure({
        inline: true,
        allowBase64: true,
      }),
      Placeholder.configure({
        placeholder: '开始输入您的内容...',
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
    ],
    content: '',
    editorProps: {
      attributes: {
        class: 'prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto focus:outline-none min-h-[500px] px-8 py-6',
      },
    },
    onUpdate: ({ editor }) => {
      setHasUnsavedChanges(true)
    },
  })

  // 加载文档
  useEffect(() => {
    if (id) {
      fetchDocument(id)
    } else if (templateId) {
      createFromTemplate(templateId)
    } else {
      // 新建文档
      setLoading(false)
      setTitle('未命名文档')
      editor?.commands.setContent('')
    }
  }, [id, templateId])

  // 自动保存（每30秒）
  useEffect(() => {
    let autoSaveTimer: NodeJS.Timeout

    if (hasUnsavedChanges && currentDoc && editor) {
      autoSaveTimer = setTimeout(() => {
        handleAutoSave()
      }, 30000) // 30秒自动保存
    }

    return () => {
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer)
      }
    }
  }, [hasUnsavedChanges, currentDoc, editor])

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

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        handleSave()
      }
    }

    window.document.addEventListener('keydown', handleKeyDown)
    return () => window.document.removeEventListener('keydown', handleKeyDown)
  }, [currentDoc, title, editor])

  const fetchDocument = async (docId: string) => {
    try {
      setLoading(true)
      setError(null)

      const res = await apiClient.get<Document>(`/documents/${docId}`)
      const doc = res.data

      setCurrentDoc(doc)
      setTitle(doc.title)
      editor?.commands.setContent(doc.content || '')
      setLastSaved(new Date(doc.updated_at))
      setHasUnsavedChanges(false)
    } catch (error: any) {
      console.error('加载文档失败:', error)
      setError(error.message || '加载文档失败')
    } finally {
      setLoading(false)
    }
  }

  const createFromTemplate = async (tempId: string) => {
    try {
      setLoading(true)
      setError(null)

      // 获取模板内容
      const res = await apiClient.get<Document>(`/documents/${tempId}`)
      const template = res.data

      if (template.is_template !== 1) {
        alert('该文档不是模板')
        navigate('/editor')
        return
      }

      setTitle(`${template.title} - 副本`)
      editor?.commands.setContent(template.content || '')
      setHasUnsavedChanges(true)
    } catch (error: any) {
      console.error('加载模板失败:', error)
      setError(error.message || '加载模板失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAutoSave = useCallback(async () => {
    if (!currentDoc || !hasUnsavedChanges || !editor) return

    try {
      setSaving(true)

      await apiClient.post(`/documents/${currentDoc.id}/autosave`, {
        content: editor.getHTML(),
        version: currentDoc.version
      })

      setCurrentDoc({ ...currentDoc, version: currentDoc.version + 1 })
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
  }, [currentDoc, editor, hasUnsavedChanges])

  const handleSave = async () => {
    if (!editor) return

    try {
      setSaving(true)
      setError(null)

      const content = editor.getHTML()

      if (currentDoc) {
        // 更新现有文档
        const res = await apiClient.patch<Document>(`/documents/${currentDoc.id}`, {
          title,
          content,
          content_type: 'html'
        })

        setCurrentDoc(res.data)
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
        navigate(`/editor/${res.data.id}`, { replace: true })
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

  const handleImageUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return

      // 检查文件大小 (限制5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('图片大小不能超过5MB')
        return
      }

      // 转换为 Base64
      const reader = new FileReader()
      reader.onload = (e) => {
        const base64 = e.target?.result as string
        editor?.chain().focus().setImage({ src: base64 }).run()
      }
      reader.readAsDataURL(file)
    }
    input.click()
  }

  const handleAddLink = () => {
    const url = window.prompt('输入链接地址:')
    if (url) {
      editor?.chain().focus().setLink({ href: url }).run()
    }
  }

  const handleExportHTML = () => {
    if (!editor) return
    const blob = new Blob([editor.getHTML()], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || '未命名文档'}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleExportMarkdown = () => {
    if (!editor) return
    // 简单的 HTML 到 Markdown 转换
    const html = editor.getHTML()
    const markdown = html
      .replace(/<h1>(.*?)<\/h1>/g, '# $1\n\n')
      .replace(/<h2>(.*?)<\/h2>/g, '## $1\n\n')
      .replace(/<h3>(.*?)<\/h3>/g, '### $1\n\n')
      .replace(/<h4>(.*?)<\/h4>/g, '#### $1\n\n')
      .replace(/<strong>(.*?)<\/strong>/g, '**$1**')
      .replace(/<em>(.*?)<\/em>/g, '*$1*')
      .replace(/<u>(.*?)<\/u>/g, '$1')
      .replace(/<p>(.*?)<\/p>/g, '$1\n\n')
      .replace(/<ul>(.*?)<\/ul>/gs, '$1\n')
      .replace(/<ol>(.*?)<\/ol>/gs, '$1\n')
      .replace(/<li>(.*?)<\/li>/g, '- $1\n')
      .replace(/<[^>]*>/g, '')

    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title || '未命名文档'}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const fetchTemplates = async () => {
    try {
      const res = await apiClient.get<{ documents: Document[] }>('/documents/?is_template=1&page_size=50')
      setTemplates(res.data.documents)
      setShowTemplateModal(true)
    } catch (error: any) {
      console.error('获取模板列表失败:', error)
      alert('获取模板列表失败')
    }
  }

  const getWordCount = () => {
    if (!editor) return 0
    return editor.state.doc.textContent.length
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
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
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* 左侧 */}
            <div className="flex items-center space-x-4 flex-1 min-w-0">
              <button
                onClick={() => navigate('/projects')}
                className="text-gray-600 hover:text-primary flex-shrink-0"
                title="返回项目列表"
              >
                ← 返回
              </button>
              <input
                type="text"
                value={title}
                onChange={(e) => {
                  setTitle(e.target.value)
                  setHasUnsavedChanges(true)
                }}
                className="text-xl font-semibold border-none focus:outline-none focus:ring-2 focus:ring-primary px-2 py-1 rounded flex-1 min-w-0"
                placeholder="输入文档标题..."
              />
              {hasUnsavedChanges && !saving && (
                <span className="text-sm text-yellow-600 flex-shrink-0">● 未保存</span>
              )}
              {saving && (
                <span className="text-sm text-blue-600 flex-shrink-0">💾 保存中...</span>
              )}
              {lastSaved && !hasUnsavedChanges && !saving && (
                <span className="text-sm text-gray-500 hidden sm:block flex-shrink-0">
                  ✓ {lastSaved.toLocaleTimeString('zh-CN')}
                </span>
              )}
            </div>

            {/* 右侧按钮 */}
            <div className="flex items-center space-x-2 flex-shrink-0 ml-4">
              <div className="text-sm text-gray-600 hidden md:block">
                {getWordCount()} 字
              </div>
              <button
                onClick={fetchTemplates}
                className="px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm"
                title="从模板创建"
              >
                📋 模板
              </button>
              <button
                onClick={handleSave}
                disabled={saving || !title.trim()}
                className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {saving ? '保存中...' : currentDoc ? '💾 保存' : '✨ 创建'}
              </button>
            </div>
          </div>
        </div>

        {/* 编辑器工具栏 */}
        {editor && (
          <div className="border-t bg-gray-50 overflow-x-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
              <div className="flex items-center space-x-1 flex-nowrap">
                {/* 文本样式 */}
                <button
                  onClick={() => editor.chain().focus().toggleBold().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('bold') ? 'bg-gray-200' : ''}`}
                  title="粗体 (Ctrl+B)"
                >
                  <strong>B</strong>
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleItalic().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('italic') ? 'bg-gray-200' : ''}`}
                  title="斜体 (Ctrl+I)"
                >
                  <em>I</em>
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleUnderline().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('underline') ? 'bg-gray-200' : ''}`}
                  title="下划线 (Ctrl+U)"
                >
                  <u>U</u>
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleStrike().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('strike') ? 'bg-gray-200' : ''}`}
                  title="删除线"
                >
                  <s>S</s>
                </button>

                <div className="w-px h-6 bg-gray-300 mx-2"></div>

                {/* 标题 */}
                {[1, 2, 3].map(level => (
                  <button
                    key={level}
                    onClick={() => editor.chain().focus().toggleHeading({ level: level as 1 | 2 | 3 }).run()}
                    className={`p-2 rounded hover:bg-gray-200 text-sm ${editor.isActive('heading', { level }) ? 'bg-gray-200' : ''}`}
                    title={`标题 ${level}`}
                  >
                    H{level}
                  </button>
                ))}

                <div className="w-px h-6 bg-gray-300 mx-2"></div>

                {/* 列表 */}
                <button
                  onClick={() => editor.chain().focus().toggleBulletList().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('bulletList') ? 'bg-gray-200' : ''}`}
                  title="无序列表"
                >
                  ●
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleOrderedList().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('orderedList') ? 'bg-gray-200' : ''}`}
                  title="有序列表"
                >
                  1.
                </button>

                <div className="w-px h-6 bg-gray-300 mx-2"></div>

                {/* 对齐 */}
                <button
                  onClick={() => editor.chain().focus().setTextAlign('left').run()}
                  className="p-2 rounded hover:bg-gray-200 text-sm"
                  title="左对齐"
                >
                  ←
                </button>
                <button
                  onClick={() => editor.chain().focus().setTextAlign('center').run()}
                  className="p-2 rounded hover:bg-gray-200 text-sm"
                  title="居中"
                >
                  ↔
                </button>
                <button
                  onClick={() => editor.chain().focus().setTextAlign('right').run()}
                  className="p-2 rounded hover:bg-gray-200 text-sm"
                  title="右对齐"
                >
                  →
                </button>

                <div className="w-px h-6 bg-gray-300 mx-2"></div>

                {/* 引用和代码 */}
                <button
                  onClick={() => editor.chain().focus().toggleBlockquote().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('blockquote') ? 'bg-gray-200' : ''}`}
                  title="引用"
                >
                  "
                </button>
                <button
                  onClick={() => editor.chain().focus().toggleCodeBlock().run()}
                  className={`p-2 rounded hover:bg-gray-200 ${editor.isActive('codeBlock') ? 'bg-gray-200' : ''}`}
                  title="代码块"
                >
                  &lt;/&gt;
                </button>

                <div className="w-px h-6 bg-gray-300 mx-2"></div>

                {/* 链接和图片 */}
                <button
                  onClick={handleAddLink}
                  className="p-2 rounded hover:bg-gray-200"
                  title="插入链接"
                >
                  🔗
                </button>
                <button
                  onClick={handleImageUpload}
                  className="p-2 rounded hover:bg-gray-200"
                  title="插入图片"
                >
                  🖼️
                </button>

                <div className="w-px h-6 bg-gray-300 mx-2"></div>

                {/* 导出 */}
                <button
                  onClick={handleExportHTML}
                  className="px-3 py-1 text-sm rounded hover:bg-gray-200"
                  title="导出HTML"
                >
                  HTML
                </button>
                <button
                  onClick={handleExportMarkdown}
                  className="px-3 py-1 text-sm rounded hover:bg-gray-200"
                  title="导出Markdown"
                >
                  MD
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            ⚠️ {error}
          </div>
        </div>
      )}

      {/* 编辑器区域 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow-sm border min-h-[600px]">
          <EditorContent editor={editor} />
        </div>
      </div>

      {/* 模板选择模态框 */}
      {showTemplateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold">选择模板</h3>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {templates.length === 0 ? (
                <p className="text-center text-gray-500 py-8">暂无模板</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {templates.map(template => (
                    <div
                      key={template.id}
                      className="border rounded-lg p-4 hover:border-primary cursor-pointer transition"
                      onClick={() => {
                        setShowTemplateModal(false)
                        navigate(`/editor?template=${template.id}`)
                        window.location.reload() // 重新加载以应用模板
                      }}
                    >
                      <h4 className="font-semibold mb-2">{template.title}</h4>
                      <p className="text-sm text-gray-600 line-clamp-2">
                        {template.content?.replace(/<[^>]*>/g, '').substring(0, 100)}...
                      </p>
                      <div className="mt-2 text-xs text-gray-400">
                        更新于: {new Date(template.updated_at).toLocaleDateString('zh-CN')}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="p-6 border-t flex justify-end">
              <button
                onClick={() => setShowTemplateModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
