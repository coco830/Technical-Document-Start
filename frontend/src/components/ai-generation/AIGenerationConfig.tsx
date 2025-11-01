'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import type { AIGenerationConfig } from '@/types'

interface AIGenerationConfigProps {
  config: AIGenerationConfig
  onChange: (config: AIGenerationConfig) => void
  disabled?: boolean
}

export function AIGenerationConfig({ config, onChange, disabled = false }: AIGenerationConfigProps) {
  const [isAdvancedMode, setIsAdvancedMode] = useState(false)

  const handleChange = (field: keyof AIGenerationConfig, value: any) => {
    const newConfig = { ...config, [field]: value }
    onChange(newConfig)
  }

  const handleStopSequenceChange = (index: number, value: string) => {
    const newStopSequences = [...(config.stop_sequences || [])]
    newStopSequences[index] = value
    handleChange('stop_sequences', newStopSequences)
  }

  const addStopSequence = () => {
    const newStopSequences = [...(config.stop_sequences || []), '']
    handleChange('stop_sequences', newStopSequences)
  }

  const removeStopSequence = (index: number) => {
    const newStopSequences = [...(config.stop_sequences || [])]
    newStopSequences.splice(index, 1)
    handleChange('stop_sequences', newStopSequences)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">生成配置</CardTitle>
          <button
            type="button"
            onClick={() => setIsAdvancedMode(!isAdvancedMode)}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            {isAdvancedMode ? '简化配置' : '高级配置'}
          </button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 基础配置 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-2">
              模型
            </label>
            <select
              id="model"
              value={config.model}
              onChange={(e) => handleChange('model', e.target.value)}
              disabled={disabled}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
          </div>

          <div>
            <label htmlFor="max_tokens" className="block text-sm font-medium text-gray-700 mb-2">
              最大令牌数
            </label>
            <Input
              id="max_tokens"
              type="number"
              min="1"
              max="4000"
              value={config.max_tokens}
              onChange={(e) => handleChange('max_tokens', parseInt(e.target.value) || 2000)}
              disabled={disabled}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 mb-2">
              温度 (0-2): {config.temperature}
            </label>
            <input
              id="temperature"
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={config.temperature}
              onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
              disabled={disabled}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>保守</span>
              <span>平衡</span>
              <span>创新</span>
            </div>
          </div>

          <div>
            <label htmlFor="top_p" className="block text-sm font-medium text-gray-700 mb-2">
              核采样 (0-1): {config.top_p}
            </label>
            <input
              id="top_p"
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={config.top_p}
              onChange={(e) => handleChange('top_p', parseFloat(e.target.value))}
              disabled={disabled}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>专注</span>
              <span>平衡</span>
              <span>多样</span>
            </div>
          </div>
        </div>

        {/* 高级配置 */}
        {isAdvancedMode && (
          <div className="space-y-4 pt-4 border-t">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="frequency_penalty" className="block text-sm font-medium text-gray-700 mb-2">
                  频率惩罚 (-2 到 2): {config.frequency_penalty}
                </label>
                <input
                  id="frequency_penalty"
                  type="range"
                  min="-2"
                  max="2"
                  step="0.1"
                  value={config.frequency_penalty}
                  onChange={(e) => handleChange('frequency_penalty', parseFloat(e.target.value))}
                  disabled={disabled}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>重复</span>
                  <span>平衡</span>
                  <span>多样</span>
                </div>
              </div>

              <div>
                <label htmlFor="presence_penalty" className="block text-sm font-medium text-gray-700 mb-2">
                  存在惩罚 (-2 到 2): {config.presence_penalty}
                </label>
                <input
                  id="presence_penalty"
                  type="range"
                  min="-2"
                  max="2"
                  step="0.1"
                  value={config.presence_penalty}
                  onChange={(e) => handleChange('presence_penalty', parseFloat(e.target.value))}
                  disabled={disabled}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>重复</span>
                  <span>平衡</span>
                  <span>多样</span>
                </div>
              </div>
            </div>

            <div>
              <label htmlFor="system_prompt" className="block text-sm font-medium text-gray-700 mb-2">
                系统提示词
              </label>
              <textarea
                id="system_prompt"
                value={config.system_prompt || ''}
                onChange={(e) => handleChange('system_prompt', e.target.value)}
                disabled={disabled}
                placeholder="设置AI的角色和行为指导"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                停止序列
              </label>
              <div className="space-y-2">
                {(config.stop_sequences || []).map((sequence, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <Input
                      value={sequence}
                      onChange={(e) => handleStopSequenceChange(index, e.target.value)}
                      disabled={disabled}
                      placeholder="输入停止序列"
                    />
                    <button
                      type="button"
                      onClick={() => removeStopSequence(index)}
                      disabled={disabled}
                      className="px-3 py-2 text-red-600 border border-red-300 rounded-md hover:bg-red-50 disabled:opacity-50"
                    >
                      删除
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addStopSequence}
                  disabled={disabled}
                  className="px-3 py-2 text-blue-600 border border-blue-300 rounded-md hover:bg-blue-50 disabled:opacity-50"
                >
                  添加停止序列
                </button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
