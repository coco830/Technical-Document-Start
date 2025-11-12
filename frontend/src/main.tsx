import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import { useUserStore } from './store/userStore'
import './index.css'

// 在应用启动时初始化认证状态
const initializeApp = () => {
  const { initializeAuth } = useUserStore.getState()
  initializeAuth()
}

// 初始化应用
initializeApp()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
