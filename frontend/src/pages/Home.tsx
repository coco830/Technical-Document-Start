import { useNavigate } from 'react-router-dom'

export default function Home() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
      <div className="text-center">
        <div className="mb-8">
          <h1 className="text-6xl font-bold text-primary mb-4">
            🌿 Yueen Platform
          </h1>
          <p className="text-2xl text-gray-700 mb-2">
            悦恩人机共写平台
          </p>
          <div className="inline-block bg-green-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
            ✓ System Running
          </div>
        </div>

        <div className="space-y-4 mt-12">
          <p className="text-gray-600 text-lg">环保文书 AI 智能创作系统</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => navigate('/login')}
              className="bg-primary text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
            >
              登录
            </button>
            <button
              onClick={() => navigate('/register')}
              className="bg-white text-primary px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors font-semibold border-2 border-primary"
            >
              注册
            </button>
          </div>
        </div>

        <div className="mt-16 text-sm text-gray-500">
          <p>Version 2.1.0 | Powered by FastAPI + React + AI</p>
        </div>
      </div>
    </div>
  )
}
