"""
Модели для аналитики и ML
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class KPICalculation(Base):
    """Расчётные KPI (агрегированные данные)"""
    __tablename__ = "kpi_calculations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # factory, equipment, production_line
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    period_type = Column(String(50), nullable=False)  # hourly, daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # KPI метрики
    oee_score = Column(Numeric(5, 2))
    availability = Column(Numeric(5, 2))
    performance = Column(Numeric(5, 2))
    quality = Column(Numeric(5, 2))
    
    # Производство
    total_production = Column(Numeric(15, 2))
    planned_production = Column(Numeric(15, 2))
    production_variance = Column(Numeric(5, 2))
    
    # Простои
    downtime_minutes = Column(Integer, default=0)
    downtime_percentage = Column(Numeric(5, 2))
    unplanned_downtime_minutes = Column(Integer, default=0)
    
    # Ресурсы
    energy_consumption_kwh = Column(Numeric(12, 2))
    energy_cost = Column(Numeric(12, 2))
    specific_energy = Column(Numeric(10, 4))
    
    # Качество
    defect_rate = Column(Numeric(5, 2))
    rework_rate = Column(Numeric(5, 2))
    
    # Финансы
    revenue = Column(Numeric(15, 2))
    costs = Column(Numeric(15, 2))
    profit_margin = Column(Numeric(5, 2))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class Anomaly(Base):
    """Аномалии (выявленные ML)"""
    __tablename__ = "anomalies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics_catalog.id"))
    
    detected_at = Column(DateTime(timezone=True), nullable=False)
    
    # Детали аномалии
    severity = Column(String(50))  # low, medium, high, critical
    anomaly_score = Column(Numeric(5, 4))  # 0-1
    
    expected_value = Column(Numeric(15, 4))
    actual_value = Column(Numeric(15, 4))
    deviation_percentage = Column(Numeric(7, 2))
    
    # Классификация
    anomaly_type = Column(String(100))  # spike, drop, drift, oscillation, flatline
    pattern = Column(Text)
    
    # Контекст
    related_metrics = Column(JSONB)
    
    # Статус
    status = Column(String(50), default="new")  # new, acknowledged, investigating, resolved
    acknowledged_by = Column(UUID(as_uuid=True))
    acknowledged_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    equipment = relationship("Equipment")
    metric = relationship("MetricsCatalog")


class Prediction(Base):
    """Прогнозы (ML predictions)"""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"), nullable=False)
    
    prediction_type = Column(String(100))  # failure, maintenance_needed, production_forecast
    
    created_at = Column(DateTime(timezone=True), nullable=False)
    predicted_for = Column(DateTime(timezone=True), nullable=False)
    
    # Результат прогноза
    prediction_value = Column(Numeric(15, 4))
    prediction_label = Column(String(200))
    confidence = Column(Numeric(5, 4))  # 0-1
    
    # Детали
    model_name = Column(String(100))
    model_version = Column(String(50))
    input_features = Column(JSONB)
    
    # Рекомендация
    recommended_action = Column(Text)
    estimated_cost_if_ignored = Column(Numeric(12, 2))
    
    # Фактический результат
    actual_value = Column(Numeric(15, 4))
    actual_occurred_at = Column(DateTime(timezone=True))
    prediction_accuracy = Column(Numeric(5, 4))
    
    # Связи
    equipment = relationship("Equipment")


class Recommendation(Base):
    """Рекомендации системы"""
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_type = Column(String(50))  # equipment, factory, production_line
    target_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Категория
    category = Column(String(100))  # maintenance, optimization, energy_saving
    priority = Column(String(50))  # low, medium, high, urgent
    
    # Содержание
    title = Column(String(300), nullable=False)
    description = Column(Text)
    expected_benefit = Column(Text)
    
    # Оценка эффекта
    estimated_savings = Column(Numeric(12, 2))
    savings_currency = Column(String(10), default="KZT")
    payback_period_days = Column(Integer)
    
    implementation_cost = Column(Numeric(12, 2))
    implementation_time_hours = Column(Integer)
    
    # Источник
    source = Column(String(100))  # ml_model, rule_engine, manual
    related_anomaly_id = Column(UUID(as_uuid=True), ForeignKey("anomalies.id"))
    related_prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"))
    
    # Статус
    status = Column(String(50), default="new")  # new, reviewing, accepted, implementing, completed
    assigned_to = Column(UUID(as_uuid=True))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

