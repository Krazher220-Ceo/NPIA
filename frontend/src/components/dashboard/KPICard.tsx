import { ReactNode } from 'react'

interface KPICardProps {
  title: string
  value: number
  unit: string
  trend?: 'up' | 'down'
  trendValue?: number
  icon: ReactNode
  color: 'green' | 'blue' | 'red' | 'purple'
}

const colorClasses = {
  green: 'bg-green-50 text-green-700 border-green-200',
  blue: 'bg-blue-50 text-blue-700 border-blue-200',
  red: 'bg-red-50 text-red-700 border-red-200',
  purple: 'bg-purple-50 text-purple-700 border-purple-200',
}

export default function KPICard({
  title,
  value,
  unit,
  trend,
  trendValue,
  icon,
  color,
}: KPICardProps) {
  return (
    <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
        <div className={colorClasses[color].split(' ')[0]}>{icon}</div>
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-bold">
          {value.toLocaleString('ru-RU')}
        </span>
        <span className="text-sm text-gray-500">{unit}</span>
      </div>
      {trend && trendValue && (
        <div className="mt-2 text-sm">
          <span className={trend === 'up' ? 'text-green-600' : 'text-red-600'}>
            {trend === 'up' ? '↑' : '↓'} {Math.abs(trendValue)}%
          </span>
          <span className="text-gray-500 ml-1">за период</span>
        </div>
      )}
    </div>
  )
}

