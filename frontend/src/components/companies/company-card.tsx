'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CompanyWithDetails } from '@/types'
import { formatDistanceToNow } from '@/utils'

interface CompanyCardProps {
  company: CompanyWithDetails
  onView?: (id: number) => void
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
  showActions?: boolean
}

export function CompanyCard({ 
  company, 
  onView, 
  onEdit, 
  onDelete, 
  showActions = true 
}: CompanyCardProps) {
  const handleView = () => {
    if (onView) onView(company.id)
  }

  const handleEdit = () => {
    if (onEdit) onEdit(company.id)
  }

  const handleDelete = () => {
    if (onDelete) onDelete(company.id)
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
              {company.name}
            </CardTitle>
            <CardDescription className="mt-1 line-clamp-2">
              {company.unified_social_credit_code || '暂无统一社会信用代码'}
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
          {company.legal_representative && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">法定代表人</span>
              <span className="text-sm font-medium">{company.legal_representative}</span>
            </div>
          )}
          
          {company.industry && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">所属行业</span>
              <span className="text-sm font-medium">{company.industry}</span>
            </div>
          )}

          {company.contact_phone && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">联系电话</span>
              <span className="text-sm font-medium">{company.contact_phone}</span>
            </div>
          )}

          {company.contact_email && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">联系邮箱</span>
              <span className="text-sm font-medium truncate max-w-[150px]" title={company.contact_email}>
                {company.contact_email}
              </span>
            </div>
          )}

          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">创建时间</span>
            <span className="text-sm text-gray-600">
              {formatDistanceToNow(new Date(company.created_at))}
            </span>
          </div>

          {(company.projects_count !== undefined || 
            company.active_projects_count !== undefined || 
            company.completed_projects_count !== undefined || 
            company.documents_count !== undefined) && (
            <div className="flex items-center justify-between pt-2 border-t">
              <div className="flex items-center space-x-4 text-sm">
                {company.projects_count !== undefined && (
                  <div>
                    <span className="text-gray-500">项目: </span>
                    <span className="font-medium">{company.projects_count}</span>
                  </div>
                )}
                {company.active_projects_count !== undefined && (
                  <div>
                    <span className="text-gray-500">活跃: </span>
                    <span className="font-medium text-green-600">{company.active_projects_count}</span>
                  </div>
                )}
                {company.completed_projects_count !== undefined && (
                  <div>
                    <span className="text-gray-500">完成: </span>
                    <span className="font-medium text-blue-600">{company.completed_projects_count}</span>
                  </div>
                )}
                {company.documents_count !== undefined && (
                  <div>
                    <span className="text-gray-500">文档: </span>
                    <span className="font-medium">{company.documents_count}</span>
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