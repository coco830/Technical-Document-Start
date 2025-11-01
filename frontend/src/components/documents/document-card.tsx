'use client'

import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { DocumentWithDetails } from '@/types'
import { DocumentStatus, DocumentFormat } from '@/types'
import { formatDistanceToNow } from '@/lib/utils'
import { 
  Eye, 
  Edit, 
  Trash2, 
  Download, 
  History,
  FileText,
  Clock,
  User
} from 'lucide-react'

interface DocumentCardProps {
  document: DocumentWithDetails
  onView?: (id: number) => void
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  onExport?: (id: number, format: 'pdf' | 'docx' | 'html' | 'markdown') => void
  onVersionHistory?: (id: number) => void
  className?: string
}

export default function DocumentCard({
  document,
  onView,
  onEdit,
  onDelete,
  onExport,
  onVersionHistory,
  className
}: DocumentCardProps) {
  const getStatusColor = (status: DocumentStatus) => {
    switch (status) {
      case DocumentStatus.DRAFT:
        return 'bg-gray-100 text-gray-800'
      case DocumentStatus.REVIEWING:
        return 'bg-blue-100 text-blue-800'
      case DocumentStatus.APPROVED:
        return 'bg-green-100 text-green-800'
      case DocumentStatus.PUBLISHED:
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: DocumentStatus) => {
    switch (status) {
      case DocumentStatus.DRAFT:
        return '草稿'
      case DocumentStatus.REVIEWING:
        return '审核中'
      case DocumentStatus.APPROVED:
        return '已批准'
      case DocumentStatus.PUBLISHED:
        return '已发布'
      default:
        return '未知'
    }
  }

  const getFormatIcon = (format: DocumentFormat) => {
    switch (format) {
      case DocumentFormat.MARKDOWN:
        return <FileText className="h-4 w-4" />
      case DocumentFormat.HTML:
        return <FileText className="h-4 w-4" />
      case DocumentFormat.PLAIN_TEXT:
        return <FileText className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getFormatText = (format: DocumentFormat) => {
    switch (format) {
      case DocumentFormat.MARKDOWN:
        return 'Markdown'
      case DocumentFormat.HTML:
        return 'HTML'
      case DocumentFormat.PLAIN_TEXT:
        return '纯文本'
      default:
        return '未知'
    }
  }

  const handleExport = (format: 'pdf' | 'docx' | 'html' | 'markdown') => {
    onExport?.(document.id, format)
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h3 className="font-semibold text-lg line-clamp-2 mb-2">
              {document.title}
            </h3>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              {getFormatIcon(document.format)}
              <span>{getFormatText(document.format)}</span>
              <span className="text-gray-300">•</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(document.status)}`}>
                {getStatusText(document.status)}
              </span>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pb-3">
        {document.content && (
          <p className="text-sm text-gray-600 line-clamp-3 mb-3">
            {document.content.replace(/<[^>]*>/g, '').substring(0, 150)}...
          </p>
        )}
        
        <div className="space-y-2 text-sm text-gray-500">
          {document.project_name && (
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              <span>项目: {document.project_name}</span>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            <span>更新于 {formatDistanceToNow(new Date(document.updated_at))}</span>
          </div>
          
          <div className="flex items-center gap-4 text-xs">
            <span>版本: {document.versions_count || 0}</span>
            <span>AI生成: {document.ai_generations_count || 0}</span>
            <span>导出: {document.exports_count || 0}</span>
          </div>
        </div>
      </CardContent>
      
      <CardFooter className="pt-3">
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onView?.(document.id)}
              title="查看"
            >
              <Eye className="h-4 w-4" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit?.(document.id)}
              title="编辑"
            >
              <Edit className="h-4 w-4" />
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onVersionHistory?.(document.id)}
              title="版本历史"
            >
              <History className="h-4 w-4" />
            </Button>
            
            <div className="relative group">
              <Button
                variant="ghost"
                size="sm"
                title="导出"
              >
                <Download className="h-4 w-4" />
              </Button>
              <div className="absolute top-full right-0 mt-1 p-2 bg-white border rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-opacity z-10 min-w-[120px]">
                <button
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                  onClick={() => handleExport('pdf')}
                >
                  导出为 PDF
                </button>
                <button
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                  onClick={() => handleExport('docx')}
                >
                  导出为 Word
                </button>
                <button
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                  onClick={() => handleExport('html')}
                >
                  导出为 HTML
                </button>
                <button
                  className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
                  onClick={() => handleExport('markdown')}
                >
                  导出为 Markdown
                </button>
              </div>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete?.(document.id)}
            className="text-red-600 hover:text-red-800 hover:bg-red-50"
            title="删除"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}