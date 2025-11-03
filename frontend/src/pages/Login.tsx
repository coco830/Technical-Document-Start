import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, Link } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'
import api from '@/utils/api'

interface LoginForm {
  email: string
  password: string
}

export default function Login() {
  const { register, handleSubmit, formState: { errors }, setError } = useForm<LoginForm>()
  const navigate = useNavigate()
  const { setToken, setUser } = useUserStore()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      const res = await api.post('/auth/login', data)

      // 保存token和用户信息
      setToken(res.data.access_token)
      setUser(res.data.user)

      // 跳转到项目页面
      navigate('/projects')
    } catch (error: any) {
      console.error('登录失败:', error)

      // 显示具体错误信息
      const errorMessage = error.response?.data?.detail || '登录失败，请检查邮箱和密码'
      setError('root', {
        type: 'manual',
        message: errorMessage
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Logo和标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">
            🌿 悦恩平台
          </h1>
          <p className="text-gray-600">人机共写智能文档平台</p>
        </div>

        {/* 登录表单 */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* 全局错误提示 */}
          {errors.root && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {errors.root.message}
            </div>
          )}

          {/* 邮箱输入 */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              邮箱地址
            </label>
            <input
              id="email"
              {...register('email', {
                required: '请输入邮箱地址',
                pattern: {
                  value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                  message: '请输入有效的邮箱地址'
                }
              })}
              type="email"
              autoComplete="email"
              className={`block w-full px-4 py-3 border ${
                errors.email ? 'border-red-300' : 'border-gray-300'
              } rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition`}
              placeholder="your@email.com"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <span className="mr-1">⚠</span> {errors.email.message}
              </p>
            )}
          </div>

          {/* 密码输入 */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <div className="relative">
              <input
                id="password"
                {...register('password', {
                  required: '请输入密码',
                  minLength: {
                    value: 6,
                    message: '密码至少需要6个字符'
                  }
                })}
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                className={`block w-full px-4 py-3 pr-12 border ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                } rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition`}
                placeholder="••••••••"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                tabIndex={-1}
              >
                {showPassword ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <span className="mr-1">⚠</span> {errors.password.message}
              </p>
            )}
          </div>

          {/* 登录按钮 */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-all ${
              isLoading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-primary hover:bg-green-700 hover:shadow-lg active:scale-[0.98]'
            } focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2`}
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                登录中...
              </span>
            ) : (
              '登录'
            )}
          </button>
        </form>

        {/* 注册链接 */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            还没有账号？{' '}
            <Link
              to="/register"
              className="text-primary font-medium hover:underline focus:outline-none focus:underline"
            >
              立即注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
