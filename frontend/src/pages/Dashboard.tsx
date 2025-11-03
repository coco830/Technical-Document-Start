import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'

export default function Dashboard() {
  const navigate = useNavigate()
  const { logout } = useUserStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary">悦恩人机共写平台</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/projects')}
                className="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium"
              >
                项目列表
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
              >
                退出登录
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-3xl font-bold mb-6">工作台</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">项目管理</h3>
              <p className="text-gray-600 mb-4">创建和管理您的环保文书项目</p>
              <button
                onClick={() => navigate('/projects')}
                className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                进入
              </button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">AI 编辑器</h3>
              <p className="text-gray-600 mb-4">使用AI辅助创作应急预案</p>
              <button
                onClick={() => navigate('/editor')}
                className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700"
              >
                进入
              </button>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">模板库</h3>
              <p className="text-gray-600 mb-4">浏览和使用标准化文档模板</p>
              <button
                className="bg-gray-300 text-gray-600 px-4 py-2 rounded-md cursor-not-allowed"
                disabled
              >
                即将开放
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
