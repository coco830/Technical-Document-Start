import React, { useState } from 'react'
import { apiClient } from '@/utils/api'

interface SectionResponse {
  chapter_id: string
  section_id: string
  title: string
}

interface GenerateSectionResponse {
  section: SectionResponse
  prompt: string
}

interface ErrorResponse {
  detail: string
}

const TemplateEngineTest: React.FC = () => {
  const [chapterId, setChapterId] = useState<string>('2')
  const [sectionId, setSectionId] = useState<string>('2.1')
  const [enterpriseData, setEnterpriseData] = useState<string>(`{
  "enterprise_name": "示例化工有限公司",
  "establish_date": "2010-05-15",
  "registered_capital": "5000万元",
  "employee_count": 120,
  "main_products": "有机溶剂、化工原料",
  "business_scope": "化工产品生产、销售",
  "address": "XX省XX市XX区XX街道XX号",
  "longitude": 120.123456,
  "latitude": 30.654321,
  "transportation": "靠近XX高速公路，交通便利",
  "surrounding_roads": "东侧为XX路，南侧为XX大道",
  "terrain_type": "平原",
  "elevation": "45米",
  "topography_description": "地势平坦，无明显起伏",
  "climate_type": "亚热带季风气候",
  "annual_temperature": "16-18℃",
  "annual_rainfall": "1200毫米",
  "prevailing_wind": "东南风",
  "extreme_weather": "台风、暴雨",
  "nearby_rivers": "东侧1公里有XX河",
  "groundwater_depth": "5-8米",
  "water_quality": "III类水质",
  "flood_risk": "较低",
  "surrounding_environment": "周边有居民区、商业区",
  "env_sensitivity": "中等",
  "nearby_residents": "约5000人",
  "env_receptors": [
    {
      "环境要素": "大气环境",
      "环境保护目标": "居民区",
      "相对方位": "西侧",
      "距离": "500米",
      "功能规模": "5000人",
      "环境质量目标": "二级"
    },
    {
      "环境要素": "水环境",
      "环境保护目标": "XX河",
      "相对方位": "东侧",
      "距离": "1000米",
      "功能规模": "III类水体",
      "环境质量目标": "III类"
    }
  ],
  "env_management_system": "ISO14001环境管理体系认证",
  "pollution_control_facilities": "废水处理站、废气处理装置",
  "env_monitoring": "定期监测废水、废气排放",
  "env_incidents": "近三年无环境事故",
  "plant_layout": "生产区、仓储区、办公区分区明确",
  "production_facilities": "反应釜3台，蒸馏塔2座",
  "storage_facilities": "原料罐区500立方米，成品仓库2000平方米",
  "waste_facilities": "危废暂存间100平方米",
  "safety_zones": "设置了安全距离和防护区域",
  "emergency_types": [
    {
      "type": "化学品泄漏",
      "principle": "迅速控制泄漏源，防止扩散",
      "steps": [
        "立即停止相关作业",
        "启动应急泵收集泄漏物",
        "使用吸附材料处理",
        "通知环保部门"
      ]
    },
    {
      "type": "火灾爆炸",
      "principle": "人员安全第一，控制火势蔓延",
      "steps": [
        "立即报警并启动应急预案",
        "组织人员疏散",
        "使用灭火器材初期灭火",
        "切断相关区域电源"
      ]
    }
  ],
  "key_equipment": [
    {
      "name": "反应釜",
      "procedures": [
        "立即停止进料",
        "关闭加热系统",
        "启动冷却系统",
        "打开紧急排放阀"
      ]
    },
    {
      "name": "蒸馏塔",
      "procedures": [
        "停止进料和出料",
        "关闭加热系统",
        "启动回流冷却",
        "监控压力变化"
      ]
    }
  ],
  "evacuation_routes": [
    {
      "route": "生产区东门",
      "destination": "紧急集合点A"
    },
    {
      "route": "办公区南门",
      "destination": "紧急集合点B"
    }
  ],
  "emergency_supplies": [
    {
      "name": "吸附棉",
      "quantity": "200公斤",
      "location": "应急物资库"
    },
    {
      "name": "防化服",
      "quantity": "20套",
      "location": "应急物资库"
    }
  ],
  "medical_resources": [
    {
      "type": "医院",
      "provider": "XX市第一人民医院",
      "phone": "120",
      "distance": "5公里"
    }
  ],
  "external_support": [
    {
      "organization": "XX市消防救援支队",
      "capability": "化学品事故处置",
      "contact": "119"
    }
  ],
  "stakeholders": [
    "员工",
    "周边居民",
    "政府部门",
    "媒体"
  ],
  "communication_channels": [
    "内部广播系统",
    "短信平台",
    "微信公众号",
    "新闻发布会"
  ],
  "key_messages": [
    "事故情况通报",
    "疏散通知",
    "环境影响评估",
    "处置进展更新"
  ]
}`)
  
  const [result, setResult] = useState<GenerateSectionResponse | null>(null)
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const handleGeneratePrompt = async () => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // 解析企业数据JSON
      let parsedEnterpriseData
      try {
        parsedEnterpriseData = JSON.parse(enterpriseData)
      } catch (jsonError) {
        setError('企业数据JSON格式错误，请检查格式')
        setLoading(false)
        return
      }

      // 发送请求到后端
      const response = await apiClient.post<GenerateSectionResponse>('/debug/generate_section', {
        chapter_id: chapterId,
        section_id: sectionId,
        enterprise_data: parsedEnterpriseData
      })

      setResult(response.data)
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError('找不到指定的章节模板，请检查章节ID和小节ID是否正确')
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail)
      } else {
        setError('生成Prompt失败，请稍后重试')
      }
      console.error('生成Prompt错误:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h1 className="text-2xl font-bold text-gray-900">模板引擎测试工具</h1>
            <p className="mt-1 text-sm text-gray-600">
              测试模板引擎和Prompt生成功能，用于调试应急预案章节生成
            </p>
          </div>

          <div className="px-6 py-4 space-y-6">
            {/* 章节ID输入 */}
            <div>
              <label htmlFor="chapter_id" className="block text-sm font-medium text-gray-700">
                章节ID
              </label>
              <input
                type="text"
                id="chapter_id"
                value={chapterId}
                onChange={(e) => setChapterId(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border"
                placeholder="例如: 2"
              />
              <p className="mt-1 text-xs text-gray-500">
                可用章节: 2 (企业基本情况), 3 (应急响应)
              </p>
            </div>

            {/* 小节ID输入 */}
            <div>
              <label htmlFor="section_id" className="block text-sm font-medium text-gray-700">
                小节ID
              </label>
              <input
                type="text"
                id="section_id"
                value={sectionId}
                onChange={(e) => setSectionId(e.target.value)}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border"
                placeholder="例如: 2.1"
              />
              <p className="mt-1 text-xs text-gray-500">
                章节2可用小节: 2.1, 2.1.1, 2.1.2.1, 2.1.2.2, 2.1.2.3, 2.1.3.text, 2.1.3.table, 2.1.4, 2.1.5<br/>
                章节3可用小节: 3.1, 3.2, 3.3, 3.4
              </p>
            </div>

            {/* 企业数据输入 */}
            <div>
              <label htmlFor="enterprise_data" className="block text-sm font-medium text-gray-700">
                企业数据 (JSON格式)
              </label>
              <textarea
                id="enterprise_data"
                value={enterpriseData}
                onChange={(e) => setEnterpriseData(e.target.value)}
                rows={15}
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border font-mono text-xs"
                placeholder="请输入JSON格式的企业数据..."
              />
              <p className="mt-1 text-xs text-gray-500">
                请输入有效的JSON格式数据，包含章节所需的企业信息字段
              </p>
            </div>

            {/* 生成按钮 */}
            <div>
              <button
                onClick={handleGeneratePrompt}
                disabled={loading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '生成中...' : '生成Prompt'}
              </button>
            </div>

            {/* 错误信息 */}
            {error && (
              <div className="rounded-md bg-red-50 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">错误</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>{error}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 结果显示 */}
            {result && (
              <div className="space-y-4">
                <div className="border-t border-gray-200 pt-4">
                  <h2 className="text-lg font-medium text-gray-900">章节信息</h2>
                  <div className="mt-2 bg-gray-50 p-3 rounded-md">
                    <p><strong>章节ID:</strong> {result.section.chapter_id}</p>
                    <p><strong>小节ID:</strong> {result.section.section_id}</p>
                    <p><strong>标题:</strong> {result.section.title}</p>
                  </div>
                </div>

                <div>
                  <h2 className="text-lg font-medium text-gray-900">生成的Prompt</h2>
                  <div className="mt-2 bg-gray-50 p-3 rounded-md">
                    <pre className="whitespace-pre-wrap text-sm text-gray-800">{result.prompt}</pre>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default TemplateEngineTest