'use client'

import React from 'react'
import { CompanyVerification } from '@/types'

interface CompanyStatusProps {
  verificationStatus?: string
  verificationType?: string
  verifiedAt?: string
  verifiedBy?: string
  className?: string
}

// 验证状态映射
const verificationStatusMap = {
  pending: { label: '待验证', color: 'bg-yellow-100 text-yellow-800' },
  verified: { label: '已验证', color: 'bg-green-100 text-green-800' },
  rejected: { label: '已拒绝', color: 'bg-red-100 text-red-800' },
  expired: { label: '已过期', color: 'bg-gray-100 text-gray-800' },
}

// 验证类型映射
const verificationTypeMap = {
  basic: { label: '基础验证', icon: '📋' },
  business_license: { label: '营业执照验证', icon: '📄' },
  tax_certificate: { label: '税务登记证验证', icon: '🧾' },
  organization_code: { label: '组织机构代码验证', icon: '🏢' },
  bank_account: { label: '银行账户验证', icon: '🏦' },
  legal_representative: { label: '法定代表人验证', icon: '👤' },
  comprehensive: { label: '综合验证', icon: '✅' },
}

export function CompanyStatus({ 
  verificationStatus = 'pending', 
  verificationType = 'basic',
  verifiedAt,
  verifiedBy,
  className = ''
}: CompanyStatusProps) {
  const statusInfo = verificationStatusMap[verificationStatus as keyof typeof verificationStatusMap] || 
                    verificationStatusMap.pending
  const typeInfo = verificationTypeMap[verificationType as keyof typeof verificationTypeMap] || 
                  verificationTypeMap.basic

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
        {typeInfo.icon} {statusInfo.label}
      </span>
      
      {verificationType && (
        <span className="text-xs text-gray-500">
          {typeInfo.label}
        </span>
      )}
      
      {verifiedAt && (
        <span className="text-xs text-gray-400">
          {new Date(verifiedAt).toLocaleDateString()}
        </span>
      )}
      
      {verifiedBy && (
        <span className="text-xs text-gray-400">
          by {verifiedBy}
        </span>
      )}
    </div>
  )
}

// 企业验证详情组件
interface CompanyVerificationDetailsProps {
  verifications: CompanyVerification[]
  className?: string
}

export function CompanyVerificationDetails({ 
  verifications, 
  className = '' 
}: CompanyVerificationDetailsProps) {
  if (!verifications || verifications.length === 0) {
    return (
      <div className={`text-center py-4 text-gray-500 ${className}`}>
        <p>暂无验证记录</p>
      </div>
    )
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {verifications.map((verification) => {
        const statusInfo = verificationStatusMap[verification.verification_status as keyof typeof verificationStatusMap] || 
                          verificationStatusMap.pending
        const typeInfo = verificationTypeMap[verification.verification_type as keyof typeof verificationTypeMap] || 
                        verificationTypeMap.basic

        return (
          <div key={verification.id} className="border rounded-lg p-3 bg-gray-50">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{typeInfo.icon}</span>
                <span className="font-medium text-sm">{typeInfo.label}</span>
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusInfo.color}`}>
                {statusInfo.label}
              </span>
            </div>
            
            {verification.verification_data && (
              <div className="text-xs text-gray-600 mb-2">
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(verification.verification_data).map(([key, value]) => (
                    <div key={key}>
                      <span className="font-medium">{key}:</span> {String(value)}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {verification.notes && (
              <div className="text-xs text-gray-500 mb-2">
                <span className="font-medium">备注:</span> {verification.notes}
              </div>
            )}
            
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>
                创建时间: {verification.created_at ? new Date(verification.created_at).toLocaleString() : '未知'}
              </span>
              {verification.verified_at && (
                <span>
                  验证时间: {new Date(verification.verified_at).toLocaleString()}
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// 企业验证状态徽章组件
interface CompanyVerificationBadgeProps {
  status: string
  type?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function CompanyVerificationBadge({ 
  status, 
  type = 'basic',
  size = 'md',
  className = ''
}: CompanyVerificationBadgeProps) {
  const statusInfo = verificationStatusMap[status as keyof typeof verificationStatusMap] || 
                    verificationStatusMap.pending
  const typeInfo = verificationTypeMap[type as keyof typeof verificationTypeMap] || 
                  verificationTypeMap.basic

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
    lg: 'px-3 py-1 text-sm'
  }

  return (
    <span className={`inline-flex items-center space-x-1 rounded-full font-medium ${statusInfo.color} ${sizeClasses[size]} ${className}`}>
      <span>{typeInfo.icon}</span>
      <span>{statusInfo.label}</span>
    </span>
  )
}