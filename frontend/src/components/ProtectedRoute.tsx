import { useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'

interface ProtectedRouteProps {
  children: ReactNode
  redirectTo?: string
}

export default function ProtectedRoute({ children, redirectTo = '/login' }: ProtectedRouteProps) {
  const navigate = useNavigate()
  const { isAuthenticated, token, user } = useUserStore()

  useEffect(() => {
    // 如果有token但没有用户信息，等待AuthProvider加载用户信息
    if (token && !user) {
      return // 不做任何操作，等待AuthProvider完成加载
    }

    // 如果没有token或未认证，重定向到登录页
    if (!token || !isAuthenticated) {
      navigate(redirectTo, { replace: true })
    }
  }, [token, isAuthenticated, user, navigate, redirectTo])

  // 如果有token但没有用户信息，显示加载状态
  if (token && !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    )
  }

  // 如果未认证，不渲染子组件
  if (!token || !isAuthenticated) {
    return null
  }

  return <>{children}</>
}