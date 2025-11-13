import api from './api';

export interface Application {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  plan_code?: string | null;
  description: string | null;
  status: 'new' | 'approved' | 'rejected';
  created_at: string;
  created_user_id?: string;
  created_username?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  rejection_reason?: string;
}

export interface ApplicationCreate {
  full_name: string;
  email: string;
  phone: string;
  plan_code?: string;
  description?: string;
}

export interface ApproveApplicationRequest {
  username: string;
  factory_id?: string;
}

export interface ApproveApplicationResponse {
  success: boolean;
  user_id: string;
  username: string;
  email: string;
  password: string;
  message: string;
}

export const applicationService = {
  async createApplication(data: ApplicationCreate): Promise<Application> {
    const response = await api.post<Application>('/applications/', data);
    return response.data;
  },

  async getApplications(status?: string): Promise<Application[]> {
    const params = status ? { status } : {};
    const response = await api.get<Application[]>('/applications/', { params });
    return response.data;
  },

  async getApplication(id: string): Promise<Application> {
    const response = await api.get<Application>(`/applications/${id}`);
    return response.data;
  },

  async approveApplication(id: string, data: ApproveApplicationRequest): Promise<ApproveApplicationResponse> {
    const response = await api.post<ApproveApplicationResponse>(
      `/admin/applications/${id}/approve`,
      data
    );
    return response.data;
  },

  async rejectApplication(id: string, reason: string): Promise<void> {
    await api.post(`/admin/applications/${id}/reject`, { reason });
  },
};

