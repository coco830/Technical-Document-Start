'use client'

import { useState } from 'react'
import { Editor } from '@tiptap/react'
import { Button } from '@/components/ui/button'
import {
  Bold,
  Italic,
  Underline,
  Strikethrough,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Quote,
  Code,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  Undo,
  Redo,
  Link,
  Image,
  Table,
  Highlighter,
  Palette,
  Download,
  FileText
} from 'lucide-react'
import DocumentExportOptions from '@/components/documents/DocumentExportOptions'
import DocumentExportProgress from '@/components/documents/DocumentExportProgress'
import { DocumentExportRequest, ExportStatus } from '@/types'

interface EditorToolbarProps {
  editor: Editor | null
  documentId?: number
  documentTitle?: string
  onExportStart?: (exportRequest: DocumentExportRequest) => void
}

export default function EditorToolbar({ editor, documentId, documentTitle, onExportStart }: EditorToolbarProps) {
  const [showExportOptions, setShowExportOptions] = useState(false)
  const [showExportProgress, setShowExportProgress] = useState(false)
  const [currentExportId, setCurrentExportId] = useState<number | null>(null)

  if (!editor) {
    return null
  }

  // 处理导出开始
  const handleExportStart = (exportRequest: DocumentExportRequest) => {
    // 这里应该调用API并获取导出ID
    // 为了演示，我们假设导出ID为 1
    const exportId = 1
    setCurrentExportId(exportId)
    setShowExportOptions(false)
    setShowExportProgress(true)
    
    if (onExportStart) {
      onExportStart(exportRequest)
    }
  }

  // 处理导出完成
  const handleExportComplete = (exportResult: any) => {
    // 导出完成后的处理逻辑
    console.log('导出完成:', exportResult)
  }

  // 处理导出错误
  const handleExportError = (exportResult: any) => {
    // 导出错误后的处理逻辑
    console.error('导出错误:', exportResult)
  }

  // 处理删除导出
  const handleDeleteExport = (exportId: number) => {
    setCurrentExportId(null)
    setShowExportProgress(false)
  }

  const addImage = () => {
    const url = window.prompt('输入图片URL:')
    if (url) {
      editor.chain().focus().setImage({ src: url }).run()
    }
  }

  const addLink = () => {
    const url = window.prompt('输入链接URL:')
    if (url) {
      editor.chain().focus().setLink({ href: url }).run()
    }
  }

  const addTable = () => {
    editor.chain().focus()
      .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
      .run()
  }

  const setColor = (color: string) => {
    editor.chain().focus().setColor(color).run()
  }

  const setHighlight = (color: string) => {
    editor.chain().focus().setHighlight({ color }).run()
  }

  return (
    <>
      <div className="border-b border-gray-200 p-2 flex flex-wrap gap-1">
      {/* 撤销/重做 */}
      <div className="flex gap-1 mr-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().undo().run()}
          disabled={!editor.can().undo()}
          title="撤销"
        >
          <Undo className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().redo().run()}
          disabled={!editor.can().redo()}
          title="重做"
        >
          <Redo className="h-4 w-4" />
        </Button>
      </div>

      {/* 文本格式 */}
      <div className="flex gap-1 mr-2">
        <Button
          variant={editor.isActive('bold') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleBold().run()}
          title="粗体"
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('italic') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          title="斜体"
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('underline') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          title="下划线"
        >
          <Underline className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('strike') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleStrike().run()}
          title="删除线"
        >
          <Strikethrough className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('code') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleCode().run()}
          title="代码"
        >
          <Code className="h-4 w-4" />
        </Button>
      </div>

      {/* 标题 */}
      <div className="flex gap-1 mr-2">
        <Button
          variant={editor.isActive('heading', { level: 1 }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          title="标题1"
        >
          <Heading1 className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('heading', { level: 2 }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          title="标题2"
        >
          <Heading2 className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('heading', { level: 3 }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          title="标题3"
        >
          <Heading3 className="h-4 w-4" />
        </Button>
      </div>

      {/* 列表 */}
      <div className="flex gap-1 mr-2">
        <Button
          variant={editor.isActive('bulletList') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          title="无序列表"
        >
          <List className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('orderedList') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          title="有序列表"
        >
          <ListOrdered className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive('blockquote') ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          title="引用"
        >
          <Quote className="h-4 w-4" />
        </Button>
      </div>

      {/* 对齐 */}
      <div className="flex gap-1 mr-2">
        <Button
          variant={editor.isActive({ textAlign: 'left' }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          title="左对齐"
        >
          <AlignLeft className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive({ textAlign: 'center' }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          title="居中对齐"
        >
          <AlignCenter className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive({ textAlign: 'right' }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          title="右对齐"
        >
          <AlignRight className="h-4 w-4" />
        </Button>
        <Button
          variant={editor.isActive({ textAlign: 'justify' }) ? 'default' : 'ghost'}
          size="sm"
          onClick={() => editor.chain().focus().setTextAlign('justify').run()}
          title="两端对齐"
        >
          <AlignJustify className="h-4 w-4" />
        </Button>
      </div>

      {/* 颜色和高亮 */}
      <div className="flex gap-1 mr-2">
        <div className="relative group">
          <Button variant="ghost" size="sm" title="文字颜色">
            <Palette className="h-4 w-4" />
          </Button>
          <div className="absolute top-full left-0 mt-1 p-2 bg-white border rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-opacity z-10">
            <div className="grid grid-cols-6 gap-1">
              {['#000000', '#ffffff', '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff', '#ff8800', '#8800ff', '#00ff88', '#ff0088'].map(color => (
                <button
                  key={color}
                  className="w-6 h-6 rounded border border-gray-300"
                  style={{ backgroundColor: color }}
                  onClick={() => setColor(color)}
                />
              ))}
            </div>
          </div>
        </div>
        <div className="relative group">
          <Button variant="ghost" size="sm" title="高亮">
            <Highlighter className="h-4 w-4" />
          </Button>
          <div className="absolute top-full left-0 mt-1 p-2 bg-white border rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-opacity z-10">
            <div className="grid grid-cols-6 gap-1">
              {['#fef08a', '#fde047', '#facc15', '#eab308', '#ca8a04', '#a16207', '#fef3c7', '#fde68a', '#fcd34d', '#fbbf24', '#f59e0b', '#d97706'].map(color => (
                <button
                  key={color}
                  className="w-6 h-6 rounded border border-gray-300"
                  style={{ backgroundColor: color }}
                  onClick={() => setHighlight(color)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 插入 */}
      <div className="flex gap-1">
        <Button
          variant={editor.isActive('link') ? 'default' : 'ghost'}
          size="sm"
          onClick={addLink}
          title="插入链接"
        >
          <Link className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={addImage}
          title="插入图片"
        >
          <Image className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={addTable}
          title="插入表格"
        >
          <Table className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setShowExportOptions(true)}
          title="导出文档"
        >
          <Download className="h-4 w-4" />
        </Button>
      </div>
    </div>

    {/* 导出选项弹窗 */}
    {showExportOptions && documentId && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <FileText className="h-5 w-5" />
                导出文档
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowExportOptions(false)}
              >
                ×
              </Button>
            </div>
            <DocumentExportOptions
              documentId={documentId}
              documentTitle={documentTitle || '未命名文档'}
              onExportStart={handleExportStart}
              onCancel={() => setShowExportOptions(false)}
            />
          </div>
        </div>
      </div>
    )}

    {/* 导出进度弹窗 */}
    {showExportProgress && currentExportId && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">导出进度</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowExportProgress(false)}
              >
                ×
              </Button>
            </div>
            <DocumentExportProgress
              exportId={currentExportId}
              onComplete={handleExportComplete}
              onError={handleExportError}
              onDelete={handleDeleteExport}
            />
          </div>
        </div>
      </div>
    )}
    </>
  )
}