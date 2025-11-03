import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '@/store/userStore'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加token
api.interceptors.request.use(
  (config) => {
    const token = useUserStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  (error: AxiosError) => {
    // 处理401未授权错误
    if (error.response?.status === 401) {
      useUserStore.getState().logout()
      window.location.href = '/login'
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    // 处理403禁止访问
    if (error.response?.status === 403) {
      return Promise.reject(new Error('没有权限访问此资源'))
    }

    // 处理404资源不存在
    if (error.response?.status === 404) {
      return Promise.reject(new Error('请求的资源不存在'))
    }

    // 处理500服务器错误
    if (error.response?.status === 500) {
      return Promise.reject(new Error('服务器内部错误，请稍后重试'))
    }

    // 处理网络错误
    if (!error.response) {
      return Promise.reject(new Error('网络连接失败，请检查您的网络'))
    }

    return Promise.reject(error)
  }
)

// API请求方法封装
export const apiClient = {
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

export default api
