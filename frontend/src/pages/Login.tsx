import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/store/userStore'
import axios from 'axios'

interface LoginForm {
  email: string
  password: string
}

export default function Login() {
  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>()
  const navigate = useNavigate()
  const setToken = useUserStore((state) => state.setToken)

  const onSubmit = async (data: LoginForm) => {
    try {
      const res = await axios.post('/api/auth/login', data)
      setToken(res.data.token)
      navigate('/dashboard')
    } catch (error) {
      console.error('登录失败:', error)
      alert('登录失败，请检查邮箱和密码')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-primary">
          悦恩人机共写平台
        </h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">邮箱</label>
            <input
              {...register('email', { required: '请输入邮箱' })}
              type="email"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="your@email.com"
            />
            {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">密码</label>
            <input
              {...register('password', { required: '请输入密码' })}
              type="password"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>}
          </div>
          <button
            type="submit"
            className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            登录
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          还没有账号？{' '}
          <a href="/register" className="text-primary hover:underline">
            立即注册
          </a>
        </p>
      </div>
    </div>
  )
}
