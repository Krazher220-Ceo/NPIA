import api from './api';

export interface Subscription {
  id: string;
  factory_id: string;
  plan: 'basic' | 'analytics' | 'corporate';
  start_date: string;
  end_date: string | null;
  equipment_limit: number | null;
  equipment_count: number;
  monthly_price: number;
  currency: string;
  is_trial: boolean;
  is_active: boolean;
}

export interface SubscriptionPlan {
  code: string;
  name: string;
  price: number;
  currency: string;
  equipment_limit: number | null;
  features: string[];
}

export const subscriptionService = {
  async getSubscriptions(factoryId?: string): Promise<{ items: Subscription[] }> {
    try {
      const params = factoryId ? { factory_id: factoryId } : {};
      const response = await api.get('/subscriptions/', { params });
      return response.data || { items: [] };
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return { items: [] };
      }
      throw error;
    }
  },

  async getPlans(): Promise<{ plans: SubscriptionPlan[] }> {
    try {
      const response = await api.get('/subscriptions/plans');
      return response.data || { plans: [] };
    } catch (error: any) {
      // Возвращаем пустой список при ошибке
      if (error.response?.status === 404 || error.response?.status >= 500) {
        return { plans: [] };
      }
      throw error;
    }
  },
};

