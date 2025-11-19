import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import Layout from '@/components/Layout'

interface Project {
  id: number
  title: string
  description: string | null
  status: 'active' | 'completed' | 'archived'
  user_id: number
  created_at: string
  updated_at: string
  progress?: number
}

interface ProjectStats {
  active: number
  completed: number
  thisMonth: number
  total: number
}

export default function Dashboard() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [stats, setStats] = useState<ProjectStats>({
    active: 0,
    completed: 0,
    thisMonth: 0,
    total: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)

      // 获取项目列表
      const projectsRes = await apiClient.get('/projects/?page_size=5&status=active')
      const projectsData = projectsRes.data?.projects || []

      // 计算统计数据
      const allProjectsRes = await apiClient.get('/projects/?page_size=100')
      const allProjects = allProjectsRes.data?.projects || []

      const currentMonth = new Date().getMonth()
      const currentYear = new Date().getFullYear()

      const thisMonthProjects = allProjects.filter(project => {
        const createdAt = new Date(project.created_at)
        return createdAt.getMonth() === currentMonth && createdAt.getFullYear() === currentYear
      })

      setStats({
        active: allProjects.filter(p => p.status === 'active').length,
        completed: allProjects.filter(p => p.status === 'completed').length,
        thisMonth: thisMonthProjects.length,
        total: allProjects.length
      })

      // 添加模拟进度数据
      const projectsWithProgress = projectsData.map(project => ({
        ...project,
        progress: Math.floor(Math.random() * 100) // 模拟进度，实际应从后端获取
      }))

      setProjects(projectsWithProgress)
    } catch (error) {
      console.error('获取工作台数据失败:', error)
      // 在错误情况下设置空数据，避免null引用错误
      setProjects([])
      setStats({
        active: 0,
        completed: 0,
        thisMonth: 0,
        total: 0
      })
    } finally {
      setLoading(false)
    }
  }

  const getProgressColor = (progress: number) => {
    if (progress >= 75) return 'bg-green-500'
    if (progress >= 50) return 'bg-blue-500'
    if (progress >= 25) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      archived: 'bg-gray-100 text-gray-800'
    }
    const labels = {
      active: '进行中',
      completed: '已完成',
      archived: '已归档'
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${badges[status as keyof typeof badges]}`}>
        {labels[status as keyof typeof labels]}
      </span>
    )
  }

  const handleContinueProject = (projectId: number) => {
    navigate(`/project/${projectId}`)
  }

  const handleCreateProject = () => {
    navigate('/projects')
    // 可以添加一个延迟来确保页面加载后再触发创建模态框
    setTimeout(() => {
      // 这里可以触发项目管理页面的创建项目模态框
    }, 100)
  }

  return (
    <Layout title="工作台">
      {loading ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">加载中...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* 欢迎区域 */}
          <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-lg p-6 text-white">
            <h1 className="text-3xl font-bold mb-2">
              👋 欢迎回来，{localStorage.getItem('userName') || '用户'}
            </h1>
            <p className="text-lg opacity-90">
              悦恩应急预案人机共写平台，让应急预案编制更简单高效
            </p>
          </div>

          {/* 项目概览统计 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">📊 我的项目概览</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-yellow-600">{stats.active}</div>
                <div className="text-sm text-yellow-800">进行中</div>
              </div>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
                <div className="text-sm text-green-800">已完成</div>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-600">{stats.thisMonth}</div>
                <div className="text-sm text-blue-800">本月创建</div>
              </div>
              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-600">{stats.total}</div>
                <div className="text-sm text-purple-800">总计</div>
              </div>
            </div>
          </div>

          {/* 快速开始区域 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">🚀 快速开始</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={handleCreateProject}
                className="p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary hover:bg-green-50 transition-all text-left group"
              >
                <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">🆕</div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">创建新项目</h3>
                <p className="text-sm text-gray-600">从零开始创建一个新的应急预案项目</p>
              </button>

              <button
                onClick={() => navigate('/projects')}
                className="p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary hover:bg-green-50 transition-all text-left group"
              >
                <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">📋</div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">继续编辑</h3>
                <p className="text-sm text-gray-600">
                  {projects && projects.length > 0
                    ? `继续编辑未完成的项目: "${projects[0].title}"`
                    : '查看和编辑您的项目'}
                </p>
              </button>

              <button
                onClick={() => navigate('/templates')}
                className="p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary hover:bg-green-50 transition-all text-left group"
              >
                <div className="text-3xl mb-3 group-hover:scale-110 transition-transform">📂</div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">使用模板</h3>
                <p className="text-sm text-gray-600">基于模板快速创建预案</p>
              </button>
            </div>
          </div>

          {/* 最近项目 */}
          {projects && projects.length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">📈 最近项目</h2>
                <button
                  onClick={() => navigate('/projects')}
                  className="text-primary hover:text-green-700 text-sm font-medium"
                >
                  查看全部 →
                </button>
              </div>
              <div className="space-y-4">
                {projects.map((project) => (
                  <div key={project.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl">📄</div>
                        <div>
                          <h3 className="font-semibold text-gray-800">{project.title}</h3>
                          <p className="text-sm text-gray-500">
                            创建于: {new Date(project.created_at).toLocaleDateString('zh-CN')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getStatusBadge(project.status)}
                        <div className="text-sm text-gray-600">
                          {project.progress}% 完成
                        </div>
                      </div>
                    </div>

                    {/* 进度条 */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                      <div
                        className={`h-2 rounded-full ${getProgressColor(project.progress || 0)}`}
                        style={{ width: `${project.progress || 0}%` }}
                      ></div>
                    </div>

                    {/* 操作按钮 */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleContinueProject(project.id)}
                        className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors text-sm"
                      >
                        {project.status === 'completed' ? '查看项目' : '进入项目'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 学习资源 */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">📚 学习资源</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <div className="text-2xl mb-2">📖</div>
                <h3 className="font-medium text-gray-800">使用指南</h3>
                <p className="text-sm text-gray-600">了解如何使用平台功能</p>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <div className="text-2xl mb-2">🎥</div>
                <h3 className="font-medium text-gray-800">视频教程</h3>
                <p className="text-sm text-gray-600">观看操作演示视频</p>
              </button>
              <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left">
                <div className="text-2xl mb-2">❓</div>
                <h3 className="font-medium text-gray-800">常见问题</h3>
                <p className="text-sm text-gray-600">查看常见问题解答</p>
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}
