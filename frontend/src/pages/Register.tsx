import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, Link } from 'react-router-dom'
import api from '@/utils/api'

interface RegisterForm {
  name: string
  email: string
  password: string
  confirm_password: string
  accept_terms: boolean
}

export default function Register() {
  const { register, handleSubmit, formState: { errors }, setError, watch } = useForm<RegisterForm>()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [showTermsModal, setShowTermsModal] = useState(false)

  // 监听密码字段用于确认密码验证
  const password = watch('password')

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true)
    try {
      await api.post('/auth/register', data)

      // 注册成功，跳转到登录页
      alert('注册成功！请登录您的账号')
      navigate('/login')
    } catch (error: any) {
      console.error('注册失败:', error)

      // 显示具体错误信息
      const errorMessage = error.response?.data?.detail || '注册失败，请稍后重试'
      setError('root', {
        type: 'manual',
        message: errorMessage
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center px-4 py-8">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        {/* Logo和标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">
            🌿 悦恩平台
          </h1>
          <p className="text-gray-600">创建您的账号</p>
        </div>

        {/* 注册表单 */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          {/* 全局错误提示 */}
          {errors.root && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {errors.root.message}
            </div>
          )}

          {/* 姓名输入 */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              姓名
            </label>
            <input
              id="name"
              {...register('name', {
                required: '请输入您的姓名',
                minLength: {
                  value: 2,
                  message: '姓名至少需要2个字符'
                },
                maxLength: {
                  value: 50,
                  message: '姓名不能超过50个字符'
                }
              })}
              type="text"
              autoComplete="name"
              className={`block w-full px-4 py-3 border ${
                errors.name ? 'border-red-300' : 'border-gray-300'
              } rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition`}
              placeholder="您的姓名"
              disabled={isLoading}
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <span className="mr-1">⚠</span> {errors.name.message}
              </p>
            )}
          </div>

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
                  },
                  pattern: {
                    value: /^(?=.*[A-Za-z])(?=.*\d).+$/,
                    message: '密码必须包含字母和数字'
                  }
                })}
                type={showPassword ? 'text' : 'password'}
                autoComplete="new-password"
                className={`block w-full px-4 py-3 pr-12 border ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                } rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition`}
                placeholder="至少6位，包含字母和数字"
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

          {/* 确认密码输入 */}
          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-2">
              确认密码
            </label>
            <div className="relative">
              <input
                id="confirm_password"
                {...register('confirm_password', {
                  required: '请再次输入密码',
                  validate: (value) => value === password || '两次输入的密码不一致'
                })}
                type={showConfirmPassword ? 'text' : 'password'}
                autoComplete="new-password"
                className={`block w-full px-4 py-3 pr-12 border ${
                  errors.confirm_password ? 'border-red-300' : 'border-gray-300'
                } rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition`}
                placeholder="再次输入密码"
                disabled={isLoading}
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                tabIndex={-1}
              >
                {showConfirmPassword ? (
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
            {errors.confirm_password && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <span className="mr-1">⚠</span> {errors.confirm_password.message}
              </p>
            )}
          </div>

          {/* 服务条款复选框 */}
          <div>
            <label className="flex items-start">
              <input
                {...register('accept_terms', {
                  required: '请阅读并同意服务条款和隐私政策'
                })}
                type="checkbox"
                className="mt-1 h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary focus:ring-2"
                disabled={isLoading}
              />
              <span className="ml-2 text-sm text-gray-600">
                我已阅读并同意{' '}
                <button
                  type="button"
                  onClick={() => setShowTermsModal(true)}
                  className="text-primary hover:underline font-medium focus:outline-none focus:underline"
                >
                  服务条款
                </button>
                {' '}和{' '}
                <button
                  type="button"
                  onClick={() => setShowTermsModal(true)}
                  className="text-primary hover:underline font-medium focus:outline-none focus:underline"
                >
                  隐私政策
                </button>
              </span>
            </label>
            {errors.accept_terms && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <span className="mr-1">⚠</span> {errors.accept_terms.message}
              </p>
            )}
          </div>

          {/* 注册按钮 */}
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
                注册中...
              </span>
            ) : (
              '注册账号'
            )}
          </button>
        </form>

        {/* 登录链接 */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            已有账号？{' '}
            <Link
              to="/login"
              className="text-primary font-medium hover:underline focus:outline-none focus:underline"
            >
              立即登录
            </Link>
          </p>
        </div>
      </div>

      {/* 服务条款和隐私政策模态框 */}
      {showTermsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">服务条款与隐私政策</h2>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh] text-sm text-gray-700 space-y-4">
              <section>
                <h3 className="font-bold text-lg mb-2">一、服务条款</h3>
                <p>1. 欢迎使用悦恩人机共写平台（以下简称"本平台"）。</p>
                <p>2. 用户在使用本平台服务前，应当仔细阅读本协议，充分理解各项条款内容。</p>
                <p>3. 用户注册成功后，即表示用户同意遵守本协议的全部约定。</p>
                <p>4. 用户应当保证注册信息的真实性、准确性和完整性，并及时更新注册信息。</p>
                <p>5. 用户对使用本平台账号和密码进行的一切活动承担全部责任。</p>
              </section>

              <section>
                <h3 className="font-bold text-lg mb-2">二、用户权利与义务</h3>
                <p>1. 用户有权使用本平台提供的环保文档智能创作服务。</p>
                <p>2. 用户应当遵守中华人民共和国相关法律法规，不得利用本平台从事违法违规活动。</p>
                <p>3. 用户不得恶意攻击、破坏本平台的正常运营。</p>
                <p>4. 用户创作的内容版权归用户所有，但授予本平台非独占性使用权。</p>
              </section>

              <section>
                <h3 className="font-bold text-lg mb-2">三、隐私政策</h3>
                <p>1. 本平台重视用户隐私保护，采取业界标准的安全措施保护用户信息。</p>
                <p>2. 我们收集的信息包括：注册信息（姓名、邮箱）、使用记录、创作内容等。</p>
                <p>3. 用户信息的使用范围：</p>
                <ul className="list-disc list-inside ml-4">
                  <li>提供和改进服务</li>
                  <li>用户身份验证</li>
                  <li>数据统计和分析</li>
                  <li>法律法规要求的其他用途</li>
                </ul>
                <p>4. 我们不会将用户信息出售给第三方，但可能在以下情况共享：</p>
                <ul className="list-disc list-inside ml-4">
                  <li>获得用户明确同意</li>
                  <li>法律法规要求</li>
                  <li>保护本平台及用户的合法权益</li>
                </ul>
              </section>

              <section>
                <h3 className="font-bold text-lg mb-2">四、数据安全</h3>
                <p>1. 用户密码采用bcrypt加密存储，平台无法获取用户明文密码。</p>
                <p>2. 数据传输采用HTTPS加密协议。</p>
                <p>3. 建议用户定期更换密码，使用强密码策略。</p>
              </section>

              <section>
                <h3 className="font-bold text-lg mb-2">五、免责声明</h3>
                <p>1. 本平台不对用户创作内容的准确性、完整性、合法性承担责任。</p>
                <p>2. 因不可抗力、系统维护等原因造成的服务中断，本平台不承担责任。</p>
                <p>3. 用户因违反本协议造成的一切后果由用户自行承担。</p>
              </section>

              <section className="text-gray-500 text-xs">
                <p>本协议最后更新日期：2025年1月</p>
                <p>如有疑问，请联系：support@yueen-platform.com</p>
              </section>
            </div>
            <div className="p-6 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setShowTermsModal(false)}
                className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 transition"
              >
                我已了解
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
