import { useNavigate } from 'react-router-dom'
import Layout from '@/components/Layout'

export default function Dashboard() {
  const navigate = useNavigate()

  return (
    <Layout title="工作台">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold mb-2">项目管理</h3>
          <p className="text-gray-600 mb-4">创建和管理您的环保文书项目</p>
          <button
            onClick={() => navigate('/projects')}
            className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
          >
            进入
          </button>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold mb-2">AI 编辑器</h3>
          <p className="text-gray-600 mb-4">使用AI辅助创作应急预案</p>
          <button
            onClick={() => navigate('/editor')}
            className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
          >
            进入
          </button>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
          <h3 className="text-xl font-semibold mb-2">模板库</h3>
          <p className="text-gray-600 mb-4">浏览和使用标准化文档模板</p>
          <button
            onClick={() => navigate('/templates')}
            className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
          >
            进入
          </button>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow border-l-4 border-blue-500">
          <h3 className="text-xl font-semibold mb-2">企业信息收集</h3>
          <p className="text-gray-600 mb-4">收集企业基本信息，为应急预案AI撰写提供数据支持</p>
          <button
            onClick={() => navigate('/enterprise-info')}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            进入
          </button>
        </div>
      </div>
    </Layout>
  )
}
