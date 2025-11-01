'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ProjectWithDetails, ProjectStatus, ProjectType } from '@/types'
import { formatDistanceToNow } from '@/utils'

interface ProjectCardProps {
  project: ProjectWithDetails
  onView?: (id: number) => void
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  showActions?: boolean
}

const statusColors = {
  [ProjectStatus.DRAFT]: 'bg-gray-100 text-gray-800',
  [ProjectStatus.GENERATING]: 'bg-blue-100 text-blue-800',
  [ProjectStatus.REVIEWING]: 'bg-yellow-100 text-yellow-800',
  [ProjectStatus.COMPLETED]: 'bg-green-100 text-green-800',
  [ProjectStatus.ARCHIVED]: 'bg-gray-100 text-gray-600',
}

const statusLabels = {
  [ProjectStatus.DRAFT]: '草稿',
  [ProjectStatus.GENERATING]: '生成中',
  [ProjectStatus.REVIEWING]: '审核中',
  [ProjectStatus.COMPLETED]: '已完成',
  [ProjectStatus.ARCHIVED]: '已归档',
}

const typeLabels = {
  [ProjectType.EMERGENCY_PLAN]: '应急预案',
  [ProjectType.ENVIRONMENTAL_ASSESSMENT]: '环境评估',
}

export function ProjectCard({ 
  project, 
  onView, 
  onEdit, 
  onDelete, 
  showActions = true 
}: ProjectCardProps) {
  const handleView = () => {
    if (onView) onView(project.id)
  }

  const handleEdit = () => {
    if (onEdit) onEdit(project.id)
  }

  const handleDelete = () => {
    if (onDelete) onDelete(project.id)
  }

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle 
              className="text-lg font-semibold line-clamp-2"
              onClick={handleView}
            >
              {project.name}
            </CardTitle>
            <CardDescription className="mt-1 line-clamp-2">
              {project.description || '暂无描述'}
            </CardDescription>
          </div>
          {showActions && (
            <div className="flex items-center space-x-1 ml-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleView}
                className="h-8 w-8 p-0"
              >
                查看
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleEdit}
                className="h-8 w-8 p-0"
              >
                编辑
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleDelete}
                className="h-8 w-8 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                删除
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">类型</span>
            <span className="text-sm font-medium">
              {typeLabels[project.type] || project.type}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">状态</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[project.status]}`}>
              {statusLabels[project.status] || project.status}
            </span>
          </div>

          {project.progress !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">进度</span>
              <div className="flex items-center">
                <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${project.progress}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-600">{project.progress}%</span>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">创建时间</span>
            <span className="text-sm text-gray-600">
              {formatDistanceToNow(new Date(project.created_at))}
            </span>
          </div>

          {(project.documents_count !== undefined || project.forms_count !== undefined) && (
            <div className="flex items-center justify-between pt-2 border-t">
              <div className="flex items-center space-x-4">
                {project.documents_count !== undefined && (
                  <div className="text-sm">
                    <span className="text-gray-500">文档: </span>
                    <span className="font-medium">{project.documents_count}</span>
                  </div>
                )}
                {project.forms_count !== undefined && (
                  <div className="text-sm">
                    <span className="text-gray-500">表单: </span>
                    <span className="font-medium">{project.forms_count}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}