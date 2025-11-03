import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface RegisterForm {
  name: string
  email: string
  password: string
  confirmPassword: string
}

export default function Register() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterForm>()
  const navigate = useNavigate()
  const password = watch('password')

  const onSubmit = async (data: RegisterForm) => {
    try {
      await axios.post('/api/auth/register', {
        name: data.name,
        email: data.email,
        password: data.password,
      })
      alert('注册成功！请登录')
      navigate('/login')
    } catch (error) {
      console.error('注册失败:', error)
      alert('注册失败，请重试')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-primary">
          注册新账号
        </h2>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">姓名</label>
            <input
              {...register('name', { required: '请输入姓名' })}
              type="text"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="您的姓名"
            />
            {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>}
          </div>
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
              {...register('password', { required: '请输入密码', minLength: { value: 6, message: '密码至少6位' } })}
              type="password"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">确认密码</label>
            <input
              {...register('confirmPassword', {
                required: '请确认密码',
                validate: value => value === password || '两次密码不一致'
              })}
              type="password"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              placeholder="••••••••"
            />
            {errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword.message}</p>}
          </div>
          <button
            type="submit"
            className="w-full bg-primary text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            注册
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-600">
          已有账号？{' '}
          <a href="/login" className="text-primary hover:underline">
            立即登录
          </a>
        </p>
      </div>
    </div>
  )
}
