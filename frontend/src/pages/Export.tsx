import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import ProjectLayout from '@/components/ProjectLayout'

interface ExportHistory {
  id: number
  project_id: number
  project_title: string
  format: 'pdf' | 'word'
  created_at: string
  file_url?: string
}

export default function Export() {
  const navigate = useNavigate()
  const { id, format } = useParams()
  const projectId = parseInt(id || '0')
  const [exportHistory, setExportHistory] = useState<ExportHistory[]>([])
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'word'>('pdf')
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [currentView, setCurrentView] = useState<'main' | 'pdf' | 'word' | 'history'>('main')
  
  // 根据URL参数确定当前视图
  useEffect(() => {
    if (format === 'pdf') {
      setCurrentView('pdf')
      setSelectedFormat('pdf')
    } else if (format === 'word') {
      setCurrentView('word')
      setSelectedFormat('word')
    } else if (format === 'history') {
      setCurrentView('history')
    } else {
      setCurrentView('main')
    }
  }, [format])

  useEffect(() => {
    fetchExportHistory()
  }, [])

  const fetchExportHistory = async () => {
    try {
      const historyRes = await apiClient.get('/export/history/')
      // 只显示当前项目的导出历史
      const projectHistory = (historyRes.data || []).filter(
        (record: ExportHistory) => record.project_id === projectId
      )
      setExportHistory(projectHistory)
    } catch (error) {
      console.error('获取导出历史失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      setExporting(true)

      const response = await apiClient.post('/export/', {
        project_id: projectId,
        format: selectedFormat
      })

      // 导出成功后刷新历史记录
      fetchExportHistory()

      // 如果返回了文件URL，直接下载
      if (response.data.file_url) {
        window.open(response.data.file_url, '_blank')
      }
    } catch (error: any) {
      console.error('导出失败:', error)
      alert(error.response?.data?.detail || '导出失败')
    } finally {
      setExporting(false)
    }
  }

  const handleDownload = (exportRecord: ExportHistory) => {
    if (exportRecord.file_url) {
      window.open(exportRecord.file_url, '_blank')
    }
  }

  if (loading) {
    return (
      <ProjectLayout title="导出中心" projectId={projectId}>
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">加载中...</p>
        </div>
      </ProjectLayout>
    )
  }

  return (
    <ProjectLayout title="导出中心" projectId={projectId}>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* 页面标题 */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📤 导出中心</h1>
          <p className="text-gray-600">将完成的应急预案导出为PDF或Word文档</p>
        </div>

        {/* 导出配置 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">导出配置</h2>

          {/* 格式选择 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              导出格式
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="pdf"
                  checked={selectedFormat === 'pdf'}
                  onChange={(e) => setSelectedFormat(e.target.value as 'pdf' | 'word')}
                  className="mr-2"
                />
                <span>PDF文档</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="word"
                  checked={selectedFormat === 'word'}
                  onChange={(e) => setSelectedFormat(e.target.value as 'pdf' | 'word')}
                  className="mr-2"
                />
                <span>Word文档</span>
              </label>
            </div>
          </div>

          {/* 导出按钮 */}
          <button
            onClick={handleExport}
            disabled={exporting}
            className="w-full bg-primary text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {exporting ? '导出中...' : '📤 开始导出'}
          </button>
        </div>

        {/* 导出历史 */}
        {exportHistory.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">导出历史</h2>
            <div className="space-y-3">
              {exportHistory.map((record) => (
                <div
                  key={record.id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-md"
                >
                  <div>
                    <h4 className="font-medium text-gray-800">{record.project_title}</h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>格式: {record.format.toUpperCase()}</span>
                      <span>时间: {new Date(record.created_at).toLocaleString('zh-CN')}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDownload(record)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm"
                  >
                    下载
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 帮助提示 */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-800 mb-2">💡 导出提示</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• PDF格式适合打印和正式提交</li>
            <li>• Word格式适合进一步编辑</li>
            <li>• 导出文件会保存在系统中，可随时下载</li>
          </ul>
        </div>
      </div>
    </ProjectLayout>
  )
}