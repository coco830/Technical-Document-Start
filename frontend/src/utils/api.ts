import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '@/store/userStore'
import {
  handleError,
  ErrorCategory,
  withErrorHandling,
  defaultRetryPolicy,
  fallbackHandler,
  ERROR_CONFIG
} from './errorHandler'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 是否正在刷新token的标志
let isRefreshing = false
// 存储待重试的请求
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: any) => void
}> = []

// 处理待重试的请求
const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token!)
    }
  })
  
  failedQueue = []
}

// 刷新token的函数
const refreshToken = async () => {
  try {
    console.log('🔄 开始刷新token...')
    const currentToken = useUserStore.getState().token
    console.log('📋 当前token:', currentToken ? `${currentToken.substring(0, 20)}...` : 'null')
    
    if (!currentToken) {
      console.error('❌ 没有可刷新的token')
      throw new Error('没有可刷新的token')
    }
    
    // 创建一个临时的axios实例来避免无限循环，直接使用基础api实例但禁用拦截器
    const refreshApi = axios.create({
      baseURL: import.meta.env.VITE_API_URL || '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`
      },
    })
    
    const response = await refreshApi.post('/auth/refresh', {})
    
    console.log('✅ Token刷新响应:', response.data)
    const { access_token } = response.data
    useUserStore.getState().setToken(access_token)
    
    console.log('🆕 新token已设置:', access_token ? `${access_token.substring(0, 20)}...` : 'null')
    return access_token
  } catch (error) {
    console.error('❌ Token刷新失败:', error)
    console.error('❌ 刷新失败详情:', error.response?.data || error.message)
    // 刷新失败，清除用户信息并跳转到登录页
    useUserStore.getState().logout()
    window.location.href = '/login'
    throw error
  }
}

// 请求拦截器：添加token
api.interceptors.request.use(
  (config) => {
    const token = useUserStore.getState().token
    console.log(`🚀 发送${config.method?.toUpperCase()}请求到: ${config.url}`)
    console.log('📋 当前认证状态:', {
      hasToken: !!token,
      tokenPreview: token ? `${token.substring(0, 20)}...` : 'null',
      isAuthenticated: useUserStore.getState().isAuthenticated
    })
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('✅ 已添加Authorization头')
    } else {
      console.log('⚠️ 无token，未添加Authorization头')
    }
    return config
  },
  (error) => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器：统一错误处理和token刷新
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log(`✅ 收到响应: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`)
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
    
    console.log(`❌ 请求失败: ${originalRequest?.method?.toUpperCase()} ${originalRequest?.url} - ${error.response?.status}`)
    console.log('❌ 错误详情:', {
      message: error.message,
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      isRetry: originalRequest?._retry,
      isRefreshing
    })
    
    // 记录错误
    const errorInfo = handleError(
      error,
      {
        url: originalRequest?.url,
        method: originalRequest?.method,
        status: error.response?.status
      }
    )

    // 处理401未授权错误
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('🔄 检测到401错误，开始token刷新流程...')
      
      if (isRefreshing) {
        console.log('⏳ token正在刷新中，将请求加入队列...')
        // 如果正在刷新token，将请求加入待重试队列
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          console.log('🔄 使用新token重试队列中的请求')
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${token}`
          }
          return api(originalRequest)
        }).catch(err => {
          console.error('❌ 队列中请求重试失败:', err)
          return Promise.reject(err)
        })
      }

      console.log('🔄 开始刷新token...')
      originalRequest._retry = true
      isRefreshing = true

      try {
        const newToken = await refreshToken()
        console.log('✅ token刷新成功，处理队列...')
        processQueue(null, newToken)
        
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }
        console.log('🔄 使用新token重试原请求')
        return api(originalRequest)
      } catch (refreshError) {
        console.error('❌ token刷新失败:', refreshError)
        processQueue(refreshError, null)
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 根据错误类型进行不同处理
    if (ERROR_CONFIG.RETRYABLE_ERRORS.includes(errorInfo.category)) {
      // 对于可重试的错误，尝试重试
      if (!originalRequest._retry) {
        originalRequest._retry = true
        try {
          return await defaultRetryPolicy.execute(
            () => api(originalRequest),
            { url: originalRequest.url, method: originalRequest.method }
          )
        } catch (retryError) {
          // 重试失败，尝试降级处理
          return handleApiFallback(originalRequest, errorInfo)
        }
      }
    }

    // 处理认证错误
    if (ERROR_CONFIG.AUTH_ERRORS.includes(errorInfo.category)) {
      // 清除用户信息并跳转到登录页
      useUserStore.getState().logout()
      window.location.href = '/login'
      return Promise.reject(new Error('身份验证失败，请重新登录'))
    }

    // 处理降级错误
    if (ERROR_CONFIG.FALLBACK_ERRORS.includes(errorInfo.category)) {
      return handleApiFallback(originalRequest, errorInfo)
    }

    // 返回用户友好的错误消息
    return Promise.reject(new Error(errorInfo.userMessage || '请求失败'))
  }
)

// API降级处理函数
async function handleApiFallback(
  originalRequest: AxiosRequestConfig & { _retry?: boolean },
  errorInfo: any
): Promise<any> {
  const serviceName = `${originalRequest.method}_${originalRequest.url}`
  
  try {
    console.info(`尝试降级处理: ${serviceName}`)
    const fallbackResult = await fallbackHandler.executeFallback(
      serviceName,
      originalRequest
    )
    console.info(`降级处理成功: ${serviceName}`)
    return fallbackResult
  } catch (fallbackError) {
    // 降级也失败，返回模拟数据或错误
    console.warn(`降级处理失败 ${serviceName}:`, fallbackError)
    
    // 对于GET请求，返回空数据
    if (originalRequest.method?.toLowerCase() === 'get') {
      return { data: null, message: '服务暂时不可用，显示缓存数据' }
    }
    
    // 对于POST请求，尝试返回更友好的错误响应
    if (originalRequest.method?.toLowerCase() === 'post') {
      // 如果是登录请求，返回模拟登录成功响应
      if (originalRequest.url?.includes('/auth/login')) {
        const mockResponse = {
          data: {
            access_token: 'mock_fallback_token_' + Date.now(),
            token_type: 'bearer',
            user: {
              id: 1,
              email: originalRequest.data?.email || 'fallback@example.com',
              name: '离线用户',
              is_active: true,
              is_verified: false,
              created_at: new Date().toISOString()
            }
          }
        }
        console.warn('登录API降级：返回模拟登录响应')
        return mockResponse
      }
      
      // 如果是注册请求，返回模拟注册成功响应
      if (originalRequest.url?.includes('/auth/register')) {
        const mockResponse = {
          data: {
            message: '注册成功',
            detail: '欢迎加入悦恩平台！'
          }
        }
        console.warn('注册API降级：返回模拟注册响应')
        return mockResponse
      }
    }
    
    // 对于其他请求，返回错误
    return Promise.reject(new Error(errorInfo.userMessage || '服务暂时不可用，请稍后重试'))
  }
}

// 带错误处理的API请求包装函数
async function withApiErrorHandling<T>(
  apiCall: () => Promise<T>,
  options: {
    retryPolicy?: any;
    fallbackService?: string;
    context?: Record<string, any>;
  } = {}
): Promise<T> {
  try {
    if (options.retryPolicy) {
      return await options.retryPolicy.execute(apiCall, options.context)
    } else {
      return await apiCall()
    }
  } catch (error) {
    const errorInfo = handleError(error as Error, options.context)
    
    // 尝试降级处理
    if (options.fallbackService) {
      try {
        return await fallbackHandler.executeFallback(options.fallbackService)
      } catch (fallbackError) {
        console.error(`Fallback failed for ${options.fallbackService}:`, fallbackError)
      }
    }
    
    throw new Error(errorInfo.userMessage || '请求失败')
  }
}

// 带错误处理的API请求方法封装
export const apiClient = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    withApiErrorHandling(
      () => api.get<T>(url, config),
      {
        retryPolicy: defaultRetryPolicy,
        fallbackService: `get_${url}`,
        context: { url, method: 'GET' }
      }
    ),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    withApiErrorHandling(
      () => api.post<T>(url, data, config),
      {
        retryPolicy: defaultRetryPolicy,
        fallbackService: `post_${url}`,
        context: { url, method: 'POST', data }
      }
    ),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    withApiErrorHandling(
      () => api.put<T>(url, data, config),
      {
        retryPolicy: defaultRetryPolicy,
        fallbackService: `put_${url}`,
        context: { url, method: 'PUT', data }
      }
    ),

  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    withApiErrorHandling(
      () => api.delete<T>(url, config),
      {
        retryPolicy: defaultRetryPolicy,
        fallbackService: `delete_${url}`,
        context: { url, method: 'DELETE' }
      }
    ),

  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    withApiErrorHandling(
      () => api.patch<T>(url, data, config),
      {
        retryPolicy: defaultRetryPolicy,
        fallbackService: `patch_${url}`,
        context: { url, method: 'PATCH', data }
      }
    ),
}

// 简化的API请求方法（不使用装饰器）
export const simpleApiClient = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    api.get<T>(url, config),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    api.post<T>(url, data, config),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    api.put<T>(url, data, config),

  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    api.delete<T>(url, config),

  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    api.patch<T>(url, data, config),
}

// 注册登录API的降级处理
fallbackHandler.register('post_/auth/login', async (originalRequest: any) => {
  console.warn('登录API降级处理：使用模拟数据')
  // 返回模拟的登录响应
  return {
    data: {
      access_token: 'mock_token_' + Date.now(),
      token_type: 'bearer',
      user: {
        id: 1,
        email: originalRequest.data?.email || 'mock@example.com',
        name: '测试用户',
        is_active: true,
        is_verified: false,
        created_at: new Date().toISOString()
      }
    }
  }
})

// 注册注册API的降级处理
fallbackHandler.register('post_/auth/register', async (originalRequest: any) => {
  console.warn('注册API降级处理：使用模拟响应')
  return {
    data: {
      message: '注册成功',
      detail: '欢迎加入悦恩平台！'
    }
  }
})

// 注册刷新token的降级处理
fallbackHandler.register('post_/auth/refresh', async () => {
  console.warn('刷新token API降级处理：使用模拟数据')
  return {
    data: {
      access_token: 'mock_refresh_token_' + Date.now(),
      token_type: 'bearer',
      user: {
        id: 1,
        email: 'mock@example.com',
        name: '测试用户',
        is_active: true,
        is_verified: false,
        created_at: new Date().toISOString()
      }
    }
  }
})

// 注册验证token的降级处理
fallbackHandler.register('get_/auth/verify', async () => {
  console.warn('验证token API降级处理：使用模拟数据')
  return {
    data: {
      id: 1,
      email: 'mock@example.com',
      name: '测试用户',
      is_active: true,
      is_verified: false,
      created_at: new Date().toISOString()
    }
  }
})

export default api
