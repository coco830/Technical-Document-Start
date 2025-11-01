'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function DemoInfo() {
  return (
    <Card className="mb-6 bg-blue-50 border-blue-200">
      <CardHeader>
        <CardTitle className="text-blue-900">💡 演示账户</CardTitle>
        <CardDescription className="text-blue-700">
          您可以使用以下账户进行登录演示
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 bg-white rounded border border-blue-200">
            <p className="font-medium text-gray-900">管理员</p>
            <p className="text-sm text-gray-600">用户名: admin</p>
            <p className="text-sm text-gray-600">密码: admin123</p>
          </div>
          <div className="p-3 bg-white rounded border border-blue-200">
            <p className="font-medium text-gray-900">测试用户</p>
            <p className="text-sm text-gray-600">用户名: test</p>
            <p className="text-sm text-gray-600">密码: test123</p>
          </div>
          <div className="p-3 bg-white rounded border border-blue-200">
            <p className="font-medium text-gray-900">演示用户</p>
            <p className="text-sm text-gray-600">用户名: demo</p>
            <p className="text-sm text-gray-600">密码: demo123</p>
          </div>
        </div>
        <p className="text-xs text-blue-600 mt-4">
          * 这是前端模拟登录功能，用于演示项目功能
        </p>
      </CardContent>
    </Card>
  )
}
