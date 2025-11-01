'use client'

import React, { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CompanyWithDetails, CompanyVerification, CompanyContact, CompanyDocument } from '@/types'
import { companyApi } from '@/lib/api'
import { CompanyStatus, CompanyVerificationDetails } from '@/components/companies/company-status'
import { CompanyVerification as CompanyVerificationComponent } from '@/components/companies/company-verification'
import { formatDistanceToNow } from '@/utils'

export default function CompanyDetailPage() {
  const params = useParams()
  const router = useRouter()
  const companyId = parseInt(params.id as string)

  const [company, setCompany] = useState<CompanyWithDetails | null>(null)
  const [verifications, setVerifications] = useState<CompanyVerification[]>([])
  const [contacts, setContacts] = useState<CompanyContact[]>([])
  const [documents, setDocuments] = useState<CompanyDocument[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'details' | 'verifications' | 'contacts' | 'documents'>('details')

  // 获取企业详情
  const fetchCompanyDetails = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await companyApi.getCompany(companyId)
      if (response.success && response.data) {
        setCompany(response.data)
      } else {
        setError(response.message || '获取企业详情失败')
      }
    } catch (err) {
      setError('获取企业详情失败')
      console.error('获取企业详情失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 获取企业验证记录
  const fetchVerifications = async () => {
    try {
      const response = await companyApi.getCompanyVerifications(companyId)
      if (response.success && response.data) {
        setVerifications(response.data.verifications)
      }
    } catch (err) {
      console.error('获取企业验证记录失败:', err)
    }
  }

  // 获取企业联系人
  const fetchContacts = async () => {
    try {
      const response = await companyApi.getCompanyContacts(companyId)
      if (response.success && response.data) {
        setContacts(response.data.contacts)
      }
    } catch (err) {
      console.error('获取企业联系人失败:', err)
    }
  }

  // 获取企业文档
  const fetchDocuments = async () => {
    try {
      const response = await companyApi.getCompanyDocuments(companyId)
      if (response.success && response.data) {
        setDocuments(response.data.documents)
      }
    } catch (err) {
      console.error('获取企业文档失败:', err)
    }
  }

  // 初始加载
  useEffect(() => {
    if (companyId) {
      fetchCompanyDetails()
      fetchVerifications()
      fetchContacts()
      fetchDocuments()
    }
  }, [companyId])

  // 处理编辑企业
  const handleEditCompany = () => {
    router.push(`/companies/${companyId}/edit`)
  }

  // 处理删除企业
  const handleDeleteCompany = async () => {
    if (window.confirm('确定要删除这个企业吗？此操作不可撤销。')) {
      try {
        const response = await companyApi.deleteCompany(companyId)
        if (response.success) {
          router.push('/companies')
        } else {
          alert(response.message || '删除企业失败')
        }
      } catch (err) {
        alert('删除企业失败')
        console.error('删除企业失败:', err)
      }
    }
  }

  // 处理创建验证记录
  const handleCreateVerification = async (data: any) => {
    try {
      const response = await companyApi.createCompanyVerification(companyId, data)
      if (response.success) {
        fetchVerifications()
      } else {
        alert(response.message || '创建验证记录失败')
      }
    } catch (err) {
      alert('创建验证记录失败')
      console.error('创建验证记录失败:', err)
    }
  }

  // 处理更新验证记录
  const handleUpdateVerification = async (verificationId: number, data: any) => {
    try {
      const response = await companyApi.updateCompanyVerification(companyId, verificationId, data)
      if (response.success) {
        fetchVerifications()
      } else {
        alert(response.message || '更新验证记录失败')
      }
    } catch (err) {
      alert('更新验证记录失败')
      console.error('更新验证记录失败:', err)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="text-lg text-gray-600">加载中...</div>
        </div>
      </div>
    )
  }

  if (error || !company) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error || '企业不存在'}
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* 页面标题和操作按钮 */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{company.name}</h1>
          <p className="text-gray-600 mt-1">企业详细信息和管理</p>
        </div>
        <div className="flex space-x-2 mt-4 md:mt-0">
          <Button variant="outline" onClick={handleEditCompany}>
            编辑企业
          </Button>
          <Button variant="outline" onClick={handleDeleteCompany} className="text-red-600 hover:text-red-700 hover:bg-red-50">
            删除企业
          </Button>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'details', label: '基本信息' },
            { id: 'verifications', label: '验证记录' },
            { id: 'contacts', label: '联系人' },
            { id: 'documents', label: '文档' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* 标签页内容 */}
      {activeTab === 'details' && (
        <div className="space-y-6">
          {/* 基本信息 */}
          <Card>
            <CardHeader>
              <CardTitle>基本信息</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">企业名称</h3>
                  <p className="text-gray-900">{company.name}</p>
                </div>
                {company.unified_social_credit_code && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">统一社会信用代码</h3>
                    <p className="text-gray-900">{company.unified_social_credit_code}</p>
                  </div>
                )}
                {company.legal_representative && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">法定代表人</h3>
                    <p className="text-gray-900">{company.legal_representative}</p>
                  </div>
                )}
                {company.contact_phone && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">联系电话</h3>
                    <p className="text-gray-900">{company.contact_phone}</p>
                  </div>
                )}
                {company.contact_email && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">联系邮箱</h3>
                    <p className="text-gray-900">{company.contact_email}</p>
                  </div>
                )}
                {company.industry && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-500 mb-2">所属行业</h3>
                    <p className="text-gray-900">{company.industry}</p>
                  </div>
                )}
                {company.address && (
                  <div className="md:col-span-2">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">企业地址</h3>
                    <p className="text-gray-900">{company.address}</p>
                  </div>
                )}
                {company.business_scope && (
                  <div className="md:col-span-2">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">经营范围</h3>
                    <p className="text-gray-900">{company.business_scope}</p>
                  </div>
                )}
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">创建时间</h3>
                  <p className="text-gray-900">
                    {new Date(company.created_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-500 mb-2">更新时间</h3>
                  <p className="text-gray-900">
                    {new Date(company.updated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 统计信息 */}
          <Card>
            <CardHeader>
              <CardTitle>统计信息</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {company.projects_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">总项目数</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {company.active_projects_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">活跃项目</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">
                    {company.completed_projects_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">已完成项目</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {company.documents_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">文档数量</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {activeTab === 'verifications' && (
        <CompanyVerificationComponent
          companyId={companyId}
          verifications={verifications}
          onCreateVerification={handleCreateVerification}
          onUpdateVerification={handleUpdateVerification}
        />
      )}

      {activeTab === 'contacts' && (
        <Card>
          <CardHeader>
            <CardTitle>企业联系人</CardTitle>
            <CardDescription>管理企业联系人信息</CardDescription>
          </CardHeader>
          <CardContent>
            {contacts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>暂无联系人信息</p>
              </div>
            ) : (
              <div className="space-y-4">
                {contacts.map((contact) => (
                  <div key={contact.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{contact.name}</h4>
                      <div className="flex space-x-2">
                        {contact.is_primary && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            主要联系人
                          </span>
                        )}
                        {contact.is_active && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            活跃
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                      {contact.position && (
                        <div>
                          <span className="font-medium text-gray-600">职位:</span>
                          <span className="ml-2">{contact.position}</span>
                        </div>
                      )}
                      {contact.phone && (
                        <div>
                          <span className="font-medium text-gray-600">电话:</span>
                          <span className="ml-2">{contact.phone}</span>
                        </div>
                      )}
                      {contact.email && (
                        <div>
                          <span className="font-medium text-gray-600">邮箱:</span>
                          <span className="ml-2">{contact.email}</span>
                        </div>
                      )}
                      {contact.department && (
                        <div>
                          <span className="font-medium text-gray-600">部门:</span>
                          <span className="ml-2">{contact.department}</span>
                        </div>
                      )}
                    </div>
                    {contact.notes && (
                      <div className="mt-2 text-sm">
                        <span className="font-medium text-gray-600">备注:</span>
                        <span className="ml-2">{contact.notes}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'documents' && (
        <Card>
          <CardHeader>
            <CardTitle>企业文档</CardTitle>
            <CardDescription>管理企业相关文档</CardDescription>
          </CardHeader>
          <CardContent>
            {documents.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>暂无文档信息</p>
              </div>
            ) : (
              <div className="space-y-4">
                {documents.map((document) => (
                  <div key={document.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{document.document_name}</h4>
                      <div className="flex space-x-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {document.document_type}
                        </span>
                        {document.is_verified && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            已验证
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">
                      <div>文件大小: {(document.file_size / 1024 / 1024).toFixed(2)} MB</div>
                      <div>上传时间: {document.created_at ? new Date(document.created_at).toLocaleString() : '未知'}</div>
                      {document.verified_at && (
                        <div>验证时间: {new Date(document.verified_at).toLocaleString()}</div>
                      )}
                    </div>
                    {document.notes && (
                      <div className="mt-2 text-sm">
                        <span className="font-medium text-gray-600">备注:</span>
                        <span className="ml-2">{document.notes}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}