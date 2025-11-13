import { useQuery } from '@tanstack/react-query'
import { dashboardService } from '../services/dashboardService'
import KPICard from '../components/dashboard/KPICard'
import { TrendingUp, Activity, AlertTriangle, Zap, Factory } from 'lucide-react'
import OEEChart from '../components/charts/OEEChart'

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardService.getStats(),
    refetchInterval: 30000, // Обновление каждые 30 секунд
    retry: 1, // Повторять только 1 раз при ошибке
  })

  const { data: kpiSummary, isLoading: kpiLoading, error: kpiError } = useQuery({
    queryKey: ['dashboard-kpi'],
    queryFn: () => dashboardService.getKPISummary(7),
    retry: 1, // Повторять только 1 раз при ошибке
  })

  if (statsLoading || kpiLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 dark:text-gray-400">Загрузка...</div>
      </div>
    )
  }

  const errorMessages: string[] = []

  if (statsError) {
    errorMessages.push(
      statsError instanceof Error
        ? `Не удалось загрузить общую статистику: ${statsError.message}`
        : 'Не удалось загрузить общую статистику.'
    )
  }

  if (kpiError) {
    errorMessages.push(
      kpiError instanceof Error
        ? `Не удалось загрузить KPI: ${kpiError.message}`
        : 'Не удалось загрузить KPI.'
    )
  }

  // Используем значения по умолчанию при ошибке
  const safeStats = stats || {
    factories_count: 0,
    equipment_count: 0,
    active_equipment: 0,
    active_alerts: 0,
    new_recommendations: 0,
    average_oee: null,
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Главная панель</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Здесь сводим ключевые KPI по всей промышленной экосистеме: эффективность, загрузку оборудования, состояние аномалий и рекомендации ИИ.
          </p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg border border-blue-100 dark:border-blue-900/40 shadow p-5 text-sm text-gray-700 dark:text-gray-200 space-y-3">
        <h2 className="text-base font-semibold text-blue-800 dark:text-blue-300 flex items-center gap-2">
          <TrendingUp className="w-4 h-4" />
          Как читать этот дашборд
        </h2>
        <ul className="list-disc pl-5 space-y-2">
          <li><strong>Карточки KPI</strong> показывают операционные метрики. OEE &gt; 85% — зона высокой эффективности. Активное оборудование / алерты помогают сразу оценить нагрузку и риски.</li>
          <li><strong>График OEE</strong> отражает динамику за последние 7 дней. Падение линии сигнализирует о простоях, плановых ТО или потенциальной аномалии.</li>
          <li><strong>Блок «Статистика»</strong> агрегирует количество заводов, оборудования и среднюю доступность. Эти цифры обновляются каждые 30 секунд вместе с API.</li>
          <li><strong>Рекомендации</strong> формируются ML-движком: если значение &gt; 0, нажмите на карточку в разделе «Отчеты» → «Рекомендации» для детального разбора.</li>
        </ul>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Советы: следите за резким ростом алертов, сравнивайте «Активное оборудование» с «Всего оборудования» и используйте график OEE для объяснения исполнительной команде причин простоев.
        </p>
      </div>

      {errorMessages.length > 0 && (
        <div className="rounded-lg border border-yellow-400 bg-yellow-50 p-4 text-yellow-800 dark:border-yellow-500 dark:bg-yellow-900/40 dark:text-yellow-200">
          <h2 className="font-semibold mb-2">Часть данных не загрузилась</h2>
          <ul className="space-y-1 text-sm">
            {errorMessages.map((message, index) => (
              <li key={index}>• {message}</li>
            ))}
          </ul>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="OEE"
          value={safeStats.average_oee || 0}
          unit="%"
          trend={safeStats.average_oee && safeStats.average_oee > 80 ? "up" : "down"}
          trendValue={safeStats.average_oee ? (safeStats.average_oee - 80) : 0}
          icon={<TrendingUp className="w-5 h-5" />}
          color="green"
        />

        <KPICard
          title="Активное оборудование"
          value={safeStats.active_equipment || 0}
          unit={`из ${safeStats.equipment_count || 0}`}
          trend="up"
          trendValue={0}
          icon={<Activity className="w-5 h-5" />}
          color="blue"
        />

        <KPICard
          title="Активные алерты"
          value={safeStats.active_alerts || 0}
          unit=""
          trend={safeStats.active_alerts && safeStats.active_alerts > 0 ? "up" : "down"}
          trendValue={safeStats.active_alerts || 0}
          icon={<AlertTriangle className="w-5 h-5" />}
          color="red"
        />

        <KPICard
          title="Новые рекомендации"
          value={safeStats.new_recommendations || 0}
          unit=""
          trend="up"
          trendValue={safeStats.new_recommendations || 0}
          icon={<Zap className="w-5 h-5" />}
          color="purple"
        />
      </div>

      {/* Графики и статистика */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* График OEE */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-colors">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">OEE за последние 7 дней</h2>
          {kpiSummary && <OEEChart data={kpiSummary} />}
        </div>

        {/* Статистика по заводам */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 transition-colors">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-900 dark:text-white">
            <Factory className="w-5 h-5" />
            Статистика
          </h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Всего заводов:</span>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">{safeStats.factories_count || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Всего оборудования:</span>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">{safeStats.equipment_count || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600 dark:text-gray-400">Активное оборудование:</span>
              <span className="text-lg font-semibold text-green-600 dark:text-green-400">
                {safeStats.active_equipment || 0}
              </span>
            </div>
            {kpiSummary && (
              <>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Средняя доступность:</span>
                  <span className="text-lg font-semibold text-gray-900 dark:text-white">
                    {kpiSummary.average_availability?.toFixed(1) || 'N/A'}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 dark:text-gray-400">Простои (мин):</span>
                  <span className="text-lg font-semibold text-red-600 dark:text-red-400">
                    {kpiSummary.total_downtime_minutes}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

