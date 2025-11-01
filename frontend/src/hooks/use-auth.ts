import React, { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useUserStore } from '@/store'
import { api } from '@/lib/api'
import { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types'
import { STORAGE_KEYS, ERROR_MESSAGES } from '@/lib/constants'

export function useAuth() {
  const router = useRouter()
  const {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateUser,
    setLoading,
    updateLastActivity,
    checkSessionTimeout,
    refreshSession
  } = useUserStore()
  const [error, setError] = useState<string | null>(null)
  
  // 清除错误信息
  const clearError = useCallback(() => {
    setError(null)
  }, [])
  
  // 登录
  const loginUser = useCallback(async (credentials: LoginRequest) => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.post<AuthResponse>('/api/v1/auth/login', credentials)
      
      if (response.success && response.data) {
        const { access_token, refresh_token, user } = response.data
        
        // 更新用户状态和token
        login(user, access_token, refresh_token)
        
        return { success: true, user }
      } else {
        throw new Error(response.message || ERROR_MESSAGES.INVALID_CREDENTIALS)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.INVALID_CREDENTIALS
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [login, setLoading, clearError])
  
  // 注册
  const registerUser = useCallback(async (userData: RegisterRequest) => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.post<AuthResponse>('/api/v1/auth/register', userData)
      
      if (response.success && response.data) {
        const { access_token, refresh_token, user } = response.data
        
        // 更新用户状态和token
        login(user, access_token, refresh_token)
        
        return { success: true, user }
      } else {
        throw new Error(response.message || ERROR_MESSAGES.VALIDATION_ERROR)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.VALIDATION_ERROR
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [login, setLoading, clearError])
  
  // 登出
  const logoutUser = useCallback(async (force = false) => {
    try {
      // 调用后端登出接口
      await api.post('/api/v1/auth/logout')
    } catch (err) {
      // 即使后端登出失败，也要清除本地数据
      console.error('Logout error:', err)
    } finally {
      // 更新状态
      logout(force)
      
      // 跳转到登录页
      router.push('/login')
    }
  }, [logout, router])
  
  // 获取当前用户信息
  const fetchCurrentUser = useCallback(async () => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.get<User>('/api/v1/users/me')
      
      if (response.success && response.data) {
        updateUser(response.data)
        return response.data
      } else {
        throw new Error(response.message || ERROR_MESSAGES.UNAUTHORIZED)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.UNAUTHORIZED
      setError(errorMessage)
      
      // 如果获取用户信息失败，可能是token过期，执行登出
      if (err.message === ERROR_MESSAGES.UNAUTHORIZED || err.message === ERROR_MESSAGES.TOKEN_EXPIRED) {
        logoutUser()
      }
      
      return null
    } finally {
      setLoading(false)
    }
  }, [updateUser, setLoading, clearError, logoutUser])
  
  // 更新用户信息
  const updateProfile = useCallback(async (userData: Partial<User>) => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.put<User>('/api/v1/users/me', userData)
      
      if (response.success && response.data) {
        updateUser(response.data)
        return { success: true, user: response.data }
      } else {
        throw new Error(response.message || ERROR_MESSAGES.VALIDATION_ERROR)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.VALIDATION_ERROR
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [updateUser, setLoading, clearError])
  
  // 修改密码
  const changePassword = useCallback(async (passwordData: {
    current_password: string
    new_password: string
  }) => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.post('/api/v1/users/change-password', passwordData)
      
      if (response.success) {
        return { success: true }
      } else {
        throw new Error(response.message || ERROR_MESSAGES.VALIDATION_ERROR)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.VALIDATION_ERROR
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [setLoading, clearError])
  
  // 重置密码
  const resetPassword = useCallback(async (email: string) => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.post('/api/v1/auth/reset-password', { email })
      
      if (response.success) {
        return { success: true }
      } else {
        throw new Error(response.message || ERROR_MESSAGES.VALIDATION_ERROR)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.VALIDATION_ERROR
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [setLoading, clearError])
  
  // 确认重置密码
  const confirmResetPassword = useCallback(async (data: {
    token: string
    new_password: string
  }) => {
    try {
      setLoading(true)
      clearError()
      
      const response = await api.post('/api/v1/auth/confirm-reset-password', data)
      
      if (response.success) {
        return { success: true }
      } else {
        throw new Error(response.message || ERROR_MESSAGES.VALIDATION_ERROR)
      }
    } catch (err: any) {
      const errorMessage = err.message || ERROR_MESSAGES.VALIDATION_ERROR
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }, [setLoading, clearError])
  
  // 初始化时检查认证状态
  useEffect(() => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    
    if (token && !user) {
      fetchCurrentUser()
    } else if (!token && isAuthenticated) {
      // 如果没有token但状态显示已认证，清除状态
      logout()
    }
  }, [user, isAuthenticated, fetchCurrentUser, logout])
  
  // 会话超时检查
  useEffect(() => {
    if (!isAuthenticated) {
      return
    }
    
    // 设置定时器，每分钟检查一次会话状态
    const interval = setInterval(() => {
      const isValid = checkSessionTimeout()
      
      if (!isValid) {
        // 会话已超时，显示提示并登出
        if (typeof window !== 'undefined') {
          // 可以在这里添加更友好的提示，比如使用toast
          console.warn('会话已超时，请重新登录')
        }
      }
    }, 60 * 1000) // 每分钟检查一次
    
    return () => clearInterval(interval)
  }, [isAuthenticated, checkSessionTimeout])
  
  // 用户活动监听
  useEffect(() => {
    if (!isAuthenticated) {
      return
    }
    
    // 监听用户活动事件
    const handleUserActivity = () => {
      updateLastActivity()
    }
    
    // 添加事件监听器
    const events = [
      'mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'
    ]
    
    events.forEach(event => {
      window.addEventListener(event, handleUserActivity, true)
    })
    
    return () => {
      // 清除事件监听器
      events.forEach(event => {
        window.removeEventListener(event, handleUserActivity, true)
      })
    }
  }, [isAuthenticated, updateLastActivity])
  
  // 自动刷新token的API请求包装器
  const apiWithRefresh = useCallback(async (apiCall: () => Promise<any>) => {
    try {
      return await apiCall()
    } catch (err: any) {
      // 如果是401错误，尝试刷新token
      if (err.message === ERROR_MESSAGES.UNAUTHORIZED || err.message === ERROR_MESSAGES.TOKEN_EXPIRED) {
        const refreshed = await refreshSession()
        
        if (refreshed) {
          // 刷新成功，重试原始请求
          return await apiCall()
        }
      }
      
      throw err
    }
  }, [refreshSession])
  
  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    clearError,
    loginUser,
    registerUser,
    logoutUser,
    fetchCurrentUser,
    updateProfile,
    changePassword,
    resetPassword,
    confirmResetPassword,
    apiWithRefresh,
  }
}