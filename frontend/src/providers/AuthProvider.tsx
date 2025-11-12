import { useEffect, ReactNode } from 'react'
import { useUserStore } from '@/store/userStore'
import api from '@/utils/api'

interface AuthProviderProps {
  children: ReactNode
}

export default function AuthProvider({ children }: AuthProviderProps) {
  const { token, isAuthenticated, initializeAuth, setUser, logout } = useUserStore()

  useEffect(() => {
    // 初始化认证状态
    initializeAuth()
  }, [initializeAuth])

  useEffect(() => {
    // 如果有token但没有用户信息，尝试获取用户信息
    if (token && isAuthenticated && !useUserStore.getState().user) {
      const fetchUserInfo = async () => {
        try {
          const response = await api.get('/auth/verify')
          setUser(response.data)
        } catch (error: any) {
          console.error('获取用户信息失败:', error)
          
          // 如果token无效，清除认证状态
          if (error.response?.status === 401) {
            logout()
          }
        }
      }
      
      fetchUserInfo()
    }
  }, [token, isAuthenticated, setUser, logout])

  // 添加全局错误处理，处理401错误
  useEffect(() => {
    const handleUnauthorized = () => {
      logout()
      // 可以在这里添加重定向到登录页的逻辑
      // window.location.href = '/login'
    }

    // 监听API请求的401错误
    const originalFetch = window.fetch
    window.fetch = async (input, init) => {
      try {
        const response = await originalFetch(input, init)
        
        // 检查响应状态
        if (response.status === 401) {
          handleUnauthorized()
        }
        
        return response
      } catch (error) {
        console.error('API请求错误:', error)
        throw error
      }
    }

    // 清理函数
    return () => {
      window.fetch = originalFetch
    }
  }, [logout])

  return <>{children}</>
}