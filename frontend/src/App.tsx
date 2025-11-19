import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Templates from './pages/Templates'
import ProjectDetail from './pages/ProjectDetail'
import ProjectEnterprise from './pages/ProjectEnterprise'
import TemplateEngineTest from './pages/TemplateEngineTest'
import AuthTest from './pages/AuthTest'
import Editor from './pages/Editor'
import AIGenerate from './pages/AIGenerate'
import Export from './pages/Export'
import DataCenter from './pages/DataCenter'
import NotFound from './pages/NotFound'
import Unauthorized from './pages/Unauthorized'
import AuthProvider from './providers/AuthProvider'
import ProtectedRoute from './components/ProtectedRoute'
import RouteGuard from './components/RouteGuard'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* 公开路由 - 使用RouteGuard处理已认证用户访问登录/注册页的重定向 */}
          <Route path="/" element={
            <RouteGuard>
              <Home />
            </RouteGuard>
          } />
          <Route path="/login" element={
            <RouteGuard>
              <Login />
            </RouteGuard>
          } />
          <Route path="/register" element={
            <RouteGuard>
              <Register />
            </RouteGuard>
          } />
          
          {/* 受保护的路由 - 使用ProtectedRoute和RouteGuard双重保护 */}
          <Route path="/dashboard" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/projects" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <Projects />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/templates" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <Templates />
              </ProtectedRoute>
            </RouteGuard>
          } />

          {/* 项目内部路由 */}
          <Route path="/project/:id" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <ProjectDetail />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/enterprise" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <ProjectEnterprise />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/enterprise/:step" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <ProjectEnterprise />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/ai-generate" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <AIGenerate />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/ai-generate/:step" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <AIGenerate />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/editor" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <Editor />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/export" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <Export />
              </ProtectedRoute>
            </RouteGuard>
          } />
          <Route path="/project/:id/export/:format" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <Export />
              </ProtectedRoute>
            </RouteGuard>
          } />

          {/* 保留模板引擎测试路由 */}
          <Route path="/template-engine-test" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <TemplateEngineTest />
              </ProtectedRoute>
            </RouteGuard>
          } />

          {/* 认证测试路由 */}
          <Route path="/auth-test" element={
            <RouteGuard requireAuth={true}>
              <ProtectedRoute>
                <AuthTest />
              </ProtectedRoute>
            </RouteGuard>
          } />

          {/* 无权限页面 */}
          <Route path="/unauthorized" element={<Unauthorized />} />
          
          {/* 404 页面 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
