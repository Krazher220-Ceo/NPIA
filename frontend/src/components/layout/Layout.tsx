import { ReactNode, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Factory, 
  BarChart3,
  Activity,
  LogOut,
  CreditCard,
  Cog,
  FileText,
  Link as LinkIcon,
  Moon,
  Sun
} from 'lucide-react'
import { authService } from '../../services/authService'
import { useTheme } from '../../hooks/useTheme'
import toast from 'react-hot-toast'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()
  const currentYear = new Date().getFullYear()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  const handleLogout = () => {
    authService.logout()
    toast.success('Выход выполнен')
    // Редирект на внешний лендинг для входа
    window.location.href = 'http://localhost:5173/login.html'
  }

  const navItems = [
    { path: '/', label: 'Главная', icon: LayoutDashboard },
    { path: '/factories', label: 'Заводы', icon: Factory },
    { path: '/equipment', label: 'Оборудование', icon: Activity },
    { path: '/analytics', label: 'Аналитика', icon: BarChart3 },
    { path: '/production', label: 'Производство', icon: Cog },
    { path: '/reports', label: 'Отчеты', icon: FileText },
    { path: '/subscriptions', label: 'Подписки', icon: CreditCard },
    { path: '/integrations', label: 'Интеграции', icon: LinkIcon },
  ]

  // Добавляем админ-меню если пользователь админ
  const user = authService.getCurrentUserSync()
  if (user?.role === 'admin') {
    navItems.push({ path: '/admin/applications', label: 'Заявки', icon: FileText })
    navItems.push({ path: '/admin/ips', label: 'ИП', icon: Factory })
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors flex flex-col">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                🏭 Промышленная аналитика Казахстана
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleTheme}
                className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                aria-label="Переключить тему"
              >
                {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                Выход
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="w-64 bg-white dark:bg-gray-800 shadow-sm min-h-[calc(100vh-4rem)] transition-colors">
          <nav className="p-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 dark:bg-primary-900 text-primary-700 dark:text-primary-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 bg-gray-50 dark:bg-gray-900 transition-colors">
          {children}
        </main>
      </div>
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-sm text-gray-600 dark:text-gray-300">
          <span>© {currentYear} Национальная платформа промышленной аналитики. Проект распространяется под лицензией MIT.</span>
          <a
            href="https://github.com/Krazher220-Ceo/NPIA"
            target="_blank"
            rel="noreferrer"
            className="text-primary-600 dark:text-primary-300 hover:underline"
          >
            Открыть репозиторий на GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}

