import React, { useState } from 'react'
import { apiClient } from '@/utils/api'
import { useUserStore } from '@/store/userStore'

export default function AuthTest() {
  const [logs, setLogs] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const { token, isAuthenticated, user, setToken, logout } = useUserStore()

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, `[${timestamp}] ${message}`])
  }

  const testLogin = async () => {
    setLoading(true)
    try {
      addLog('🔄 开始测试登录...')
      
      // 模拟登录数据
      const loginData = {
        email: 'test@example.com',
        password: 'test123456'
      }
      
      // 直接使用axios而不是apiClient来避免拦截器干扰
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(loginData)
      })
      
      if (response.ok) {
        const data = await response.json()
        addLog(`✅ 登录成功: ${data.access_token.substring(0, 30)}...`)
        setToken(data.access_token)
      } else {
        const error = await response.text()
        addLog(`❌ 登录失败: ${error}`)
      }
    } catch (error) {
      addLog(`❌ 登录错误: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testVerifyToken = async () => {
    if (!token) {
      addLog('⚠️ 没有token，请先登录')
      return
    }

    setLoading(true)
    try {
      addLog('🔄 开始验证token...')
      const response = await apiClient.get('/auth/verify')
      addLog(`✅ Token验证成功: ${JSON.stringify(response.data)}`)
    } catch (error) {
      addLog(`❌ Token验证失败: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testRefreshToken = async () => {
    if (!token) {
      addLog('⚠️ 没有token，请先登录')
      return
    }

    setLoading(true)
    try {
      addLog('🔄 开始刷新token...')
      const response = await apiClient.post('/auth/refresh', {})
      addLog(`✅ Token刷新成功: ${response.data.access_token.substring(0, 30)}...`)
    } catch (error) {
      addLog(`❌ Token刷新失败: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testEnterpriseAPI = async () => {
    if (!token) {
      addLog('⚠️ 没有token，请先登录')
      return
    }

    setLoading(true)
    try {
      addLog('🔄 开始测试企业信息API...')
      const enterpriseData = {
        project_id: 1,
        enterprise_identity: {
          enterprise_name: "测试企业",
          industry: "测试行业"
        }
      }
      
      const response = await apiClient.post('/enterprise/info', enterpriseData)
      addLog(`✅ 企业信息API成功: ${JSON.stringify(response.data)}`)
    } catch (error) {
      addLog(`❌ 企业信息API失败: ${error.message}`)
      addLog(`❌ 错误详情: ${JSON.stringify(error.response?.data || {})}`)
    } finally {
      setLoading(false)
    }
  }

  const clearLogs = () => {
    setLogs([])
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">认证调试测试</h1>
      
      {/* 当前状态 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">当前认证状态</h2>
        <div className="space-y-2">
          <p><strong>已认证:</strong> {isAuthenticated ? '✅ 是' : '❌ 否'}</p>
          <p><strong>有Token:</strong> {token ? '✅ 是' : '❌ 否'}</p>
          <p><strong>Token预览:</strong> {token ? `${token.substring(0, 30)}...` : '无'}</p>
          <p><strong>用户信息:</strong> {user ? JSON.stringify(user) : '无'}</p>
        </div>
      </div>

      {/* 测试按钮 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">认证测试</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={testLogin}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            测试登录
          </button>
          <button
            onClick={testVerifyToken}
            disabled={loading || !token}
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            验证Token
          </button>
          <button
            onClick={testRefreshToken}
            disabled={loading || !token}
            className="px-4 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600 disabled:opacity-50"
          >
            刷新Token
          </button>
          <button
            onClick={testEnterpriseAPI}
            disabled={loading || !token}
            className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600 disabled:opacity-50"
          >
            测试企业API
          </button>
        </div>
        <div className="mt-4 flex gap-4">
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            登出
          </button>
          <button
            onClick={clearLogs}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            清除日志
          </button>
        </div>
      </div>

      {/* 日志输出 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">调试日志</h2>
        <div className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-400">暂无日志...</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">{log}</div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}