'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ProjectStatusBadge } from '@/components/projects/project-status'
import { RouteGuard } from '@/components/auth/route-guard'
import { projectApi } from '@/lib/api'
import { useProjectStore, useUserStore } from '@/store'
import { ProjectWithDetails, ProjectFormWithDetails } from '@/types'

function ProjectDetailPageContent() {
  const params = useParams()
  const router = useRouter()
  const { user } = useUserStore()
  const { setCurrentProject } = useProjectStore()
  
  const [project, setProject] = useState<ProjectWithDetails | null>(null)
  const [forms, setForms] = useState<ProjectFormWithDetails[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const projectId = parseInt(params.id as string)

  useEffect(() => {
    if (isNaN(projectId)) {
      setError('无效的项目ID')
      setIsLoading(false)
      return
    }

    fetchProjectDetails()
    fetchProjectForms()
  }, [projectId])

  const fetchProjectDetails = async () => {
    try {
      const response = await projectApi.getProject(projectId)
      
      if (response.success && response.data) {
        setProject(response.data)
        setCurrentProject(response.data)
      } else {
        setError(response.error || '获取项目详情失败')
      }
    } catch (err) {
      setError('获取项目详情失败')
      console.error('Failed to fetch project details:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchProjectForms = async () => {
    try {
      const response = await projectApi.getProjectForms(projectId)
      
      if (response.success && response.data) {
        setForms(response.data.forms)
      }
    } catch (err) {
      console.error('Failed to fetch project forms:', err)
    }
  }

  const handleEditProject = () => {
    router.push(`/projects/${projectId}/edit`)
  }

  const handleDeleteProject = async () => {
    if (!confirm('确定要删除这个项目吗？此操作不可撤销。')) {
      return
    }

    setIsDeleting(true)
    
    try {
      const response = await projectApi.deleteProject(projectId)
      
      if (response.success) {
        router.push('/projects')
      } else {
        setError(response.error || '删除项目失败')
      }
    } catch (err) {
      setError('删除项目失败')
      console.error('Failed to delete project:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const handleViewForm = (formId: number) => {
    router.push(`/projects/${projectId}/forms/${formId}`)
  }

  const canEditProject = user && project && (
    user.role === 'admin' || Number(user.id) === project.user_id
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    )
  }

  if (error || !project) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-red-600 mb-4">
            {error || '项目不存在'}
          </div>
          <Button onClick={() => router.push('/projects')}>
            返回项目列表
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {project.name}
              </h1>
              <div className="mt-2 flex items-center space-x-4">
                <ProjectStatusBadge status={project.status} />
                <span className="text-sm text-gray-600">
                  创建于 {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
            
            {canEditProject && (
              <div className="flex space-x-4">
                <Button
                  variant="outline"
                  onClick={handleEditProject}
                >
                  编辑项目
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteProject}
                  disabled={isDeleting}
                >
                  {isDeleting ? '删除中...' : '删除项目'}
                </Button>
              </div>
            )}
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              {/* 项目基本信息 */}
              <Card>
                <CardHeader>
                  <CardTitle>项目信息</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-700">描述</h3>
                      <p className="mt-1 text-gray-600">
                        {project.description || '暂无描述'}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-700">类型</h3>
                      <p className="mt-1 text-gray-600">
                        {project.type === 'emergency_plan' ? '应急预案' : '环境评估'}
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-sm font-medium text-gray-700">创建者</h3>
                      <p className="mt-1 text-gray-600">
                        {project.user_name || '未知'}
                      </p>
                    </div>
                    
                    {project.company_name && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700">所属企业</h3>
                        <p className="mt-1 text-gray-600">
                          {project.company_name}
                        </p>
                      </div>
                    )}
                    
                    {project.progress !== undefined && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700">进度</h3>
                        <div className="mt-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full" 
                              style={{ width: `${project.progress}%` }}
                            ></div>
                          </div>
                          <div className="mt-1 text-sm text-gray-600">
                            {project.progress}% 完成
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* 项目表单 */}
              <Card>
                <CardHeader>
                  <CardTitle>项目表单</CardTitle>
                  <CardDescription>
                    此项目包含的表单列表
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {forms.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500 mb-4">
                        此项目还没有任何表单
                      </p>
                      {canEditProject && (
                        <Button onClick={() => router.push(`/projects/${projectId}/forms/new`)}>
                          创建表单
                        </Button>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {forms.map((form) => (
                        <div
                          key={form.id}
                          className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                          onClick={() => handleViewForm(form.id)}
                        >
                          <div>
                            <h4 className="font-medium">{form.form_type}</h4>
                            <p className="text-sm text-gray-600">
                              {form.fields_count || 0} 个字段
                            </p>
                          </div>
                          <div className="text-sm text-gray-500">
                            {new Date(form.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      ))}
                      
                      {canEditProject && (
                        <div className="mt-4">
                          <Button 
                            variant="outline" 
                            onClick={() => router.push(`/projects/${projectId}/forms/new`)}
                          >
                            添加新表单
                          </Button>
                        </div>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="space-y-8">
              {/* 项目统计 */}
              <Card>
                <CardHeader>
                  <CardTitle>项目统计</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">文档数量</span>
                      <span className="font-medium">
                        {project.documents_count || 0}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">表单数量</span>
                      <span className="font-medium">
                        {project.forms_count || 0}
                      </span>
                    </div>
                    
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-500">最后更新</span>
                      <span className="font-medium">
                        {new Date(project.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    
                    {project.completed_at && (
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-500">完成时间</span>
                        <span className="font-medium">
                          {new Date(project.completed_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* 快速操作 */}
              {canEditProject && (
                <Card>
                  <CardHeader>
                    <CardTitle>快速操作</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Button 
                      className="w-full justify-start" 
                      variant="outline"
                      onClick={() => router.push(`/projects/${projectId}/documents/new`)}
                    >
                      创建文档
                    </Button>
                    
                    <Button 
                      className="w-full justify-start" 
                      variant="outline"
                      onClick={() => router.push(`/projects/${projectId}/forms/new`)}
                    >
                      创建表单
                    </Button>
                    
                    <Button 
                      className="w-full justify-start" 
                      variant="outline"
                      onClick={() => router.push(`/projects/${projectId}/edit`)}
                    >
                      编辑项目
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function ProjectDetailPage() {
  return (
    <RouteGuard requireAuth={true}>
      <ProjectDetailPageContent />
    </RouteGuard>
  )
}
