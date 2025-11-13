import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import ProjectLayout from '@/components/ProjectLayout'

interface Project {
  id: number
  title: string
  description: string | null
  status: 'active' | 'completed' | 'archived'
  user_id: number
  created_at: string
  updated_at: string
}

interface ProgressStep {
  id: string
  title: string
  status: 'completed' | 'in_progress' | 'pending'
  description: string
  route: string
}

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 项目进度步骤
  const progressSteps: ProgressStep[] = [
    {
      id: 'enterprise',
      title: '企业信息收集',
      status: 'in_progress',
      description: '收集企业基本信息、生产过程、环境信息和环保手续',
      route: `/project/${id}/enterprise`
    },
    {
      id: 'ai-generate',
      title: 'AI智能生成',
      status: 'pending',
      description: '选择模板并使用AI生成应急预案文档',
      route: `/project/${id}/ai-generate`
    },
    {
      id: 'edit',
      title: '编辑校对',
      status: 'pending',
      description: '对生成的文档进行编辑和校对',
      route: `/project/${id}/editor`
    },
    {
      id: 'export',
      title: '文档导出',
      status: 'pending',
      description: '导出最终文档为PDF或Word格式',
      route: `/project/${id}/export`
    }
  ]

  useEffect(() => {
    if (id) {
      fetchProject()
    }
  }, [id])

  const fetchProject = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get(`/projects/${id}`)
      setProject(response.data)
    } catch (err) {
      console.error('获取项目信息失败:', err)
      setError('获取项目信息失败')
    } finally {
      setLoading(false)
    }
  }

  const handleStepClick = (step: ProgressStep) => {
    if (step.status !== 'pending') {
      navigate(step.route)
    }
  }

  if (loading) {
    return (
      <ProjectLayout title="项目概览">
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">加载中...</p>
        </div>
      </ProjectLayout>
    )
  }

  if (error || !project) {
    return (
      <ProjectLayout title="项目概览">
        <div className="text-center py-12">
          <p className="text-red-500 text-lg">{error || '项目不存在'}</p>
        </div>
      </ProjectLayout>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'completed': return 'bg-blue-100 text-blue-800'
      case 'archived': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return '进行中'
      case 'completed': return '已完成'
      case 'archived': return '已归档'
      default: return '未知'
    }
  }

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'in_progress': return '🔄'
      case 'pending': return '⏳'
      default: return '⏳'
    }
  }

  return (
    <ProjectLayout title="项目概览" projectId={project.id}>
      {/* 项目基本信息 */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">{project.title}</h1>
            <p className="text-gray-600 mb-4">
              {project.description || '暂无描述'}
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>创建时间: {new Date(project.created_at).toLocaleDateString('zh-CN')}</span>
              <span>更新时间: {new Date(project.updated_at).toLocaleDateString('zh-CN')}</span>
            </div>
          </div>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(project.status)}`}>
            {getStatusText(project.status)}
          </div>
        </div>
      </div>

      {/* 项目进度 */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">项目进度</h2>

        {/* 进度条 */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>完成进度</span>
            <span>25%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div className="bg-blue-600 h-3 rounded-full transition-all duration-300" style={{ width: '25%' }}></div>
          </div>
        </div>

        {/* 步骤列表 */}
        <div className="space-y-4">
          {progressSteps.map((step, index) => (
            <div
              key={step.id}
              className={`border rounded-lg p-4 transition-all ${
                step.status === 'in_progress'
                  ? 'border-blue-300 bg-blue-50'
                  : step.status === 'completed'
                  ? 'border-green-300 bg-green-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white border-2 border-gray-300">
                    <span className="text-sm">{getStepIcon(step.status)}</span>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{step.title}</h3>
                    <p className="text-sm text-gray-600">{step.description}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className={`text-sm font-medium ${
                    step.status === 'completed' ? 'text-green-600' :
                    step.status === 'in_progress' ? 'text-blue-600' :
                    'text-gray-400'
                  }`}>
                    {step.status === 'completed' ? '已完成' :
                     step.status === 'in_progress' ? '进行中' :
                     '待开始'}
                  </span>

                  {step.status !== 'pending' && (
                    <button
                      onClick={() => handleStepClick(step)}
                      className="px-4 py-2 text-sm font-medium text-primary hover:text-green-700 transition-colors"
                    >
                      {step.status === 'in_progress' ? '继续' : '查看'}
                    </button>
                  )}

                  {step.status === 'pending' && (
                    <button
                      disabled
                      className="px-4 py-2 text-sm font-medium text-gray-400 cursor-not-allowed"
                    >
                      待开始
                    </button>
                  )}
                </div>
              </div>

              {/* 步骤间的连接线 */}
              {index < progressSteps.length - 1 && (
                <div className="flex justify-center mt-4">
                  <div className="w-0.5 h-6 bg-gray-300"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 快速操作 */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">快速操作</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate(`/project/${id}/enterprise`)}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <span className="text-2xl">🏭</span>
            <div>
              <div className="font-medium text-gray-900">企业信息</div>
              <div className="text-sm text-gray-600">完善企业基本信息</div>
            </div>
          </button>

          <button
            onClick={() => navigate(`/project/${id}/ai-generate`)}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <span className="text-2xl">🤖</span>
            <div>
              <div className="font-medium text-gray-900">AI生成</div>
              <div className="text-sm text-gray-600">智能生成应急预案</div>
            </div>
          </button>

          <button
            onClick={() => navigate(`/project/${id}/editor`)}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <span className="text-2xl">✏️</span>
            <div>
              <div className="font-medium text-gray-900">编辑校对</div>
              <div className="text-sm text-gray-600">编辑文档内容</div>
            </div>
          </button>

          <button
            onClick={() => navigate(`/project/${id}/export`)}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <span className="text-2xl">📤</span>
            <div>
              <div className="font-medium text-gray-900">导出文档</div>
              <div className="text-sm text-gray-600">导出PDF或Word</div>
            </div>
          </button>
        </div>
      </div>
    </ProjectLayout>
  )
}