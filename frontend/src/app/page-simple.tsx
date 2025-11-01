'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'

export default function SimpleHome() {
  const [count, setCount] = useState(0)

  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">悦恩人机共写平台</h1>
        <p className="text-gray-600">欢迎使用 AI 辅助写作平台</p>
        <Button onClick={() => setCount(count + 1)}>
          点击次数: {count}
        </Button>
      </div>
    </main>
  )
}
