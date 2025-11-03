import { create } from 'zustand'

interface UserState {
  token: string | null
  user: { email: string; name?: string } | null
  setToken: (token: string | null) => void
  setUser: (user: { email: string; name?: string } | null) => void
  logout: () => void
}

export const useUserStore = create<UserState>((set) => ({
  token: localStorage.getItem('token') || null,
  user: null,
  setToken: (token) => {
    if (token) {
      localStorage.setItem('token', token)
    } else {
      localStorage.removeItem('token')
    }
    set({ token })
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, user: null })
  },
}))
