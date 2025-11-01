'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AIGenerationRequest, AIGenerationResponse, AIGenerationConfig } from '@/types'
import { aiGenerationApi } from '@/lib/api'
import { 
  Wand2, 
  Send, 
  Loader2, 
  Copy, 
  Check,
  Sparkles,
  BookOpen,
  FileText,
  Lightbulb
} from 'lucide-react'

interface AIWritingAssistantProps {
  documentId: number
  documentContent?: string
  onContentGenerated: (content: string) => void
  onInsertToEditor: (content: string) => void
  className?: string
}

export default function AIWritingAssistant({
  documentId,
  documentContent = '',
  onContentGenerated,
  onInsertToEditor,
  className
}: AIWritingAssistantProps) {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedContent, setGeneratedContent] = useState('')
  const [generationHistory, setGenerationHistory] = useState<Array<{
    prompt: string
    content: string
    timestamp: Date
  }>>([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [showTemplates, setShowTemplates] = useState(false)

  const templates = [
    {
      id: 'expand',
      name: '扩展内容',
      prompt: '请扩展以下内容，使其更加详细和丰富：',
      icon: <BookOpen className="h-4 w-4" />
    },
    {
      id: 'improve',
      name: '改进文笔',
      prompt: '请改进以下内容的文笔，使其更加流畅和专业：',
      icon: <Sparkles className="h-4 w-4" />
    },
    {
      id: 'summarize',
      name: '总结内容',
      prompt: '请总结以下内容的主要观点：',
      icon: <FileText className="h-4 w-4" />
    },
    {
      id: 'ideas',
      name: '生成想法',
      prompt: '基于以下内容，请生成一些相关的想法和建议：',
      icon: <Lightbulb className="h-4 w-4" />
    }
  ]

  const defaultConfig: AIGenerationConfig = {
    model: 'gpt-3.5-turbo',
    temperature: 0.7,
    max_tokens: 1000,
    top_p: 1,
    frequency_penalty: 0,
    presence_penalty: 0,
    system_prompt: '你是一个专业的写作助手，帮助用户改进和生成高质量的文档内容。'
  }

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setIsGenerating(true)
    try {
      const request: AIGenerationRequest = {
        prompt: selectedTemplate 
          ? `${templates.find(t => t.id === selectedTemplate)?.prompt}\n\n${prompt}`
          : prompt,
        context: documentContent,
        generation_config: defaultConfig
      }

      const response = await aiGenerationApi.generateContent(request, documentId)
      
      if (response.success && response.data?.generated_content) {
        const content = response.data.generated_content
        setGeneratedContent(content)
        onContentGenerated(content)
        
        // 添加到历史记录
        setGenerationHistory(prev => [
          {
            prompt: selectedTemplate 
              ? `${templates.find(t => t.id === selectedTemplate)?.name}: ${prompt}`
              : prompt,
            content,
            timestamp: new Date()
          },
          ...prev.slice(0, 9) // 只保留最近10条记录
        ])
        
        setPrompt('')
        setSelectedTemplate('')
      }
    } catch (error) {
      console.error('生成内容失败:', error)
      alert('生成内容失败，请稍后重试')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleInsertToEditor = () => {
    if (generatedContent) {
      onInsertToEditor(generatedContent)
    }
  }

  const handleCopyToClipboard = async () => {
    if (generatedContent) {
      try {
        await navigator.clipboard.writeText(generatedContent)
        // 这里可以添加一个toast提示
      } catch (error) {
        console.error('复制失败:', error)
      }
    }
  }

  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId)
    setShowTemplates(false)
  }

  const handleHistoryItemClick = (item: typeof generationHistory[0]) => {
    setGeneratedContent(item.content)
    onContentGenerated(item.content)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wand2 className="h-5 w-5" />
          AI写作助手
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 模板选择 */}
        <div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowTemplates(!showTemplates)}
            className="w-full justify-between"
          >
            <span className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              {selectedTemplate 
                ? templates.find(t => t.id === selectedTemplate)?.name 
                : '选择写作模板'
              }
            </span>
          </Button>
          
          {showTemplates && (
            <div className="mt-2 grid grid-cols-2 gap-2">
              {templates.map((template) => (
                <Button
                  key={template.id}
                  variant={selectedTemplate === template.id ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => handleTemplateSelect(template.id)}
                  className="justify-start"
                >
                  <span className="flex items-center gap-2">
                    {template.icon}
                    {template.name}
                  </span>
                </Button>
              ))}
            </div>
          )}
        </div>

        {/* 输入框 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            写作要求
          </label>
          <div className="flex gap-2">
            <Input
              placeholder="请描述您希望AI生成或改进的内容..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-1"
              disabled={isGenerating}
            />
            <Button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* 生成的内容 */}
        {generatedContent && (
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-sm">生成的内容</h4>
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopyToClipboard}
                  title="复制到剪贴板"
                >
                  <Copy className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleInsertToEditor}
                  title="插入到编辑器"
                >
                  <Check className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg max-h-60 overflow-y-auto">
              <pre className="whitespace-pre-wrap text-sm text-gray-700">
                {generatedContent}
              </pre>
            </div>
          </div>
        )}

        {/* 历史记录 */}
        {generationHistory.length > 0 && (
          <div>
            <h4 className="font-medium text-sm mb-2">历史记录</h4>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {generationHistory.map((item, index) => (
                <div
                  key={index}
                  className="bg-gray-50 p-2 rounded cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleHistoryItemClick(item)}
                >
                  <div className="text-xs text-gray-500 mb-1">
                    {item.timestamp.toLocaleString()}
                  </div>
                  <div className="text-sm font-medium truncate">
                    {item.prompt}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}