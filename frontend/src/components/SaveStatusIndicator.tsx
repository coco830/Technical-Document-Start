interface SaveStatusIndicatorProps {
  status: 'saved' | 'saving' | 'unsaved' | 'error'
  lastSaved: Date | null
}

export default function SaveStatusIndicator({ status, lastSaved }: SaveStatusIndicatorProps) {
  const getStatusText = () => {
    switch (status) {
      case 'saving':
        return '保存中...'
      case 'saved':
        if (lastSaved) {
          const now = new Date()
          const diff = Math.floor((now.getTime() - lastSaved.getTime()) / 1000)
          if (diff < 60) return '刚刚保存'
          if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前保存`
          return `${Math.floor(diff / 3600)} 小时前保存`
        }
        return '已保存'
      case 'unsaved':
        return '有未保存的更改'
      case 'error':
        return '保存失败'
      default:
        return ''
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'saving':
        return <span className="animate-spin">⟳</span>
      case 'saved':
        return <span className="text-green-600">✓</span>
      case 'unsaved':
        return <span className="text-yellow-600">●</span>
      case 'error':
        return <span className="text-red-600">✕</span>
      default:
        return null
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'saving':
        return 'text-blue-600'
      case 'saved':
        return 'text-gray-600'
      case 'unsaved':
        return 'text-yellow-700'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  return (
    <div className={`flex items-center gap-2 text-sm ${getStatusColor()}`}>
      {getStatusIcon()}
      <span>{getStatusText()}</span>
    </div>
  )
}
