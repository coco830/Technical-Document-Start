import { BubbleMenu, Editor } from '@tiptap/react'

interface EditorBubbleMenuProps {
  editor: Editor
}

export default function EditorBubbleMenu({ editor }: EditorBubbleMenuProps) {
  return (
    <BubbleMenu
      editor={editor}
      tippyOptions={{ duration: 100 }}
      className="bg-gray-900 text-white rounded-lg shadow-lg p-1 flex gap-1"
    >
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('bold') ? 'bg-gray-700' : ''
        }`}
        title="加粗 (Ctrl+B)"
      >
        <strong>B</strong>
      </button>

      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors italic ${
          editor.isActive('italic') ? 'bg-gray-700' : ''
        }`}
        title="斜体 (Ctrl+I)"
      >
        I
      </button>

      <button
        onClick={() => editor.chain().focus().toggleStrike().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors line-through ${
          editor.isActive('strike') ? 'bg-gray-700' : ''
        }`}
        title="删除线"
      >
        S
      </button>

      <div className="w-px bg-gray-600 mx-1" />

      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors font-bold ${
          editor.isActive('heading', { level: 2 }) ? 'bg-gray-700' : ''
        }`}
        title="标题"
      >
        H2
      </button>

      <button
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('bulletList') ? 'bg-gray-700' : ''
        }`}
        title="无序列表"
      >
        •
      </button>

      <button
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        className={`px-3 py-1.5 rounded hover:bg-gray-700 transition-colors ${
          editor.isActive('blockquote') ? 'bg-gray-700' : ''
        }`}
        title="引用"
      >
        "
      </button>

      <div className="w-px bg-gray-600 mx-1" />

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
    </BubbleMenu>
  )
}
