import { ReactNode, useState, useEffect } from 'react'
import { useNavigate, useLocation, useParams } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'

interface ProjectLayoutProps {
  children: ReactNode
  title?: string
  projectId?: number
}

export default function ProjectLayout({ children, title, projectId }: ProjectLayoutProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useUserStore()
  const { id } = useParams()

  // 使用URL参数或传入的projectId
  const currentProjectId = projectId || parseInt(id || '0')
  
  // 子菜单展开状态管理
  const [expandedMenus, setExpandedMenus] = useState<Set<string>>(new Set())
  
  // 初始化时自动展开当前路径所在的菜单
  useEffect(() => {
    const currentPath = location.pathname
    const newExpandedMenus = new Set<string>()
    
    projectNavItems.forEach(item => {
      if (item.children) {
        // 检查当前路径是否在此菜单或其子菜单下
        if (currentPath.startsWith(item.path) ||
            item.children.some(child => currentPath.startsWith(child.path))) {
          newExpandedMenus.add(item.path)
        }
      }
    })
    
    setExpandedMenus(newExpandedMenus)
  }, [location.pathname])

  const handleBackToProjects = () => {
    navigate('/projects')
  }

  const isActiveRoute = (path: string) => {
    return location.pathname.startsWith(path)
  }
  
  const isExactRoute = (path: string) => {
    return location.pathname === path
  }
  
  const toggleMenu = (path: string) => {
    setExpandedMenus(prev => {
      const newSet = new Set(prev)
      if (newSet.has(path)) {
        newSet.delete(path)
      } else {
        newSet.add(path)
      }
      return newSet
    })
  }
  
  // 计算项目完成进度
  const calculateProgress = () => {
    const steps = [
      `/project/${currentProjectId}`,
      `/project/${currentProjectId}/enterprise`,
      `/project/${currentProjectId}/ai-generate`,
      `/project/${currentProjectId}/editor`,
      `/project/${currentProjectId}/export`
    ]
    
    let completedSteps = 0
    steps.forEach(step => {
      if (location.pathname.startsWith(step)) {
        completedSteps++
        // 如果当前在企业信息、AI生成或导出页面，检查子页面进度
        if (step.includes('/enterprise') && location.pathname !== step) {
          completedSteps += 0.2 // 企业信息子页面进度
        } else if (step.includes('/ai-generate') && location.pathname !== step) {
          completedSteps += 0.2 // AI生成子页面进度
        } else if (step.includes('/export') && location.pathname !== step) {
          completedSteps += 0.2 // 导出子页面进度
        }
      }
    })
    
    return Math.min(Math.round((completedSteps / steps.length) * 100), 100)
  }
  
  const getProgressText = () => {
    const progress = calculateProgress()
    if (progress <= 20) return '项目概览'
    if (progress <= 40) return '企业信息收集'
    if (progress <= 60) return 'AI生成文档'
    if (progress <= 80) return '编辑校对'
    return '导出文档'
  }

  // 项目内部导航菜单
  const projectNavItems = [
    {
      path: `/project/${currentProjectId}`,
      label: '项目概览',
      icon: '📄',
      description: '查看项目基本信息和进度'
    },
    {
      path: `/project/${currentProjectId}/enterprise`,
      label: '企业信息',
      icon: '🏭',
      description: '企业基本信息收集',
      children: [
        {
          path: `/project/${currentProjectId}/enterprise`,
          label: '企业基本信息',
          icon: '📝'
        },
        {
          path: `/project/${currentProjectId}/enterprise/production`,
          label: '生产过程与风险物质',
          icon: '⚙️'
        },
        {
          path: `/project/${currentProjectId}/enterprise/environment`,
          label: '环境信息',
          icon: '🌍'
        },
        {
          path: `/project/${currentProjectId}/enterprise/permits`,
          label: '环保手续与管理制度',
          icon: '📋'
        },
        {
          path: `/project/${currentProjectId}/enterprise/emergency`,
          label: '应急管理与资源',
          icon: '🚨'
        }
      ]
    },
    {
      path: `/project/${currentProjectId}/ai-generate`,
      label: 'AI 生成',
      icon: '🤖',
      description: 'AI智能生成预案文档',
      children: [
        {
          path: `/project/${currentProjectId}/ai-generate`,
          label: '选择模板',
          icon: '📋'
        },
        {
          path: `/project/${currentProjectId}/ai-generate/chapters`,
          label: '生成章节',
          icon: '🔧'
        },
        {
          path: `/project/${currentProjectId}/ai-generate/history`,
          label: '历史记录',
          icon: '📚'
        }
      ]
    },
    {
      path: `/project/${currentProjectId}/editor`,
      label: '编辑校对',
      icon: '✏️',
      description: '文档编辑与校对'
    },
    {
      path: `/project/${currentProjectId}/export`,
      label: '导出',
      icon: '📤',
      description: '文档导出功能',
      children: [
        {
          path: `/project/${currentProjectId}/export/pdf`,
          label: 'PDF 导出',
          icon: '📄'
        },
        {
          path: `/project/${currentProjectId}/export/word`,
          label: 'Word 导出',
          icon: '📝'
        },
        {
          path: `/project/${currentProjectId}/export/history`,
          label: '导出历史',
          icon: '📚'
        }
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* 左侧 */}
            <div className="flex items-center">
              <button
                onClick={handleBackToProjects}
                className="mr-4 text-gray-500 hover:text-gray-700 transition-colors"
              >
                ← 返回项目列表
              </button>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold mr-3">
                  Y
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">悦恩预案协作平台</h1>
                  <p className="text-xs text-gray-500">应急预案智能生成系统</p>
                </div>
              </div>
            </div>

            {/* 右侧用户信息 */}
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <span className="text-sm text-gray-600">{user?.name?.[0]}</span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex">
        {/* 项目侧边栏 */}
        <aside className="w-64 bg-white shadow-sm h-[calc(100vh-4rem)] sticky top-16">
          <div className="p-4">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
              项目导航
            </h2>

            {/* 进度指示器 */}
            <div className="mb-6 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-900 mb-2">完成进度</p>
              <div className="w-full bg-blue-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${calculateProgress()}%` }}
                ></div>
              </div>
              <p className="text-xs text-blue-700 mt-1">当前：{getProgressText()}</p>
            </div>

            <nav className="space-y-1">
              {projectNavItems.map((item) => (
                <div key={item.path}>
                  <button
                    onClick={() => {
                      if (item.children) {
                        toggleMenu(item.path)
                      }
                      navigate(item.path)
                    }}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActiveRoute(item.path)
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <span className="mr-3">{item.icon}</span>
                        <div>
                          <div>{item.label}</div>
                          {item.description && (
                            <div className={`text-xs ${
                              isActiveRoute(item.path) ? 'text-blue-100' : 'text-gray-500'
                            }`}>
                              {item.description}
                            </div>
                          )}
                        </div>
                      </div>
                      {item.children && (
                        <span className={`transform transition-transform ${
                          expandedMenus.has(item.path) ? 'rotate-90' : ''
                        }`}>
                          ▶
                        </span>
                      )}
                    </div>
                  </button>

                  {/* 子菜单 */}
                  {item.children && expandedMenus.has(item.path) && (
                    <div className="ml-6 mt-1 space-y-1">
                      {item.children.map((child) => (
                        <button
                          key={child.path}
                          onClick={() => navigate(child.path)}
                          className={`w-full text-left px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                            isExactRoute(child.path)
                              ? 'bg-green-100 text-green-800'
                              : 'text-gray-600 hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center">
                            <span className="mr-2">{child.icon}</span>
                            {child.label}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </nav>
          </div>
        </aside>

        {/* 主内容区 */}
        <main className="flex-1 p-6">
          {title && (
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  )
}