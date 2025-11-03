import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface Project {
  id: number
  name: string
  description: string
  created_at: string
}

export default function Projects() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const res = await axios.get('/api/projects')
      setProjects(res.data)
    } catch (error) {
      console.error('获取项目列表失败:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
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
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-bold">项目列表</h2>
            <button
              className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              + 新建项目
            </button>
          </div>
          {projects.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">暂无项目，点击上方按钮创建您的第一个项目</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <div key={project.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                  <h3 className="text-xl font-semibold mb-2">{project.name}</h3>
                  <p className="text-gray-600 mb-4">{project.description}</p>
                  <p className="text-sm text-gray-400 mb-4">创建于: {new Date(project.created_at).toLocaleDateString()}</p>
                  <button
                    onClick={() => navigate(`/editor/${project.id}`)}
                    className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700"
                  >
                    打开项目
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
