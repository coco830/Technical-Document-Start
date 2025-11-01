'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useAuth } from '@/hooks/use-auth'

export default function ForgotPasswordPage() {
  const router = useRouter()
  const { resetPassword, isLoading } = useAuth()
  const [email, setEmail] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSuccess, setIsSuccess] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target
    setEmail(value)
    
    // 清除错误信息
    if (errors.email) {
      setErrors(prev => ({
        ...prev,
        email: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!email.trim()) {
      newErrors.email = '邮箱不能为空'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = '请输入有效的邮箱地址'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }
    
    const result = await resetPassword(email)
    
    if (result.success) {
      setIsSuccess(true)
    }
  }

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full">
          <Card>
            <CardHeader>
              <CardTitle className="text-center text-green-600">邮件已发送</CardTitle>
              <CardDescription className="text-center">
                我们已向您的邮箱发送了重置密码链接，请查收邮件并按照提示操作。
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <p className="text-sm text-gray-600">
                没有收到邮件？请检查垃圾邮件文件夹，或稍后再试。
              </p>
              <div className="space-y-2">
                <Link href="/login">
                  <Button variant="outline" className="w-full">
                    返回登录
                  </Button>
                </Link>
                <Button 
                  variant="link" 
                  onClick={() => setIsSuccess(false)}
                  className="w-full"
                >
                  重新发送
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            忘记密码
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            记起密码了？{' '}
            <Link href="/login" className="font-medium text-primary hover:text-primary/90">
              返回登录
            </Link>
          </p>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>重置密码</CardTitle>
            <CardDescription>
              请输入您的邮箱地址，我们将向您发送重置密码的链接
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  邮箱地址
                </label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={email}
                  onChange={handleChange}
                  className={`mt-1 ${errors.email ? 'border-red-500' : ''}`}
                  placeholder="请输入您的邮箱地址"
                />
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                )}
              </div>

              <div className="bg-blue-50 p-4 rounded-md">
                <h4 className="text-sm font-medium text-blue-900 mb-2">重置流程说明：</h4>
                <ol className="text-xs text-blue-800 space-y-1 list-decimal list-inside">
                  <li>输入您的邮箱地址</li>
                  <li>我们向该邮箱发送重置链接</li>
                  <li>点击邮件中的链接重置密码</li>
                  <li>设置新密码并登录</li>
                </ol>
              </div>

              <Button
                type="submit"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? '发送中...' : '发送重置链接'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}