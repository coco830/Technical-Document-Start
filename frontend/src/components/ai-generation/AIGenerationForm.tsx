'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AIGenerationRequest, AIGenerationConfig, AIGenerationTemplate } from '@/types'
import { AIGenerationConfig as AIGenerationConfigComponent } from './AIGenerationConfig'
import { AIGenerationTemplate as AIGenerationTemplateComponent } from './AIGenerationTemplate'

interface AIGenerationFormProps {
  onSubmit: (data: AIGenerationRequest) => void
  onCancel: () => void
  isLoading?: boolean
  initialData?: Partial<AIGenerationRequest>
  documentId?: number
}

const defaultConfig: AIGenerationConfig = {
  model: 'gpt-3.5-turbo',
  temperature: 0.7,
  max_tokens: 2000,
  top_p: 0.9,
  frequency_penalty: 0.1,
  presence_penalty: 0.1,
  stop_sequences: [],
  system_prompt: '',
}

export function AIGenerationForm({ 
  onSubmit, 
  onCancel, 
  isLoading = false, 
  initialData = {},
  documentId 
}: AIGenerationFormProps) {
  const [formData, setFormData] = useState({
    prompt: initialData.prompt || '',
    context: initialData.context || '',
    section: initialData.section || '',
    generation_config: initialData.generation_config || defaultConfig,
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [selectedTemplate, setSelectedTemplate] = useState<AIGenerationTemplate | null>(null)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    
    // 清除错误
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const handleConfigChange = (config: AIGenerationConfig) => {
    setFormData(prev => ({
      ...prev,
      generation_config: config
    }))
  }

  const handleTemplateSelect = (template: AIGenerationTemplate) => {
    setSelectedTemplate(template)
    setFormData(prev => ({
      ...prev,
      prompt: template.prompt_template,
      generation_config: template.config
    }))
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.prompt.trim()) {
      newErrors.prompt = '提示词不能为空'
    } else if (formData.prompt.length > 2000) {
      newErrors.prompt = '提示词不能超过2000个字符'
    }
    
    if (formData.context && formData.context.length > 5000) {
      newErrors.context = '上下文内容不能超过5000个字符'
    }
    
    if (formData.section && formData.section.length > 100) {
      newErrors.section = '章节名称不能超过100个字符'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (validateForm()) {
      onSubmit(formData)
    }
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>AI内容生成</CardTitle>
        <CardDescription>
          使用AI技术生成专业内容，支持多种生成模式和配置选项
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 模板选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              选择模板（可选）
            </label>
            <AIGenerationTemplateComponent 
              onTemplateSelect={handleTemplateSelect}
              selectedTemplate={selectedTemplate}
            />
          </div>

          {/* 提示词 */}
          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
              提示词 <span className="text-red-500">*</span>
            </label>
            <textarea
              id="prompt"
              name="prompt"
              value={formData.prompt}
              onChange={handleChange}
              placeholder="请输入生成提示词，描述您希望AI生成的内容"
              rows={4}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.prompt ? 'border-red-500' : ''}`}
            />
            {errors.prompt && (
              <p className="mt-1 text-sm text-red-600">{errors.prompt}</p>
            )}
          </div>

          {/* 上下文内容 */}
          <div>
            <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-2">
              上下文内容（可选）
            </label>
            <textarea
              id="context"
              name="context"
              value={formData.context}
              onChange={handleChange}
              placeholder="提供相关的上下文信息，帮助AI更好地理解需求"
              rows={3}
              className={`w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${errors.context ? 'border-red-500' : ''}`}
            />
            {errors.context && (
              <p className="mt-1 text-sm text-red-600">{errors.context}</p>
            )}
          </div>

          {/* 章节名称 */}
          <div>
            <label htmlFor="section" className="block text-sm font-medium text-gray-700 mb-2">
              章节名称（可选）
            </label>
            <Input
              id="section"
              name="section"
              type="text"
              value={formData.section}
              onChange={handleChange}
              placeholder="指定生成内容的章节或部分"
              className={errors.section ? 'border-red-500' : ''}
            />
            {errors.section && (
              <p className="mt-1 text-sm text-red-600">{errors.section}</p>
            )}
          </div>

          {/* 生成配置 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              生成配置
            </label>
            <AIGenerationConfigComponent 
              config={formData.generation_config}
              onChange={handleConfigChange}
            />
          </div>

          {/* 操作按钮 */}
          <div className="flex justify-end space-x-4 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isLoading}
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
            >
              {isLoading ? '生成中...' : '开始生成'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}