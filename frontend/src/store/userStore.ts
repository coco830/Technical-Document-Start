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
        if (token) {
          set({ token, isAuthenticated: true })
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
