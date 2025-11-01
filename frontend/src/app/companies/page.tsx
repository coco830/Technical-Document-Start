'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { mockCompanies } from '@/utils/mock-data'
import { useAuth } from '@/hooks/use-auth-simple'

export default function SimpleCompaniesPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [companies, setCompanies] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login')
      return
    }
    setTimeout(() => {
      setCompanies(mockCompanies)
      setLoading(false)
    }, 500)
  }, [isAuthenticated, router])

  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    company.industry.toLowerCase().includes(searchTerm.toLowerCase())
  )

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">正在验证身份...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">悦恩人机共写平台</h1>
            <Button onClick={() => router.push('/dashboard')} variant="outline" size="sm">
              返回仪表盘
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900">企业管理</h2>
            <p className="mt-2 text-sm text-gray-600">
              管理您的企业信息和设置
            </p>
          </div>
          <Button onClick={() => alert('这是演示版本，创建功能暂时不可用')}>
            添加企业
          </Button>
        </div>

        <div className="mb-6">
          <Input
            type="text"
            placeholder="搜索企业..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-lg text-gray-600">加载中...</div>
          </div>
        ) : filteredCompanies.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-lg text-gray-600 mb-4">
              {searchTerm ? '没有找到匹配的企业' : '您还没有任何企业'}
            </div>
            {!searchTerm && (
              <Button onClick={() => alert('这是演示版本，创建功能暂时不可用')}>
                添加第一个企业
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCompanies.map((company) => (
              <Card key={company.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{company.name}</CardTitle>
                      <CardDescription className="mt-2">
                        {company.industry}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Badge variant="outline">{company.industry}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">注册号:</span> {company.registration_number}
                    </div>
                    <div>
                      <span className="font-medium">联系人:</span> {company.contact_person}
                    </div>
                    <div>
                      <span className="font-medium">电话:</span> {company.contact_phone}
                    </div>
                    <div>
                      <span className="font-medium">地址:</span> {company.address}
                    </div>
                    <div className="flex justify-between pt-2 border-t">
                      <span>项目: {company.projects_count}</span>
                      <span>文档: {company.documents_count}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => alert(`查看企业 ${company.id} (演示版本)`)}
                    >
                      查看
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => alert(`编辑企业 ${company.id} (演示版本)`)}
                    >
                      编辑
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
