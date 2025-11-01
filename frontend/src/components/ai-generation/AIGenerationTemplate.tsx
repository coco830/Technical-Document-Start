'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import type { AIGenerationTemplate as AIGenerationTemplateType } from '@/types'
import { aiGenerationApi } from '@/lib/api'

interface AIGenerationTemplateProps {
  onTemplateSelect: (template: AIGenerationTemplateType) => void
  selectedTemplate?: AIGenerationTemplateType | null
  disabled?: boolean
}

export function AIGenerationTemplate({ 
  onTemplateSelect, 
  selectedTemplate, 
  disabled = false 
}: AIGenerationTemplateProps) {
  const [templates, setTemplates] = useState<AIGenerationTemplateType[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  useEffect(() => {
    fetchTemplates()
  }, [])

  const fetchTemplates = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await aiGenerationApi.getAllTemplates()
      
      if (response.success && response.data) {
        setTemplates(response.data.templates)
      } else {
        setError(response.error || '获取模板失败')
      }
    } catch (err) {
      setError('获取模板失败')
      console.error('Failed to fetch templates:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const categoryList = templates
    .map(template => template.category)
    .filter((category): category is string => typeof category === 'string' && category.length > 0)

  const categories = ['all', ...Array.from(new Set(categoryList))]

  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(t => t.category === selectedCategory)

  const handleTemplateClick = (template: AIGenerationTemplateType) => {
    if (!disabled) {
      onTemplateSelect(template)
    }
  }

  return (
    <div className="space-y-4">
      {/* 分类筛选 */}
      <div className="flex flex-wrap gap-2">
        {categories.map(category => (
          <button
            key={category}
            type="button"
            onClick={() => setSelectedCategory(category)}
            disabled={disabled}
            className={`px-3 py-1 rounded-full text-sm ${
              selectedCategory === category
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } disabled:opacity-50`}
          >
            {category === 'all' ? '全部' : category}
          </button>
        ))}
      </div>

      {/* 加载状态 */}
      {isLoading && (
        <div className="flex justify-center items-center py-8">
          <div className="text-gray-600">加载模板中...</div>
        </div>
      )}

      {/* 错误状态 */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <div className="text-red-800">{error}</div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchTemplates}
            className="mt-2"
            disabled={disabled}
          >
            重试
          </Button>
        </div>
      )}

      {/* 模板列表 */}
      {!isLoading && !error && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTemplates.map(template => (
            <Card 
              key={template.id}
              className={`cursor-pointer transition-all hover:shadow-md ${
                selectedTemplate?.id === template.id 
                  ? 'ring-2 ring-blue-500 bg-blue-50' 
                  : 'hover:bg-gray-50'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
              onClick={() => handleTemplateClick(template)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <CardTitle className="text-sm font-medium line-clamp-2">
                    {template.name}
                  </CardTitle>
                  {template.category && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                      {template.category}
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 line-clamp-3 mb-3">
                  {template.description || '暂无描述'}
                </p>
                
                <div className="space-y-2 text-xs text-gray-500">
                  <div className="flex justify-between">
                    <span>模型:</span>
                    <span>{template.config.model}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>温度:</span>
                    <span>{template.config.temperature}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>最大令牌:</span>
                    <span>{template.config.max_tokens}</span>
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t">
                  <div className="text-xs text-gray-500">
                    <div className="font-medium mb-1">提示词预览:</div>
                    <div className="line-clamp-2 bg-gray-50 p-2 rounded">
                      {template.prompt_template}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* 空状态 */}
      {!isLoading && !error && filteredTemplates.length === 0 && (
        <div className="text-center py-8">
          <div className="text-gray-600">
            {selectedCategory === 'all' ? '暂无可用模板' : '该分类下暂无模板'}
          </div>
        </div>
      )}
    </div>
  )
}
