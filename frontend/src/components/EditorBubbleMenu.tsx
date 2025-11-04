import { useEffect, useState, useRef } from 'react'
import { Editor } from '@tiptap/react'

interface EditorBubbleMenuProps {
  editor: Editor
}

export default function EditorBubbleMenu({ editor }: EditorBubbleMenuProps) {
  const [show, setShow] = useState(false)
  const [position, setPosition] = useState({ top: 0, left: 0 })
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const updateMenu = () => {
      const { from, to, empty } = editor.state.selection

      // 如果没有选中文本，隐藏菜单
      if (empty) {
        setShow(false)
        return
      }

      // 获取选中文本的DOM范围
      const { view } = editor
      const start = view.coordsAtPos(from)
      const end = view.coordsAtPos(to)

      // 计算工具栏位置（显示在选中文本上方）
      const menuWidth = menuRef.current?.offsetWidth || 300
      const menuHeight = menuRef.current?.offsetHeight || 50

      const left = (start.left + end.left) / 2 - menuWidth / 2
      const top = start.top - menuHeight - 10 // 10px间距

      setPosition({ top, left })
      setShow(true)
    }

    // 监听选择变化和更新事件
    editor.on('selectionUpdate', updateMenu)
    editor.on('update', updateMenu)

    // 监听鼠标松开事件（文本选择完成）
    const handleMouseUp = () => {
      setTimeout(updateMenu, 10)
    }

    window.document.addEventListener('mouseup', handleMouseUp)

    return () => {
      editor.off('selectionUpdate', updateMenu)
      editor.off('update', updateMenu)
      window.document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [editor])

  if (!show) return null

  return (
    <div
      ref={menuRef}
      className="fixed z-50 bg-gray-900 text-white rounded-lg shadow-2xl p-1 flex gap-1 items-center"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
        transition: 'opacity 0.2s',
        opacity: show ? 1 : 0,
      }}
    >
      {/* 加粗 */}
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('bold') ? 'bg-gray-700' : ''
        }`}
        title="加粗 (Ctrl+B)"
      >
        <strong>B</strong>
      </button>

      {/* 斜体 */}
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors italic ${
          editor.isActive('italic') ? 'bg-gray-700' : ''
        }`}
        title="斜体 (Ctrl+I)"
      >
        I
      </button>

      {/* 删除线 */}
      <button
        onClick={() => editor.chain().focus().toggleStrike().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors line-through ${
          editor.isActive('strike') ? 'bg-gray-700' : ''
        }`}
        title="删除线"
      >
        S
      </button>

      <div className="w-px h-6 bg-gray-600 mx-1" />

      {/* 标题 H2 */}
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors font-bold ${
          editor.isActive('heading', { level: 2 }) ? 'bg-gray-700' : ''
        }`}
        title="标题 2"
      >
        H2
      </button>

      {/* 标题 H3 */}
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors font-bold text-sm ${
          editor.isActive('heading', { level: 3 }) ? 'bg-gray-700' : ''
        }`}
        title="标题 3"
      >
        H3
      </button>

      <div className="w-px h-6 bg-gray-600 mx-1" />

      {/* 无序列表 */}
      <button
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('bulletList') ? 'bg-gray-700' : ''
        }`}
        title="无序列表"
      >
        •
      </button>

      {/* 引用 */}
      <button
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('blockquote') ? 'bg-gray-700' : ''
        }`}
        title="引用"
      >
        "
      </button>

      <div className="w-px h-6 bg-gray-600 mx-1" />

      {/* 链接 */}
      <button
        onClick={() => {
          const url = window.prompt('输入链接地址:')
          if (url) {
            editor.chain().focus().setLink({ href: url }).run()
          }
        }}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('link') ? 'bg-gray-700' : ''
        }`}
        title="添加链接"
      >
        🔗
      </button>
    </div>
  )
}
