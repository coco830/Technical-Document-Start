import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'

export interface User {
  id: number
  username: string
  email: string
  full_name: string
  is_active: boolean
}

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // 检查本地存储中的用户信息
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const userInfo = localStorage.getItem('user_info')

    if (token && userInfo) {
      try {
        const userData = JSON.parse(userInfo)
        setUser(userData)
        setIsAuthenticated(true)
      } catch (error) {
        console.error('Failed to parse user info:', error)
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
      }
    }
  }, [])

  const loginUser = useCallback(async (username: string, password: string) => {
    setIsLoading(true)
    try {
      // 模拟用户数据库
      const mockUsers: Record<string, { password: string; user: User }> = {
        'admin': {
          password: 'admin123',
          user: {
            id: 1,
            username: 'admin',
            email: 'admin@example.com',
            full_name: '管理员',
            is_active: true
          }
        },
        'test': {
          password: 'test123',
          user: {
            id: 2,
            username: 'test',
            email: 'test@example.com',
            full_name: '测试用户',
            is_active: true
          }
        },
        'demo': {
          password: 'demo123',
          user: {
            id: 3,
            username: 'demo',
            email: 'demo@example.com',
            full_name: '演示用户',
            is_active: true
          }
        }
      }

      // 模拟延迟
      await new Promise(resolve => setTimeout(resolve, 800))

      const mockUser = mockUsers[username]
      if (!mockUser || mockUser.password !== password) {
        throw new Error('用户名或密码错误')
      }

      // 保存用户信息
      localStorage.setItem('access_token', `mock_token_${Date.now()}`)
      localStorage.setItem('user_info', JSON.stringify(mockUser.user))

      setUser(mockUser.user)
      setIsAuthenticated(true)

      return mockUser.user
    } catch (error: any) {
      throw new Error(error.message || '登录失败')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const registerUser = useCallback(async (username: string, password: string, email: string, fullName: string) => {
    setIsLoading(true)
    try {
      // 模拟延迟
      await new Promise(resolve => setTimeout(resolve, 800))

      // 检查用户名是否已存在
      if (username === 'admin' || username === 'test' || username === 'demo') {
        throw new Error('用户名已存在')
      }

      // 创建新用户
      const newUser: User = {
        id: Date.now(),
        username,
        email,
        full_name: fullName,
        is_active: true
      }

      // 保存用户信息
      localStorage.setItem('access_token', `mock_token_${Date.now()}`)
      localStorage.setItem('user_info', JSON.stringify(newUser))

      setUser(newUser)
      setIsAuthenticated(true)

      return newUser
    } catch (error: any) {
      throw new Error(error.message || '注册失败')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logoutUser = useCallback(async () => {
    // 清除本地存储
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')

    // 重置状态
    setUser(null)
    setIsAuthenticated(false)

    // 跳转到首页
    router.push('/')
  }, [router])

  return {
    user,
    isAuthenticated,
    isLoading,
    loginUser,
    registerUser,
    logoutUser
  }
}
