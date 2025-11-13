import api from './api';

export interface ExternalSystem {
  id: string;
  factory_id: string | null;
  system_type: string;
  name: string;
  connection_type: string;
  sync_frequency: string;
  is_active: boolean;
  last_sync_at: string | null;
}

export const integrationService = {
  async getSystems(params?: {
    factory_id?: string;
    system_type?: string;
    is_active?: boolean;
  }): Promise<{ items: ExternalSystem[] }> {
    try {
      const response = await api.get('/integrations/', { params });
      return response.data || { items: [] };
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return { items: [] };
      }
      throw error;
    }
  },
};

