import api from './api'
import { Factory, Industry } from '../types/api.types'

export const factoryService = {
  async getFactories(params?: {
    industry_id?: string
    status?: string
    limit?: number
    offset?: number
  }) {
    try {
      const response = await api.get<{
        items: Factory[]
        total: number
        limit: number
        offset: number
      }>('/factories/', { params })
      return response.data
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return {
          items: [],
          total: 0,
          limit: params?.limit || 50,
          offset: params?.offset || 0,
        }
      }
      throw error
    }
  },

  async getFactory(id: string) {
    try {
      const response = await api.get<Factory>(`/factories/${id}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Завод не найден')
      }
      throw error
    }
  },

  async getIndustries() {
    try {
      const response = await api.get<{ items: Industry[] }>('/factories/industries/')
      return response.data.items || []
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return []
      }
      throw error
    }
  },
}

