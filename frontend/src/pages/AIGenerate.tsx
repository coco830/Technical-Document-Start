import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import ProjectLayout from '@/components/ProjectLayout'

interface Template {
  id: number
  name: string
  description: string
  category: string
  sections: string[]
}

export default function AIGenerate() {
  const navigate = useNavigate()
  const { id, step } = useParams()
  const projectId = parseInt(id || '0')
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [currentView, setCurrentView] = useState<'templates' | 'chapters' | 'history'>('templates')
  
  // 根据URL参数确定当前视图
  useEffect(() => {
    if (step === 'chapters') {
      setCurrentView('chapters')
    } else if (step === 'history') {
      setCurrentView('history')
    } else {
      setCurrentView('templates')
    }
  }, [step])

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    try {
      const templatesRes = await apiClient.get('/templates/')
      setTemplates(templatesRes.data || [])
    } catch (error) {
      console.error('获取模板数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    if (!selectedTemplate) {
      alert('请选择模板')
      return
    }

    try {
      setGenerating(true)

      const response = await apiClient.post('/ai-generate/', {
        project_id: projectId,
        template_id: selectedTemplate.id
      })

      // 生成成功后跳转到项目内部的编辑器
      navigate(`/project/${projectId}/editor`)
    } catch (error: any) {
      console.error('AI生成失败:', error)
      alert(error.response?.data?.detail || 'AI生成失败')
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <ProjectLayout title="AI生成">
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">加载中...</p>
        </div>
      </ProjectLayout>
    )
  }

  return (
    <ProjectLayout title="AI生成" projectId={projectId}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* 页面标题 */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🤖 AI智能生成</h1>
          <p className="text-gray-600">选择合适的模板，让AI为您生成专业的应急预案</p>
        </div>

        {/* 模板选择 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">选择预案模板</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {templates.map((template) => (
              <div
                key={template.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  selectedTemplate?.id === template.id
                    ? 'border-primary bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedTemplate(template)}
              >
                <h3 className="font-semibold text-gray-800 mb-2">{template.name}</h3>
                <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                <div className="flex flex-wrap gap-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {template.category}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                    {template.sections?.length || 0} 个章节
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 生成配置 */}
        {selectedTemplate && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">生成配置</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700 mb-2">选中的模板</h3>
                <div className="bg-gray-50 p-3 rounded-md">
                  <p className="font-medium">{selectedTemplate.name}</p>
                  <p className="text-sm text-gray-600">{selectedTemplate.description}</p>
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-700 mb-2">包含章节</h3>
                <div className="space-y-1">
                  {selectedTemplate.sections?.map((section, index) => (
                    <div key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                      <span>✓</span>
                      <span>{section}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 生成按钮 */}
        <div className="text-center">
          <button
            onClick={handleGenerate}
            disabled={!selectedTemplate || generating}
            className="bg-primary text-white px-8 py-3 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-lg font-medium"
          >
            {generating ? '生成中...' : '🚀 开始生成'}
          </button>
        </div>
      </div>
    </ProjectLayout>
  )
}