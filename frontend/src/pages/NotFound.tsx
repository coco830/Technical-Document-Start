import { useNavigate } from 'react-router-dom'

export default function NotFound() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-primary mb-4">404</h1>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">页面未找到</h2>
          <p className="text-lg text-gray-600 mb-8">
            抱歉，您访问的页面不存在或已被移动。
          </p>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => navigate(-1)}
            className="block w-full bg-white text-primary px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors font-semibold border-2 border-primary"
          >
            返回上一页
          </button>
          <button
            onClick={() => navigate('/')}
            className="block w-full bg-primary text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
          >
            返回首页
          </button>
        </div>

        <div className="mt-12 text-sm text-gray-500">
          <p>如果您认为这是一个错误，请联系我们的技术支持。</p>
        </div>
      </div>
    </div>
  )
}