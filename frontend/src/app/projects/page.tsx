import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/utils/api'

interface Project {
  id: number
  title: string
  description: string | null
  status: 'active' | 'completed' | 'archived'
  user_id: number
  created_at: string
  updated_at: string
}

interface ProjectListResponse {
  projects: Project[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface CreateProjectData {
  title: string
  description?: string
  status?: 'active' | 'completed' | 'archived'
}

export default function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [newProject, setNewProject] = useState<CreateProjectData>({
    title: '',
    description: '',
    status: 'active'
  })
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchProjects()
  }, [page, search, statusFilter])

  const fetchProjects = async () => {
    try {
      setLoading(true)
      setError(null)

      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '9'
      })

      if (search) params.append('search', search)
      if (statusFilter) params.append('status', statusFilter)

      const res = await apiClient.get<ProjectListResponse>(`/projects/?${params.toString()}`)

      setProjects(res.data.projects)
      setTotal(res.data.total)
      setTotalPages(res.data.total_pages)
    } catch (error: any) {
      console.error('获取项目列表失败:', error)
      setError(error.message || '获取项目列表失败')
    } finally {
      setLoading(false)
    }
  }

  const createProject = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!newProject.title.trim()) {
      alert('请输入项目标题')
      return
    }

    try {
      await apiClient.post('/projects/', newProject)
      setIsCreateModalOpen(false)
      setNewProject({ title: '', description: '', status: 'active' })
      fetchProjects()
    } catch (error: any) {
      console.error('创建项目失败:', error)
      alert(error.response?.data?.detail || '创建项目失败')
    }
  }

  const deleteProject = async (projectId: number, projectTitle: string) => {
    if (!confirm(`确定要删除项目「${projectTitle}」吗？此操作不可恢复。`)) {
      return
    }

    try {
      await apiClient.delete(`/projects/${projectId}`)
      fetchProjects()
    } catch (error: any) {
      console.error('删除项目失败:', error)
      alert(error.response?.data?.detail || '删除项目失败')
    }
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

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
    setPage(1) // 重置到第一页
  }

  const handleStatusFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value)
    setPage(1) // 重置到第一页
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 导航栏 */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1
                className="text-2xl font-bold text-primary cursor-pointer"
                onClick={() => navigate('/dashboard')}
              >
                悦恩人机共写平台
              </h1>
            </div>
          </div>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* 标题和新建按钮 */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-bold">项目管理</h2>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="bg-primary text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
            >
              + 新建项目
            </button>
          </div>

          {/* 搜索和过滤 */}
          <div className="mb-6 flex gap-4">
            <input
              type="text"
              placeholder="搜索项目标题或描述..."
              value={search}
              onChange={handleSearchChange}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <select
              value={statusFilter}
              onChange={handleStatusFilterChange}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">所有状态</option>
              <option value="active">进行中</option>
              <option value="completed">已完成</option>
              <option value="archived">已归档</option>
            </select>
          </div>

          {/* 统计信息 */}
          <div className="mb-4 text-gray-600">
            共 {total} 个项目
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}

          {/* 项目列表 */}
          {loading ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">加载中...</p>
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">
                {search || statusFilter ? '没有找到匹配的项目' : '暂无项目，点击上方按钮创建您的第一个项目'}
              </p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map((project) => (
                  <div key={project.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-xl font-semibold flex-1">{project.title}</h3>
                      {getStatusBadge(project.status)}
                    </div>
                    <p className="text-gray-600 mb-4 line-clamp-2">
                      {project.description || '暂无描述'}
                    </p>
                    <p className="text-sm text-gray-400 mb-4">
                      创建于: {new Date(project.created_at).toLocaleDateString('zh-CN')}
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => navigate(`/editor/${project.id}`)}
                        className="flex-1 bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                      >
                        打开项目
                      </button>
                      <button
                        onClick={() => deleteProject(project.id, project.title)}
                        className="px-4 py-2 border border-red-300 text-red-600 rounded-md hover:bg-red-50 transition-colors"
                      >
                        删除
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* 分页 */}
              {totalPages > 1 && (
                <div className="mt-8 flex justify-center gap-2">
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    上一页
                  </button>
                  <span className="px-4 py-2">
                    第 {page} / {totalPages} 页
                  </span>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page === totalPages}
                    className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    下一页
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </main>

      {/* 创建项目模态框 */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-2xl font-bold mb-4">创建新项目</h3>
            <form onSubmit={createProject}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  项目标题 <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newProject.title}
                  onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="输入项目标题"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  项目描述
                </label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="输入项目描述（可选）"
                  rows={3}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  项目状态
                </label>
                <select
                  value={newProject.status}
                  onChange={(e) => setNewProject({ ...newProject, status: e.target.value as any })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="active">进行中</option>
                  <option value="completed">已完成</option>
                  <option value="archived">已归档</option>
                </select>
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setIsCreateModalOpen(false)
                    setNewProject({ title: '', description: '', status: 'active' })
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  取消
                </button>
                <button
                  type="submit"
                  className="flex-1 bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  创建
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
