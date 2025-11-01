'use client'

import { Editor } from '@tiptap/react'
import { Button } from '@/components/ui/button'
import { 
  File, 
  Save, 
  Download, 
  Eye, 
  History, 
  Settings,
  HelpCircle,
  Maximize2,
  Minimize2
} from 'lucide-react'

interface EditorMenuBarProps {
  editor: Editor | null
  onSave?: () => void
  onPreview?: () => void
  onExport?: (format: 'pdf' | 'docx' | 'html' | 'markdown') => void
  onVersionHistory?: () => void
  onSettings?: () => void
  onFullscreen?: () => void
  isFullscreen?: boolean
  isSaving?: boolean
  hasUnsavedChanges?: boolean
}

export default function EditorMenuBar({
  editor,
  onSave,
  onPreview,
  onExport,
  onVersionHistory,
  onSettings,
  onFullscreen,
  isFullscreen = false,
  isSaving = false,
  hasUnsavedChanges = false
}: EditorMenuBarProps) {
  if (!editor) {
    return null
  }

  const handleExport = (format: 'pdf' | 'docx' | 'html' | 'markdown') => {
    onExport?.(format)
  }

  return (
    <div className="border-b border-gray-200 bg-white px-4 py-2 flex items-center justify-between">
      <div className="flex items-center gap-2">
        {/* 文件操作 */}
        <div className="flex items-center gap-1 mr-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSave}
            disabled={isSaving}
            className="relative"
            title="保存"
          >
            <Save className="h-4 w-4" />
            {isSaving && (
              <span className="absolute -top-1 -right-1 h-2 w-2 bg-blue-500 rounded-full animate-pulse"></span>
            )}
          </Button>
          
          <div className="relative group">
            <Button variant="ghost" size="sm" title="导出">
              <Download className="h-4 w-4" />
            </Button>
            <div className="absolute top-full left-0 mt-1 p-2 bg-white border rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-opacity z-10 min-w-[120px]">
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

        {/* 视图操作 */}
        <div className="flex items-center gap-1 mr-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onPreview}
            title="预览"
          >
            <Eye className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={onVersionHistory}
            title="版本历史"
          >
            <History className="h-4 w-4" />
          </Button>
        </div>

        {/* 工具 */}
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSettings}
            title="设置"
          >
            <Settings className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            title="帮助"
          >
            <HelpCircle className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* 保存状态 */}
        {hasUnsavedChanges && (
          <span className="text-xs text-orange-600 mr-2">有未保存的更改</span>
        )}
        
        {/* 字数统计 */}
        <span className="text-xs text-gray-500 mr-2">
          {editor.storage.characterCount?.characters() || 0} 字符
        </span>
        
        {/* 全屏切换 */}
        <Button
          variant="ghost"
          size="sm"
          onClick={onFullscreen}
          title={isFullscreen ? "退出全屏" : "全屏"}
        >
          {isFullscreen ? (
            <Minimize2 className="h-4 w-4" />
          ) : (
            <Maximize2 className="h-4 w-4" />
          )}
        </Button>
      </div>
    </div>
  )
}
