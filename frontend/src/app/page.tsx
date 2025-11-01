'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth-simple'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

export default function Home() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    // 如果用户已登录，重定向到仪表盘
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner h-8 w-8"></div>
      </div>
    )
  }

  // 如果已登录，显示欢迎页面
  if (isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>欢迎回来！</CardTitle>
            <CardDescription>
              您已成功登录悦恩人机共写平台
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/dashboard">进入仪表盘</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  // 未登录用户看到的功能介绍页面
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">悦恩人机共写平台</h1>
            <div className="space-x-4">
              <Button asChild variant="outline">
                <Link href="/login">登录</Link>
              </Button>
              <Button asChild>
                <Link href="/register">注册</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
            AI驱动的环保文案生成平台
          </h2>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            让AI生成80%模板内容，剩余20%由人机共创、人工复核
          </p>
        </div>

        {/* Features */}
        <div className="mt-20">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader>
                <CardTitle>应急预案</CardTitle>
                <CardDescription>
                  AI自动生成企业应急预案，符合法规要求，节省80%撰写时间
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>环评报告</CardTitle>
                <CardDescription>
                  智能生成环境影响评价报告，专业模板确保合规性
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>人机协作</CardTitle>
                <CardDescription>
                  AI处理80%模板内容，人工专注20%关键内容
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>智能编辑</CardTitle>
                <CardDescription>
                  富文本编辑器，AI辅助改写、扩写、润色
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold text-gray-900">
            开始使用悦恩人机共写平台
          </h3>
          <p className="mt-4 text-lg text-gray-600">
            提高环保文书撰写效率，让AI为您的业务助力
          </p>
          <div className="mt-8 space-x-4">
            <Button asChild size="lg">
              <Link href="/register">立即注册</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/login">立即登录</Link>
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
