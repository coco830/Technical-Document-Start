import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email: string
  name: string
  is_active: boolean
  is_verified: boolean
  created_at: string
}

interface UserState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  setToken: (token: string | null) => void
  setUser: (user: User | null) => void
  logout: () => void
  initializeAuth: () => void
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      setToken: (token) => {
        if (token) {
          localStorage.setItem('token', token)
          set({ token, isAuthenticated: true })
        } else {
          localStorage.removeItem('token')
          set({ token, isAuthenticated: false })
        }
      },
      setUser: (user) => set({ user }),
      logout: () => {
        localStorage.removeItem('token')
        set({ token: null, user: null, isAuthenticated: false })
      },
      initializeAuth: () => {
        const token = localStorage.getItem('token')
        console.log('🔍 初始化认证状态，token:', token ? `${token.substring(0, 20)}...` : 'null')
        
        if (token) {
          // 验证token格式（简单的JWT格式检查）
          try {
            const parts = token.split('.')
            if (parts.length === 3) {
              // 尝试解析payload部分（不验证签名，只检查格式）
              const payload = JSON.parse(atob(parts[1]))
              const now = Math.floor(Date.now() / 1000)
              
              if (payload.exp && payload.exp > now) {
                console.log('✅ Token格式正确且未过期')
                set({ token, isAuthenticated: true })
              } else {
                console.log('⚠️ Token已过期，清除认证状态')
                localStorage.removeItem('token')
                set({ token: null, isAuthenticated: false })
              }
            } else {
              console.log('⚠️ Token格式错误，清除认证状态')
              localStorage.removeItem('token')
              set({ token: null, isAuthenticated: false })
            }
          } catch (error) {
            console.log('⚠️ Token解析失败，清除认证状态:', error)
            localStorage.removeItem('token')
            set({ token: null, isAuthenticated: false })
          }
        }
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
)
