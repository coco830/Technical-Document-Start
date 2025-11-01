// 模拟认证API
export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterCredentials extends LoginCredentials {
  email: string
  full_name: string
}

export interface AuthUser {
  id: number
  username: string
  email: string
  full_name: string
}

export interface AuthResponse {
  access_token: {
    token: string
    expires: number
  }
  token_type: string
  user: AuthUser
}

// 模拟用户数据库
const MOCK_USERS: Record<string, { password: string; user: AuthUser }> = {
  'admin': {
    password: 'admin123',
    user: {
      id: 1,
      username: 'admin',
      email: 'admin@example.com',
      full_name: '管理员'
    }
  },
  'test': {
    password: 'test123',
    user: {
      id: 2,
      username: 'test',
      email: 'test@example.com',
      full_name: '测试用户'
    }
  },
  'demo': {
    password: 'demo123',
    user: {
      id: 3,
      username: 'demo',
      email: 'demo@example.com',
      full_name: '演示用户'
    }
  }
}

// 模拟API延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 模拟登录
export async function mockLogin(credentials: LoginCredentials): Promise<AuthResponse> {
  await delay(800) // 模拟网络延迟

  const { username, password } = credentials
  const userData = MOCK_USERS[username]

  if (!userData || userData.password !== password) {
    throw new Error('用户名或密码错误')
  }

  return {
    access_token: {
      token: `mock_token_${username}_${Date.now()}`,
      expires: Date.now() + 3600 * 1000 // 1小时
    },
    token_type: 'bearer',
    user: userData.user
  }
}

// 模拟注册
export async function mockRegister(credentials: RegisterCredentials): Promise<AuthResponse> {
  await delay(800)

  const { username, password, email, full_name } = credentials

  // 检查用户名是否已存在
  if (MOCK_USERS[username]) {
    throw new Error('用户名已存在')
  }

  // 创建新用户
  const newUser: AuthUser = {
    id: Object.keys(MOCK_USERS).length + 1,
    username,
    email,
    full_name
  }

  MOCK_USERS[username] = {
    password,
    user: newUser
  }

  return {
    access_token: {
      token: `mock_token_${username}_${Date.now()}`,
      expires: Date.now() + 3600 * 1000
    },
    token_type: 'bearer',
    user: newUser
  }
}

// 模拟登出
export async function mockLogout(): Promise<void> {
  await delay(300)
  // 清空本地存储
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }
}
