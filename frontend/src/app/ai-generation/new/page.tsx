'use client'

import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AIGenerationForm } from '@/components/ai-generation/AIGenerationForm'
import { AIGenerationStatus } from '@/components/ai-generation/AIGenerationStatus'
import { AIGenerationResult } from '@/components/ai-generation/AIGenerationResult'
import { RouteGuard } from '@/components/auth/route-guard'
import { aiGenerationApi } from '@/lib/api'
import { 
  AIGenerationRequest, 
  AIGenerationResponse, 
  AIGenerationWithDetails, 
  AIGenerationStatus as AIGenerationStatusEnum,
  AIGenerationConfig 
} from '@/types'

function AIGenerationNewPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const type = searchParams.get('type') || 'general'
  const regenerateId = searchParams.get('regenerate')
  
  const [currentStep, setCurrentStep] = useState<'form' | 'generating' | 'result'>('form')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [generationRequest, setGenerationRequest] = useState<AIGenerationRequest | null>(null)
  const [generationResponse, setGenerationResponse] = useState<AIGenerationResponse | null>(null)
  const [generationDetails, setGenerationDetails] = useState<AIGenerationWithDetails | null>(null)
  const [documentId, setDocumentId] = useState<number>(1) // 默认文档ID，实际应用中可能需要从上下文获取

  useEffect(() => {
    if (regenerateId) {
      loadRegenerationData(parseInt(regenerateId))
    }
  }, [regenerateId])

  const loadRegenerationData = async (id: number) => {
    try {
      const response = await aiGenerationApi.getAIGeneration(id)
      
      if (response.success && response.data) {
        const generation = response.data
        setGenerationDetails(generation)
        
        // 预填充表单数据
        setGenerationRequest({
          prompt: generation.prompt,
          context: '',
          generation_config: normalizeGenerationConfig(generation.generation_config),
          section: '',
        })
      }
    } catch (err) {
      setError('加载重新生成数据失败')
      console.error('Failed to load regeneration data:', err)
    }
  }

  const getDefaultConfig = (): AIGenerationConfig => {
    switch (type) {
      case 'emergency_plan':
        return {
          model: 'gpt-4',
          temperature: 0.7,
          max_tokens: 3000,
          top_p: 0.9,
          frequency_penalty: 0.1,
          presence_penalty: 0.1,
          stop_sequences: [],
          system_prompt: '你是一个专业的应急预案编写专家，擅长根据企业信息生成详细、实用的应急预案文档。',
        }
      case 'environmental_assessment':
        return {
          model: 'gpt-4',
          temperature: 0.6,
          max_tokens: 4000,
          top_p: 0.9,
          frequency_penalty: 0.1,
          presence_penalty: 0.1,
          stop_sequences: [],
          system_prompt: '你是一个环境影响评价专家，擅长根据项目信息生成专业、全面的环境影响评价报告。',
        }
      default:
        return {
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 2000,
          top_p: 0.9,
          frequency_penalty: 0.1,
          presence_penalty: 0.1,
          stop_sequences: [],
          system_prompt: '',
        }
    }
  }

  const normalizeGenerationConfig = (
    config: AIGenerationConfig | Record<string, any> | null | undefined
  ): AIGenerationConfig => {
    if (!config || typeof config !== 'object') {
      return getDefaultConfig()
    }

    const base = getDefaultConfig()
    const partial = config as Partial<AIGenerationConfig>

    return {
      ...base,
      ...partial,
    }
  }

  const getInitialPrompt = (): string => {
    switch (type) {
      case 'emergency_plan':
        return '请为以下企业生成一份完整的应急预案：\n\n企业名称：\n行业类型：\n企业规模：\n主要风险点：\n\n请包含以下内容：\n1. 总则\n2. 组织机构与职责\n3. 预防与预警\n4. 应急响应\n5. 后期处置\n6. 保障措施\n7. 培训与演练'
      case 'environmental_assessment':
        return '请为以下项目生成一份环境影响评价报告：\n\n项目名称：\n项目地点：\n项目类型：\n建设规模：\n\n请包含以下内容：\n1. 项目概况\n2. 环境现状调查\n3. 环境影响识别与评价\n4. 环境保护措施\n5. 环境风险评价\n6. 公众参与\n7. 评价结论'
      default:
        return ''
    }
  }

  const handleSubmit = async (data: AIGenerationRequest) => {
    setIsLoading(true)
    setError(null)
    setGenerationRequest(data)
    setCurrentStep('generating')

    try {
      let response: any

      switch (type) {
        case 'emergency_plan':
          // 这里需要根据实际的企业信息调用相应的API
          response = await aiGenerationApi.generateEmergencyPlan(
            'comprehensive', // 预案类型
            { company_info: '企业信息' }, // 企业信息，实际应用中需要从表单获取
            documentId
          )
          break
        case 'environmental_assessment':
          // 这里需要根据实际的项目信息调用相应的API
          response = await aiGenerationApi.generateEnvironmentalAssessment(
            { project_info: '项目信息' }, // 项目信息，实际应用中需要从表单获取
            documentId
          )
          break
        default:
          response = await aiGenerationApi.generateContent(data, documentId)
          break
      }

      if (response.success && response.data) {
        setGenerationResponse(response.data)
        
        // 如果是同步完成，获取详细信息
        if (response.data.status === AIGenerationStatusEnum.COMPLETED) {
          const detailResponse = await aiGenerationApi.getAIGeneration(response.data.id)
          if (detailResponse.success && detailResponse.data) {
            setGenerationDetails(detailResponse.data)
          }
        }
        
        setCurrentStep('result')
      } else {
        setError(response.error || '生成失败')
        setCurrentStep('form')
      }
    } catch (err) {
      setError('生成失败')
      setCurrentStep('form')
      console.error('Failed to generate content:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    router.back()
  }

  const handleCopy = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content)
      // 这里可以添加成功提示
    } catch (err) {
      console.error('Failed to copy content:', err)
      // 这里可以添加失败提示
    }
  }

  const handleDownload = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const handleRegenerate = (id: number) => {
    router.push(`/ai-generation/new?regenerate=${id}`)
  }

  const handleNewGeneration = () => {
    router.push('/ai-generation/new')
  }

  const getPageTitle = () => {
    if (regenerateId) return '重新生成内容'
    
    switch (type) {
      case 'emergency_plan':
        return '生成应急预案'
      case 'environmental_assessment':
        return '生成环评报告'
      default:
        return 'AI内容生成'
    }
  }

  const getPageDescription = () => {
    if (regenerateId) return '基于原有配置重新生成AI内容'
    
    switch (type) {
      case 'emergency_plan':
        return '根据企业信息生成专业的应急预案文档'
      case 'environmental_assessment':
        return '根据项目信息生成环境影响评价报告'
      default:
        return '使用AI技术生成各类专业内容'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* 页面标题 */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              {getPageTitle()}
            </h1>
            <p className="mt-2 text-gray-600">
              {getPageDescription()}
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-800">{error}</div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep('form')}
                className="mt-2"
              >
                重新开始
              </Button>
            </div>
          )}

          {/* 表单步骤 */}
          {currentStep === 'form' && (
            <AIGenerationForm
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              isLoading={isLoading}
              initialData={{
                prompt: getInitialPrompt(),
                generation_config: getDefaultConfig(),
              }}
              documentId={documentId}
            />
          )}

          {/* 生成中步骤 */}
          {currentStep === 'generating' && generationResponse && (
            <div className="space-y-6">
              <AIGenerationStatus
                generationId={generationResponse.id}
                onComplete={(status) => {
                  // 生成完成后获取详细信息
                  aiGenerationApi.getAIGeneration(status.id).then(response => {
                    if (response.success && response.data) {
                      setGenerationDetails(response.data)
                      setCurrentStep('result')
                    }
                  })
                }}
                onFailed={() => {
                  setError('生成失败，请重试')
                  setCurrentStep('form')
                }}
              />
              
              <div className="text-center">
                <Button
                  variant="outline"
                  onClick={() => setCurrentStep('form')}
                  disabled={isLoading}
                >
                  取消生成
                </Button>
              </div>
            </div>
          )}

          {/* 结果步骤 */}
          {currentStep === 'result' && generationDetails && (
            <div className="space-y-6">
              <AIGenerationResult
                generation={generationDetails}
                onCopy={handleCopy}
                onDownload={handleDownload}
                onRegenerate={handleRegenerate}
              />
              
              <div className="flex justify-center space-x-4">
                <Button
                  variant="outline"
                  onClick={handleNewGeneration}
                >
                  创建新生成
                </Button>
                <Button
                  onClick={() => router.push('/ai-generation')}
                >
                  返回首页
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AIGenerationNewPage() {
  return (
    <RouteGuard requireAuth={true}>
      <AIGenerationNewPageContent />
    </RouteGuard>
  )
}
