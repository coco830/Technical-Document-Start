'use client'

import React from 'react'
import { ProjectStatus } from '@/types'

interface ProjectStatusProps {
  status: ProjectStatus
  showLabel?: boolean
  className?: string
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

export function ProjectStatusBadge({ 
  status, 
  showLabel = true, 
  className = '' 
}: ProjectStatusProps) {
  const colorClass = statusColors[status] || statusColors[ProjectStatus.DRAFT]
  const label = statusLabels[status] || status

  return (
    <span 
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass} ${className}`}
    >
      {showLabel && label}
    </span>
  )
}

export function ProjectStatusIcon({ status, className = '' }: ProjectStatusProps) {
  const colorClass = statusColors[status] || statusColors[ProjectStatus.DRAFT]

  return (
    <span 
      className={`inline-block w-3 h-3 rounded-full ${colorClass} ${className}`}
      title={statusLabels[status] || status}
    />
  )
}