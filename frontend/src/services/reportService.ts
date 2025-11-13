import api from './api';

export interface ReportTemplate {
  id: string;
  name: string;
  description: string | null;
  report_type: string;
  format: string;
  schedule: string;
  is_public: boolean;
}

export interface GeneratedReport {
  id: string;
  template_id: string | null;
  factory_id: string | null;
  period_start: string | null;
  period_end: string | null;
  file_url: string | null;
  file_size_bytes: number | null;
  generated_at: string;
}

export const reportService = {
  async getTemplates(params?: {
    report_type?: string;
    is_public?: boolean;
  }): Promise<{ items: ReportTemplate[] }> {
    try {
      const response = await api.get('/reports/templates', { params });
      return response.data || { items: [] };
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return { items: [] };
      }
      throw error;
    }
  },

  async getGeneratedReports(params?: {
    factory_id?: string;
    template_id?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ items: GeneratedReport[]; limit: number; offset: number }> {
    try {
      const response = await api.get('/reports/generated', { params });
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

