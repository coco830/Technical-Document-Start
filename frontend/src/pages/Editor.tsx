import { useParams, useNavigate } from 'react-router-dom'

export default function Editor() {
  const { id } = useParams()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1
                className="text-2xl font-bold text-primary cursor-pointer"
                onClick={() => navigate('/dashboard')}
              >
                悦恩人机共写平台
              </h1>
              <span className="ml-4 text-gray-600">
                {id ? `项目 #${id}` : '新建文档'}
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <button className="text-gray-700 hover:text-primary px-3 py-2">
                保存
              </button>
              <button className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700">
                生成文档
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-4">AI 协作编辑器</h2>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
              <p className="text-gray-500 text-lg">编辑器功能开发中...</p>
              <p className="text-gray-400 mt-2">将支持富文本编辑和AI辅助写作</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
