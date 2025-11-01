'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DocumentCreate, DocumentUpdate, DocumentFormat, DocumentStatus } from '@/types'
import { projectApi } from '@/lib/api'
import { useEffect } from 'react'

const documentSchema = z.object({
  title: z.string().min(1, '标题不能为空').max(200, '标题不能超过200个字符'),
  content: z.string().optional(),
  format: z.nativeEnum(DocumentFormat).default(DocumentFormat.MARKDOWN),
  status: z.nativeEnum(DocumentStatus).default(DocumentStatus.DRAFT),
  project_id: z.number().min(1, '请选择项目'),
  metadata: z.record(z.string(), z.any()).optional(),
})

type DocumentFormData = z.infer<typeof documentSchema>

interface DocumentFormProps {
  initialData?: DocumentUpdate
  projectId?: number
  onSubmit: (data: DocumentCreate | DocumentUpdate) => void | Promise<void>
  onCancel?: () => void
  isLoading?: boolean
  className?: string
}

export default function DocumentForm({
  initialData,
  projectId,
  onSubmit,
  onCancel,
  isLoading = false,
  className
}: DocumentFormProps) {
  const [projects, setProjects] = useState<any[]>([])
  const [loadingProjects, setLoadingProjects] = useState(false)
  const initialProjectId = projectId ?? (initialData as { project_id?: number })?.project_id ?? 0

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    reset
  } = useForm<DocumentFormData>({
    resolver: zodResolver(documentSchema),
    defaultValues: {
      title: initialData?.title || '',
      content: initialData?.content || '',
      format: initialData?.format || DocumentFormat.MARKDOWN,
      status: initialData?.status || DocumentStatus.DRAFT,
      project_id: initialProjectId,
      metadata: initialData?.metadata || {},
    },
  })

  const selectedFormat = watch('format')
  const selectedStatus = watch('status')

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoadingProjects(true)
        const response = await projectApi.getProjects({ limit: 100 })
        if (response.success && response.data) {
          setProjects(response.data.projects)
        }
      } catch (error) {
        console.error('获取项目列表失败:', error)
      } finally {
        setLoadingProjects(false)
      }
    }

    if (!projectId && initialProjectId === 0) {
      fetchProjects()
    }
  }, [projectId, initialProjectId])

  const onFormSubmit = async (data: DocumentFormData) => {
    const submitData = {
      ...data,
      metadata: data.metadata || {},
    }
    await Promise.resolve(onSubmit(submitData))
  }

  const handleContentChange = (content: string) => {
    setValue('content', content)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>
          {initialData ? '编辑文档' : '创建文档'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
          {/* 标题 */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
              文档标题 *
            </label>
            <Input
              id="title"
              placeholder="请输入文档标题"
              {...register('title')}
              className={errors.title ? 'border-red-500' : ''}
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            )}
          </div>

          {/* 项目选择 */}
          {!projectId && (
            <div>
              <label htmlFor="project_id" className="block text-sm font-medium text-gray-700 mb-1">
                所属项目 *
              </label>
              <select
                id="project_id"
                {...register('project_id', { valueAsNumber: true })}
                className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  errors.project_id ? 'border-red-500' : ''
                }`}
                disabled={loadingProjects}
              >
                <option value="">请选择项目</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
              {errors.project_id && (
                <p className="mt-1 text-sm text-red-600">{errors.project_id.message}</p>
              )}
            </div>
          )}

          {/* 文档格式 */}
          <div>
            <label htmlFor="format" className="block text-sm font-medium text-gray-700 mb-1">
              文档格式
            </label>
            <select
              id="format"
              {...register('format')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={DocumentFormat.MARKDOWN}>Markdown</option>
              <option value={DocumentFormat.HTML}>HTML</option>
              <option value={DocumentFormat.PLAIN_TEXT}>纯文本</option>
            </select>
          </div>

          {/* 文档状态 */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              文档状态
            </label>
            <select
              id="status"
              {...register('status')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={DocumentStatus.DRAFT}>草稿</option>
              <option value={DocumentStatus.REVIEWING}>审核中</option>
              <option value={DocumentStatus.APPROVED}>已批准</option>
              <option value={DocumentStatus.PUBLISHED}>已发布</option>
            </select>
          </div>

          {/* 文档内容 */}
          <div>
            <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-1">
              文档内容
            </label>
            <textarea
              id="content"
              placeholder="请输入文档内容"
              {...register('content')}
              rows={10}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.content ? 'border-red-500' : ''
              }`}
              onChange={(e) => handleContentChange(e.target.value)}
            />
            {errors.content && (
              <p className="mt-1 text-sm text-red-600">{errors.content.message}</p>
            )}
          </div>

          {/* 按钮组 */}
          <div className="flex justify-end space-x-2 pt-4">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isLoading}
              >
                取消
              </Button>
            )}
            <Button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? '保存中...' : (initialData ? '更新' : '创建')}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
