import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { apiClient } from '@/utils/api'
import Layout from '@/components/Layout'

interface CompanyInfo {
  id: number
  name: string
  industry: string
  address: string
  created_at: string
}

interface Template {
  id: number
  name: string
  description: string
  category: string
  usage_count: number
  created_at: string
}

export default function DataCenter() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get('tab') || 'companies'

  const [companies, setCompanies] = useState<CompanyInfo[]>([])
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    try {
      setLoading(true)

      if (activeTab === 'companies') {
        const res = await apiClient.get('/enterprise/info')
        setCompanies(res.data || [])
      } else {
        const res = await apiClient.get('/templates/')
        setTemplates(res.data || [])
      }
    } catch (error) {
      console.error('获取数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTabChange = (tab: string) => {
    setSearchParams({ tab })
  }

  if (loading) {
    return (
      <Layout title="数据中心">
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">加载中...</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout title="数据中心">
      <div className="max-w-6xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">📊 数据中心</h1>
          <p className="text-gray-600">管理企业信息库和预案模板库</p>
        </div>

        {/* 标签页导航 */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => handleTabChange('companies')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'companies'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🏢 企业信息库
            </button>
            <button
              onClick={() => handleTabChange('templates')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'templates'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📋 预案模板库
            </button>
          </nav>
        </div>

        {/* 企业信息库 */}
        {activeTab === 'companies' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">
                企业信息库 ({companies.length})
              </h2>
              <button
                onClick={() => navigate('/enterprise-info')}
                className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                添加企业信息
              </button>
            </div>

            {companies.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="text-4xl mb-4">🏢</div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">暂无企业信息</h3>
                <p className="text-gray-600 mb-4">开始添加企业信息，为预案生成提供数据支持</p>
                <button
                  onClick={() => navigate('/enterprise-info')}
                  className="bg-primary text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  添加第一个企业信息
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {companies.map((company) => (
                  <div key={company.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                    <h3 className="font-semibold text-gray-800 mb-2">{company.name}</h3>
                    <div className="space-y-1 text-sm text-gray-600">
                      <p>🏭 行业: {company.industry}</p>
                      <p>📍 地址: {company.address}</p>
                      <p>📅 创建时间: {new Date(company.created_at).toLocaleDateString('zh-CN')}</p>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => navigate(`/enterprise-info/${company.id}`)}
                        className="flex-1 border border-gray-300 text-gray-700 px-3 py-1.5 rounded-md hover:bg-gray-50 transition-colors text-sm"
                      >
                        查看详情
                      </button>
                      <button
                        onClick={() => navigate(`/enterprise-info?edit=${company.id}`)}
                        className="flex-1 bg-primary text-white px-3 py-1.5 rounded-md hover:bg-green-700 transition-colors text-sm"
                      >
                        编辑
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 预案模板库 */}
        {activeTab === 'templates' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-800">
                预案模板库 ({templates.length})
              </h2>
              <button
                onClick={() => navigate('/templates')}
                className="bg-primary text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                管理模板
              </button>
            </div>

            {templates.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <div className="text-4xl mb-4">📋</div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">暂无预案模板</h3>
                <p className="text-gray-600 mb-4">添加预案模板，为AI生成提供标准格式</p>
                <button
                  onClick={() => navigate('/templates')}
                  className="bg-primary text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  添加第一个模板
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <div key={template.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                    <h3 className="font-semibold text-gray-800 mb-2">{template.name}</h3>
                    <p className="text-sm text-gray-600 mb-4 line-clamp-2">{template.description}</p>
                    <div className="space-y-1 text-sm text-gray-600 mb-4">
                      <p>📁 分类: {template.category}</p>
                      <p>📈 使用次数: {template.usage_count}</p>
                      <p>📅 创建时间: {new Date(template.created_at).toLocaleDateString('zh-CN')}</p>
                    </div>
                    <div className="mt-4 flex gap-2">
                      <button
                        onClick={() => navigate(`/templates/${template.id}`)}
                        className="flex-1 border border-gray-300 text-gray-700 px-3 py-1.5 rounded-md hover:bg-gray-50 transition-colors text-sm"
                      >
                        查看详情
                      </button>
                      <button
                        onClick={() => navigate(`/ai-generate?template=${template.id}`)}
                        className="flex-1 bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700 transition-colors text-sm"
                      >
                        使用模板
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 统计信息 */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">📈 数据统计</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{companies.length}</div>
              <div className="text-sm text-blue-800">企业信息</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{templates.length}</div>
              <div className="text-sm text-green-800">预案模板</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {templates.reduce((sum, t) => sum + t.usage_count, 0)}
              </div>
              <div className="text-sm text-purple-800">模板使用次数</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">--</div>
              <div className="text-sm text-yellow-800">本月新增</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}