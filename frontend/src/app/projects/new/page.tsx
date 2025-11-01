'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ProjectForm } from '@/components/projects/project-form'
import { RouteGuard } from '@/components/auth/route-guard'
import { projectApi } from '@/lib/api'
import { useUserStore, useProjectStore } from '@/store'
import { ProjectType } from '@/types'

function CreateProjectPageContent() {
  const router = useRouter()
  const { user } = useUserStore()
  const { addProject } = useProjectStore()
  
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

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
      const userId = Number(user.id)
      if (Number.isNaN(userId)) {
        throw new Error('无效的用户ID')
      }

      const projectData = {
        ...data,
        user_id: userId,
      }

      const response = await projectApi.createProject(projectData)
      
      if (response.success && response.data) {
        addProject(response.data)
        router.push(`/projects/${response.data.id}`)
      } else {
        setError(response.error || '创建项目失败')
      }
    } catch (err) {
      setError('创建项目失败')
      console.error('Failed to create project:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    router.push('/projects')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              创建新项目
            </h1>
            <p className="mt-2 text-gray-600">
              填写项目基本信息以创建新项目
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-800">{error}</div>
            </div>
          )}

          <ProjectForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  )
}

export default function CreateProjectPage() {
  return (
    <RouteGuard requireAuth={true}>
      <CreateProjectPageContent />
    </RouteGuard>
  )
}
