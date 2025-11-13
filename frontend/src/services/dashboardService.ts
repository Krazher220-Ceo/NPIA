import api from './api'

export interface DashboardStats {
  factories_count: number
  equipment_count: number
  active_equipment: number
  active_alerts: number
  new_recommendations: number
  average_oee: number | null
}

export interface KPISummary {
  period_days: number
  average_oee: number | null
  average_availability: number | null
  average_performance: number | null
  average_quality: number | null
  total_downtime_minutes: number
}

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    try {
      const response = await api.get<DashboardStats>('/dashboard/stats')
      return response.data
    } catch (error: any) {
      // Возвращаем значения по умолчанию при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return {
          factories_count: 0,
          equipment_count: 0,
          active_equipment: 0,
          active_alerts: 0,
          new_recommendations: 0,
          average_oee: null,
        }
      }
      throw error
    }
  },

  async getKPISummary(days: number = 7): Promise<KPISummary> {
    try {
      const response = await api.get<KPISummary>('/dashboard/kpi-summary', {
        params: { days },
      })
      return response.data
    } catch (error: any) {
      // Возвращаем значения по умолчанию при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return {
          period_days: days,
          average_oee: null,
          average_availability: null,
          average_performance: null,
          average_quality: null,
          total_downtime_minutes: 0,
        }
      }
      throw error
    }
  },
}

