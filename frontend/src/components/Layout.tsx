import { ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'

interface LayoutProps {
  children: ReactNode
  title?: string
  showBackButton?: boolean
  actions?: ReactNode
}

export default function Layout({ children, title, showBackButton = false, actions }: LayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useUserStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActiveRoute = (path: string) => {
    return location.pathname === path
  }

  const navItems = [
    { path: '/dashboard', label: '工作台', icon: '🏠' },
    { path: '/projects', label: '项目管理', icon: '📁' },
    { path: '/templates', label: '模板管理', icon: '🧩' }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* 左侧 */}
            <div className="flex items-center">
              {showBackButton && (
                <button
                  onClick={() => navigate(-1)}
                  className="mr-4 text-gray-600 hover:text-primary transition-colors"
                  title="返回"
                >
                  ← 返回
                </button>
              )}
              <h1
                className="text-2xl font-bold text-primary cursor-pointer"
                onClick={() => navigate('/dashboard')}
              >
                🌿 悦恩人机共写平台
              </h1>
              {title && (
                <span className="ml-4 text-gray-400">/</span>
              )}
              {title && (
                <span className="ml-4 text-lg font-medium text-gray-700">{title}</span>
              )}
            </div>

            {/* 右侧 */}
            <div className="flex items-center space-x-4">
              {actions}
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-600">
                  欢迎，{user?.name || '用户'}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors text-sm"
                >
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* 侧边导航栏（仅在非编辑器页面显示） */}
      {!location.pathname.startsWith('/editor') && (
        <div className="flex">
          <aside className="w-64 bg-white shadow-sm min-h-[calc(100vh-4rem)]">
            <nav className="mt-5 px-2">
              <div className="space-y-1">
                {navItems.map((item) => (
                  <button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    className={`w-full text-left group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors ${
                      isActiveRoute(item.path)
                        ? 'bg-primary text-white'
                        : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                    }`}
                  >
                    <span className="mr-3 text-lg">{item.icon}</span>
                    {item.label}
                  </button>
                ))}
              </div>
            </nav>
          </aside>

          {/* 主内容区域 */}
          <main className="flex-1">
            <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
              <div className="px-4 py-6 sm:px-0">
                {children}
              </div>
            </div>
          </main>
        </div>
      )}

      {/* 编辑器页面直接显示内容，不显示侧边栏 */}
      {location.pathname.startsWith('/editor') && (
        <main className="flex-1">
          {children}
        </main>
      )}
    </div>
  )
}
