'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ProjectForm } from '@/components/projects/project-form'
import { RouteGuard } from '@/components/auth/route-guard'
import { projectApi } from '@/lib/api'
import { useUserStore, useProjectStore } from '@/store'
import { Project, ProjectType } from '@/types'

function EditProjectPageContent() {
  const params = useParams()
  const router = useRouter()
  const { user } = useUserStore()
  const { updateProject } = useProjectStore()
  
  const [project, setProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const projectId = parseInt(params.id as string)

  useEffect(() => {
    if (isNaN(projectId)) {
      setError('无效的项目ID')
      setIsFetching(false)
      return
    }

    fetchProject()
  }, [projectId])

  const fetchProject = async () => {
    try {
      const response = await projectApi.getProject(projectId)
      
      if (response.success && response.data) {
        setProject(response.data)
      } else {
        setError(response.error || '获取项目详情失败')
      }
    } catch (err) {
      setError('获取项目详情失败')
      console.error('Failed to fetch project details:', err)
    } finally {
      setIsFetching(false)
    }
  }

  const handleSubmit = async (data: {
    name: string
    type: ProjectType
    description?: string
    metadata?: Record<string, any>
  }) => {
    if (!user) {
      setError('用户未登录')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const response = await projectApi.updateProject(projectId, data)
      
      if (response.success && response.data) {
        updateProject(projectId.toString(), response.data)
        router.push(`/projects/${projectId}`)
      } else {
        setError(response.error || '更新项目失败')
      }
    } catch (err) {
      setError('更新项目失败')
      console.error('Failed to update project:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    router.push(`/projects/${projectId}`)
  }

  const canEditProject = user && project && (
    user.role === 'admin' || Number(user.id) === project.user_id
  )

  if (isFetching) {
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

  if (!canEditProject) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-red-600 mb-4">
            您没有权限编辑此项目
          </div>
          <Button onClick={() => router.push(`/projects/${projectId}`)}>
            返回项目详情
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              编辑项目
            </h1>
            <p className="mt-2 text-gray-600">
              修改项目信息
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          <ProjectForm
            project={project}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  )
}

export default function EditProjectPage() {
  return (
    <RouteGuard requireAuth={true}>
      <EditProjectPageContent />
    </RouteGuard>
  )
}
