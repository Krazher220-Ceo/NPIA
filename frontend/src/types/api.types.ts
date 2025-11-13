export interface Factory {
  id: string
  name: string
  industry_id?: string
  region?: string
  city?: string
  address?: string
  director_name?: string
  phone?: string
  email?: string
  production_capacity?: number
  equipment_count: number
  status: string
  subscription_plan?: string
}

export interface Industry {
  id: string
  name_ru: string
  name_kk?: string
  name_en?: string
  code?: string
}

export interface Equipment {
  id: string
  name: string
  factory_id: string
  serial_number?: string
  status: string
  health_score?: number
  workshop?: string
  line?: string
  manufacturer?: string
  model?: string
  power_consumption_kw?: number
}

export interface KPIData {
  period_start: string
  period_end: string
  oee_score?: number
  availability?: number
  performance?: number
  quality?: number
  downtime_minutes: number
}

export interface Anomaly {
  id: string
  equipment_id: string
  detected_at: string
  severity: string
  anomaly_score?: number
  anomaly_type?: string
  status: string
}

export interface Prediction {
  id: string
  equipment_id: string
  prediction_type: string
  predicted_for: string
  confidence?: number
  recommended_action?: string
}

export interface Recommendation {
  id: string
  target_type: string
  target_id: string
  title: string
  category: string
  priority: string
  estimated_savings?: number
  status: string
}

