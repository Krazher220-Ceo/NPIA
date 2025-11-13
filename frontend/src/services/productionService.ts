import api from './api';

export interface ProductionCycle {
  id: string;
  factory_id: string;
  equipment_id: string | null;
  start_time: string;
  end_time: string | null;
  product_name: string | null;
  planned_quantity: number | null;
  actual_quantity: number | null;
  oee_score: number | null;
  status: string;
}

export interface MaintenanceLog {
  id: string;
  equipment_id: string;
  type: string;
  title: string;
  scheduled_date: string | null;
  start_time: string | null;
  end_time: string | null;
  duration_minutes: number | null;
  cost: number | null;
  status: string;
}

export const productionService = {
  async getCycles(params?: {
    factory_id?: string;
    equipment_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ items: ProductionCycle[]; limit: number; offset: number }> {
    try {
      const response = await api.get('/production/cycles', { params });
      return response.data || { items: [], limit: params?.limit || 20, offset: params?.offset || 0 };
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return { items: [], limit: params?.limit || 20, offset: params?.offset || 0 };
      }
      throw error;
    }
  },

  async getMaintenanceLogs(params?: {
    equipment_id?: string;
    type?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ items: MaintenanceLog[]; limit: number; offset: number }> {
    try {
      const response = await api.get('/production/maintenance', { params });
      return response.data || { items: [], limit: params?.limit || 20, offset: params?.offset || 0 };
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return { items: [], limit: params?.limit || 20, offset: params?.offset || 0 };
      }
      throw error;
    }
  },
};

