import { useEffect, ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'

interface RouteGuardProps {
  children: ReactNode
  requireAuth?: boolean
  redirectTo?: string
  allowedRoles?: string[]
}

export default function RouteGuard({ 
  children, 
  requireAuth = false, 
  redirectTo = '/login',
  allowedRoles = []
}: RouteGuardProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated, user, token } = useUserStore()

  useEffect(() => {
    // 如果需要认证但没有token，重定向到登录页
    if (requireAuth && !token) {
      navigate(redirectTo, { replace: true })
      return
    }

    // 如果有token但没有用户信息，等待AuthProvider加载用户信息
    if (token && !user) {
      return
    }

    // 如果需要认证但未认证，重定向到登录页
    if (requireAuth && token && !isAuthenticated) {
      navigate(redirectTo, { replace: true })
      return
    }

    // 如果需要特定角色但用户角色不匹配，重定向到无权限页面
    if (requireAuth && allowedRoles.length > 0 && user && !allowedRoles.includes((user as any).role || 'user')) {
      navigate('/unauthorized', { replace: true })
      return
    }

    // 如果已认证用户访问登录/注册页面，重定向到仪表盘
    if (token && isAuthenticated && user && (
      location.pathname === '/login' || 
      location.pathname === '/register'
    )) {
      navigate('/dashboard', { replace: true })
      return
    }
  }, [token, user, isAuthenticated, navigate, location.pathname, requireAuth, redirectTo, allowedRoles])

  // 如果需要认证但没有token，显示加载状态
  if (requireAuth && !token) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    )
  }

  // 如果有token但没有用户信息，显示加载状态
  if (token && !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">加载用户信息...</p>
        </div>
      </div>
    )
  }

  // 如果需要认证但未认证，不渲染子组件
  if (requireAuth && token && !isAuthenticated) {
    return null
  }

  // 如果需要特定角色但用户角色不匹配，不渲染子组件
  if (requireAuth && allowedRoles.length > 0 && user && !allowedRoles.includes((user as any).role || 'user')) {
    return null
  }

  return <>{children}</>
}