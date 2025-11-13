import { Routes, Route } from 'react-router-dom'
import { authService } from './services/authService'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Factories from './pages/Factories'
import Equipment from './pages/Equipment'
import Analytics from './pages/Analytics'
import Subscriptions from './pages/Subscriptions'
import Production from './pages/Production'
import Reports from './pages/Reports'
import Integrations from './pages/Integrations'
import Apply from './pages/Apply'
import AdminApplications from './pages/AdminApplications'
import AdminIPs from './pages/AdminIPs'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  // Проверяем авторизацию
  const isAuth = authService.isAuthenticated();
  
  if (!isAuth) {
    // Редирект на отдельную страницу входа только если действительно не авторизован
    // Определяем порт для редиректа
    const currentPort = window.location.port || '5173';
    const loginPort = currentPort === '4173' ? '4173' : '5173';
    window.location.href = `http://${window.location.hostname}:${loginPort}/login.html`;
    return null;
  }
  
  return <Layout>{children}</Layout>;
}

function App() {
  return (
    <Routes>
      <Route path="/apply" element={<Apply />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/factories"
        element={
          <ProtectedRoute>
            <Factories />
          </ProtectedRoute>
        }
      />
      <Route
        path="/equipment"
        element={
          <ProtectedRoute>
            <Equipment />
          </ProtectedRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        }
      />
      <Route
        path="/subscriptions"
        element={
          <ProtectedRoute>
            <Subscriptions />
          </ProtectedRoute>
        }
      />
      <Route
        path="/production"
        element={
          <ProtectedRoute>
            <Production />
          </ProtectedRoute>
        }
      />
      <Route
        path="/reports"
        element={
          <ProtectedRoute>
            <Reports />
          </ProtectedRoute>
        }
      />
      <Route
        path="/integrations"
        element={
          <ProtectedRoute>
            <Integrations />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/applications"
        element={
          <ProtectedRoute>
            <AdminApplications />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/ips"
        element={
          <ProtectedRoute>
            <AdminIPs />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}

export default App

