'use client'

import { DocumentStatus as DocumentStatusEnum } from '@/types'
import { cn } from '@/lib/utils'

interface DocumentStatusProps {
  status: DocumentStatusEnum
  className?: string
  showText?: boolean
}

export default function DocumentStatus({
  status,
  className,
  showText = true
}: DocumentStatusProps) {
  const getStatusConfig = (status: DocumentStatusEnum) => {
    switch (status) {
      case DocumentStatusEnum.DRAFT:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '📝',
          text: '草稿'
        }
      case DocumentStatusEnum.REVIEWING:
        return {
          color: 'bg-blue-100 text-blue-800 border-blue-200',
          icon: '👀',
          text: '审核中'
        }
      case DocumentStatusEnum.APPROVED:
        return {
          color: 'bg-green-100 text-green-800 border-green-200',
          icon: '✅',
          text: '已批准'
        }
      case DocumentStatusEnum.PUBLISHED:
        return {
          color: 'bg-purple-100 text-purple-800 border-purple-200',
          icon: '🌐',
          text: '已发布'
        }
      default:
        return {
          color: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: '❓',
          text: '未知'
        }
    }
  }

  const config = getStatusConfig(status)

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border',
        config.color,
        className
      )}
    >
      <span className="text-sm">{config.icon}</span>
      {showText && <span>{config.text}</span>}
    </div>
  )
}

interface DocumentStatusBadgeProps {
  status: DocumentStatusEnum
  className?: string
}

export function DocumentStatusBadge({ status, className }: DocumentStatusBadgeProps) {
  return <DocumentStatus status={status} className={className} showText={true} />
}

interface DocumentStatusIconProps {
  status: DocumentStatusEnum
  className?: string
}

export function DocumentStatusIcon({ status, className }: DocumentStatusIconProps) {
  return <DocumentStatus status={status} className={className} showText={false} />
}