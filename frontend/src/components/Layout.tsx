import { ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'

interface LayoutProps {
  children: ReactNode
  showNav?: boolean
}

export default function Layout({ children, showNav = true }: LayoutProps) {
  const navigate = useNavigate()
  const { token, logout } = useUserStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {showNav && (
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center space-x-8">
                <h1
                  className="text-2xl font-bold text-primary cursor-pointer hover:text-green-700 transition-colors"
                  onClick={() => navigate('/')}
                >
                  🌿 悦恩平台
                </h1>
                {token && (
                  <div className="hidden md:flex space-x-4">
                    <button
                      onClick={() => navigate('/dashboard')}
                      className="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      工作台
                    </button>
                    <button
                      onClick={() => navigate('/projects')}
                      className="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      项目列表
                    </button>
                    <button
                      onClick={() => navigate('/editor')}
                      className="text-gray-700 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      编辑器
                    </button>
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-4">
                {token ? (
                  <>
                    <span className="text-sm text-gray-600">欢迎回来</span>
                    <button
                      onClick={handleLogout}
                      className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors text-sm font-medium"
                    >
                      退出登录
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => navigate('/login')}
                      className="text-gray-700 hover:text-primary px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      登录
                    </button>
                    <button
                      onClick={() => navigate('/register')}
                      className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors text-sm font-medium"
                    >
                      注册
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </nav>
      )}
      <main className="w-full">
        {children}
      </main>
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2025 悦恩人机共写平台 v2.1.0 | 让环保文书创作更智能
          </p>
        </div>
      </footer>
    </div>
  )
}
