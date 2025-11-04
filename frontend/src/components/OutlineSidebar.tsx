import { Editor } from '@tiptap/react'

interface OutlineSidebarProps {
  editor: Editor | null
  outline: { level: number; text: string; id: string }[]
  show: boolean
  onToggle: () => void
}

export default function OutlineSidebar({ editor, outline, show, onToggle }: OutlineSidebarProps) {
  const scrollToHeading = (text: string) => {
    if (!editor) return

    // 简单的滚动到标题功能
    const headings = window.document.querySelectorAll('h1, h2, h3, h4, h5, h6')
    for (const heading of headings) {
      if (heading.textContent === text) {
        heading.scrollIntoView({ behavior: 'smooth', block: 'start' })
        break
      }
    }
  }

  if (!show) {
    return (
      <button
        onClick={onToggle}
        className="fixed right-0 top-1/2 -translate-y-1/2 bg-primary text-white px-2 py-4 rounded-l-lg shadow-lg hover:bg-green-700 transition-colors z-10"
        title="显示大纲"
      >
        📋
      </button>
    )
  }

  return (
    <div className="fixed right-0 top-16 bottom-0 w-64 bg-white border-l border-gray-200 shadow-lg overflow-y-auto z-10">
      <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
        <h3 className="font-semibold text-gray-900">文档大纲</h3>
        <button
          onClick={onToggle}
          className="text-gray-500 hover:text-gray-700"
          title="隐藏大纲"
        >
          ✕
        </button>
      </div>

      <div className="p-4">
        {outline.length === 0 ? (
          <p className="text-gray-400 text-sm italic">暂无标题</p>
        ) : (
          <nav>
            {outline.map((item, index) => (
              <button
                key={index}
                onClick={() => scrollToHeading(item.text)}
                className="block w-full text-left py-2 px-2 hover:bg-gray-100 rounded transition-colors text-sm"
                style={{ paddingLeft: `${(item.level - 1) * 12 + 8}px` }}
              >
                <span className="text-gray-600 mr-2">
                  {item.level === 1 && '📌'}
                  {item.level === 2 && '▪'}
                  {item.level === 3 && '◦'}
                  {item.level > 3 && '·'}
                </span>
                <span className={`${item.level === 1 ? 'font-semibold' : ''}`}>
                  {item.text || '(空标题)'}
                </span>
              </button>
            ))}
          </nav>
        )}
      </div>

      {outline.length > 0 && (
        <div className="border-t border-gray-200 p-4 text-xs text-gray-500">
          共 {outline.length} 个标题
        </div>
      )}
    </div>
  )
}
