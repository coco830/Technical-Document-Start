import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { devtools } from 'zustand/middleware'
import { User, Theme } from '@/types'
import { STORAGE_KEYS } from '@/lib/constants'

// 用户状态接口
interface UserState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  lastActivity: number | null
  sessionTimeout: number | null
  login: (user: User, accessToken?: string, refreshToken?: string) => void
  logout: (force?: boolean) => void
  updateUser: (user: Partial<User>) => void
  setLoading: (loading: boolean) => void
  updateLastActivity: () => void
  checkSessionTimeout: () => boolean
  refreshSession: () => Promise<boolean>
}

// 创建用户状态store
export const useUserStore = create<UserState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        lastActivity: null,
        sessionTimeout: null, // 默认会话超时时间（毫秒）
        
        login: (user, accessToken, refreshToken) => {
          const now = Date.now()
          // 设置会话超时时间为8小时
          const sessionTimeout = now + (8 * 60 * 60 * 1000)
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            lastActivity: now,
            sessionTimeout,
          })
          
          // 保存token到本地存储
          if (accessToken) {
            localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken)
          }
          if (refreshToken) {
            localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, refreshToken)
          }
        },
        
        logout: (force = false) => {
          const { sessionTimeout, lastActivity } = get()
          
          // 检查是否是会话超时导致的登出
          const isSessionTimeout = !force && sessionTimeout && lastActivity && Date.now() > sessionTimeout
          
          // 清除本地存储
          localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
          localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
          
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            lastActivity: null,
            sessionTimeout: null,
          })
          
          // 如果是会话超时，显示提示
          if (isSessionTimeout && typeof window !== 'undefined') {
            console.warn('会话已超时，请重新登录')
          }
        },
        
        updateUser: (userData) => {
          const currentUser = get().user
          if (currentUser) {
            set({
              user: { ...currentUser, ...userData },
              lastActivity: Date.now(),
            })
          }
        },
        
        setLoading: (loading) => {
          set({ isLoading: loading })
        },
        
        updateLastActivity: () => {
          set({ lastActivity: Date.now() })
        },
        
        checkSessionTimeout: () => {
          const { sessionTimeout, isAuthenticated } = get()
          
          // 如果未认证或没有设置超时时间，返回true
          if (!isAuthenticated || !sessionTimeout) {
            return true
          }
          
          // 检查是否超时
          const now = Date.now()
          const isExpired = now > sessionTimeout
          
          if (isExpired) {
            get().logout(true) // 强制登出
          }
          
          return !isExpired
        },
        
        refreshSession: async () => {
          const { isAuthenticated } = get()
          
          if (!isAuthenticated) {
            return false
          }
          
          try {
            const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN)
            
            if (!refreshToken) {
              get().logout(true)
              return false
            }
            
            // 调用API刷新token
            const response = await fetch('/api/v1/auth/refresh', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-Refresh-Token': refreshToken,
              },
            })
            
            if (response.ok) {
              const data = await response.json()
              const { access_token } = data
              
              // 更新token
              localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, access_token)
              
              // 更新会话超时时间
              const now = Date.now()
              const newSessionTimeout = now + (8 * 60 * 60 * 1000)
              
              set({
                lastActivity: now,
                sessionTimeout: newSessionTimeout,
              })
              
              return true
            } else {
              get().logout(true)
              return false
            }
          } catch (error) {
            console.error('刷新会话失败:', error)
            get().logout(true)
            return false
          }
        },
      }),
      {
        name: STORAGE_KEYS.USER_INFO,
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
          lastActivity: state.lastActivity,
          sessionTimeout: state.sessionTimeout,
        }),
      }
    ),
    {
      name: 'user-store',
    }
  )
)

// 主题状态接口
interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

// 创建主题状态store
export const useThemeStore = create<ThemeState>()(
  devtools(
    persist(
      (set, get) => ({
        theme: 'system',
        
        setTheme: (theme) => {
          set({ theme })
          // 应用主题到DOM
          if (typeof window !== 'undefined') {
            const root = window.document.documentElement
            root.classList.remove('light', 'dark')
            
            if (theme === 'system') {
              const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
                ? 'dark'
                : 'light'
              root.classList.add(systemTheme)
            } else {
              root.classList.add(theme)
            }
          }
        },
        
        toggleTheme: () => {
          const currentTheme = get().theme
          const newTheme = currentTheme === 'light' ? 'dark' : 'light'
          get().setTheme(newTheme)
        },
      }),
      {
        name: STORAGE_KEYS.THEME,
        storage: createJSONStorage(() => localStorage),
      }
    ),
    {
      name: 'theme-store',
    }
  )
)

// 应用状态接口
interface AppState {
  sidebarOpen: boolean
  notifications: Array<{
    id: string
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    read: boolean
    createdAt: string
  }>
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  addNotification: (notification: Omit<AppState['notifications'][0], 'id' | 'createdAt'>) => void
  markNotificationAsRead: (id: string) => void
  clearNotifications: () => void
}

// 创建应用状态store
export const useAppStore = create<AppState>()(
  devtools(
    (set, get) => ({
      sidebarOpen: true,
      notifications: [],
      
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }))
      },
      
      setSidebarOpen: (open) => {
        set({ sidebarOpen: open })
      },
      
      addNotification: (notification) => {
        const id = Date.now().toString()
        const createdAt = new Date().toISOString()
        
        set((state) => ({
          notifications: [
            {
              ...notification,
              id,
              createdAt,
              read: false,
            },
            ...state.notifications,
          ],
        }))
      },
      
      markNotificationAsRead: (id) => {
        set((state) => ({
          notifications: state.notifications.map((notification) =>
            notification.id === id ? { ...notification, read: true } : notification
          ),
        }))
      },
      
      clearNotifications: () => {
        set({ notifications: [] })
      },
    }),
    {
      name: 'app-store',
    }
  )
)

// 项目状态接口
interface ProjectState {
  currentProject: any | null
  projects: any[]
  isLoading: boolean
  setCurrentProject: (project: any) => void
  setProjects: (projects: any[]) => void
  addProject: (project: any) => void
  updateProject: (id: string, updates: Partial<any>) => void
  removeProject: (id: string) => void
  setLoading: (loading: boolean) => void
}

// 创建项目状态store
export const useProjectStore = create<ProjectState>()(
  devtools(
    (set, get) => ({
      currentProject: null,
      projects: [],
      isLoading: false,
      
      setCurrentProject: (project) => {
        set({ currentProject: project })
      },
      
      setProjects: (projects) => {
        set({ projects })
      },
      
      addProject: (project) => {
        set((state) => ({
          projects: [...state.projects, project],
        }))
      },
      
      updateProject: (id, updates) => {
        set((state) => ({
          projects: state.projects.map((project) =>
            project.id === id ? { ...project, ...updates } : project
          ),
          currentProject:
            state.currentProject?.id === id
              ? { ...state.currentProject, ...updates }
              : state.currentProject,
        }))
      },
      
      removeProject: (id) => {
        set((state) => ({
          projects: state.projects.filter((project) => project.id !== id),
          currentProject:
            state.currentProject?.id === id ? null : state.currentProject,
        }))
      },
      
      setLoading: (loading) => {
        set({ isLoading: loading })
      },
    }),
    {
      name: 'project-store',
    }
  )
)

// 导出所有store的类型
export type { UserState, ThemeState, AppState, ProjectState }