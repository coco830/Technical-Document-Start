'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/hooks/use-auth-simple'

export default function LoginPage() {
  const router = useRouter()
  const { loginUser, isLoading, isAuthenticated } = useAuth()

  // 认证成功后自动跳转到仪表盘
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, router])
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      await loginUser(formData.username, formData.password)
      // 不需要手动跳转，useAuth 状态变化会自动处理
    } catch (error: any) {
      alert(error.message || '登录失败')
    }
  }

  // 快速填充演示账户
  const fillDemoAccount = (username: string, password: string) => {
    setFormData({ username, password })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            登录到悦恩人机共写平台
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            还没有账号？{' '}
            <Link href="/register" className="font-medium text-primary hover:text-primary/90">
              立即注册
            </Link>
          </p>
        </div>

        {/* 演示账户信息 */}
        <Card className="mb-6 bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="text-blue-900 text-lg">💡 演示账户</CardTitle>
            <CardDescription className="text-blue-700">
              点击下方按钮快速填充演示账户
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="grid grid-cols-1 gap-2">
              <Button
                type="button"
                variant="outline"
                className="justify-start"
                onClick={() => fillDemoAccount('admin', 'admin123')}
              >
                管理员 (admin / admin123)
              </Button>
              <Button
                type="button"
                variant="outline"
                className="justify-start"
                onClick={() => fillDemoAccount('test', 'test123')}
              >
                测试用户 (test / test123)
              </Button>
              <Button
                type="button"
                variant="outline"
                className="justify-start"
                onClick={() => fillDemoAccount('demo', 'demo123')}
              >
                演示用户 (demo / demo123)
              </Button>
            </div>
            <p className="text-xs text-blue-600 mt-2">
              * 这是前端模拟登录功能，用于演示项目功能
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>登录</CardTitle>
            <CardDescription>
              请输入您的用户名和密码进行登录
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                  用户名
                </label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="mt-1"
                  placeholder="请输入用户名"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  密码
                </label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="mt-1"
                  placeholder="请输入密码"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                    记住我
                  </label>
                </div>

                <div className="text-sm">
                  <Link href="/forgot-password" className="font-medium text-primary hover:text-primary/90">
                    忘记密码？
                  </Link>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? '登录中...' : '登录'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}