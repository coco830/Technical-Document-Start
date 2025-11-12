import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import Layout from '@/components/Layout'

interface Document {
  id: number
  title: string
  content: string | null
  content_type: string
  project_id: number | null
  user_id: number
  version: number
  is_template: number
  doc_metadata: { category?: string; description?: string } | null
  created_at: string
  updated_at: string
}

interface DocumentListResponse {
  documents: Document[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 模板分类
const TEMPLATE_CATEGORIES = [
  { value: '', label: '全部模板' },
  { value: '环保报告', label: '环保报告' },
  { value: '技术文书', label: '技术文书' },
  { value: '会议纪要', label: '会议纪要' },
  { value: '工作总结', label: '工作总结' },
  { value: '项目方案', label: '项目方案' },
  { value: '其他', label: '其他' }
]

export default function Templates() {
  const navigate = useNavigate()
  const [templates, setTemplates] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [previewTemplate, setPreviewTemplate] = useState<Document | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTemplates()
  }, [page, search, selectedCategory])

  const fetchTemplates = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '12',
        is_template: '1' // 只获取模板
      })

      if (search) params.append('search', search)

      const res = await apiClient.get<DocumentListResponse>(`/documents/?${params.toString()}`)

      // 前端过滤分类（如果选择了分类）
      let filteredTemplates = res.data.documents
      if (selectedCategory) {
        filteredTemplates = res.data.documents.filter(
          t => t.doc_metadata?.category === selectedCategory
        )
      }

      setTemplates(filteredTemplates)
      setTotal(res.data.total)
      setTotalPages(res.data.total_pages)
    } catch (error: any) {
      console.error('获取模板列表失败:', error)
      setError(error.message || '获取模板列表失败')
    } finally {
      setLoading(false)
    }
  }

  const createFromTemplate = async (templateId: number, title: string) => {
    try {
      const response = await apiClient.post(`/documents/from-template/${templateId}?title=${encodeURIComponent(title)}`)

      // 跳转到新文档编辑器
      navigate(`/editor/${response.data.id}`)
    } catch (error: any) {
      console.error('从模板创建文档失败:', error)
      alert(error.response?.data?.detail || '从模板创建文档失败')
    }
  }

  const handleUseTemplate = (template: Document) => {
    const title = window.prompt('请输入新文档标题:', `${template.title} - 副本`)
    if (title && title.trim()) {
      createFromTemplate(template.id, title.trim())
    }
  }

  const handlePreview = (template: Document) => {
    setPreviewTemplate(template)
  }

  const closePreview = () => {
    setPreviewTemplate(null)
  }

  return (
    <Layout
      title="模板库"
      showBackButton={true}
    >
      <div className="mb-4 text-gray-600">
        共 {total} 个模板
      </div>
        {/* 筛选和搜索栏 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* 搜索框 */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="搜索模板..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value)
                  setPage(1)
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            {/* 分类筛选 */}
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value)
                setPage(1)
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              {TEMPLATE_CATEGORIES.map(cat => (
                <option key={cat.value} value={cat.value}>
                  {cat.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* 模板网格 */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="mt-4 text-gray-600">加载中...</p>
          </div>
        ) : templates.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <p className="text-gray-500 text-lg">暂无模板</p>
            <p className="text-gray-400 text-sm mt-2">
              {search || selectedCategory ? '尝试调整筛选条件' : '创建文档时可以将其标记为模板'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200 overflow-hidden"
              >
                {/* 分类标签 */}
                {template.doc_metadata?.category && (
                  <div className="bg-primary/10 px-4 py-2 border-b border-gray-100">
                    <span className="text-xs font-medium text-primary">
                      {template.doc_metadata.category}
                    </span>
                  </div>
                )}

                <div className="p-6">
                  {/* 标题 */}
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {template.title}
                  </h3>

                  {/* 描述 */}
                  {template.doc_metadata?.description && (
                    <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                      {template.doc_metadata.description}
                    </p>
                  )}

                  {/* 元信息 */}
                  <div className="text-xs text-gray-400 mb-4">
                    更新于 {new Date(template.updated_at).toLocaleDateString('zh-CN')}
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handlePreview(template)}
                      className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm"
                    >
                      预览
                    </button>
                    <button
                      onClick={() => handleUseTemplate(template)}
                      className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      使用模板
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 分页 */}
        {!loading && templates.length > 0 && totalPages > 1 && (
          <div className="mt-8 flex justify-center items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <span className="text-gray-600">
              第 {page} / {totalPages} 页
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        )}

      {/* 预览模态框 */}
      {previewTemplate && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            {/* 模态框头部 */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">
                  {previewTemplate.title}
                </h2>
                {previewTemplate.doc_metadata?.category && (
                  <span className="inline-block mt-1 text-xs px-2 py-1 bg-primary/10 text-primary rounded">
                    {previewTemplate.doc_metadata.category}
                  </span>
                )}
              </div>
              <button
                onClick={closePreview}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ✕
              </button>
            </div>

            {/* 模态框内容 */}
            <div className="flex-1 overflow-y-auto p-6">
              {previewTemplate.doc_metadata?.description && (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    {previewTemplate.doc_metadata.description}
                  </p>
                </div>
              )}

              <div
                className="prose prose-sm max-w-none"
                dangerouslySetInnerHTML={{ __html: previewTemplate.content || '<p class="text-gray-400">暂无内容</p>' }}
              />
            </div>

            {/* 模态框底部 */}
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={closePreview}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                关闭
              </button>
              <button
                onClick={() => {
                  closePreview()
                  handleUseTemplate(previewTemplate)
                }}
                className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                使用此模板
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
