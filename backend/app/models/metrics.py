"""
Модели для метрик и измерений
"""
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class MetricsCatalog(Base):
    """Каталог метрик (универсальные параметры)"""
    __tablename__ = "metrics_catalog"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_ru = Column(String(200), nullable=False)
    name_kk = Column(String(200))
    name_en = Column(String(200))
    code = Column(String(100), unique=True, nullable=False)
    
    # Единицы измерения
    unit = Column(String(50))  # °C, MPa, m/s, kW, %
    
    # Диапазоны
    min_value = Column(Numeric(15, 4))
    max_value = Column(Numeric(15, 4))
    optimal_min = Column(Numeric(15, 4))
    optimal_max = Column(Numeric(15, 4))
    critical_min = Column(Numeric(15, 4))
    critical_max = Column(Numeric(15, 4))
    
    # Классификация
    category = Column(String(100))  # temperature, pressure, speed, energy, quality
    data_type = Column(String(50))  # numeric, boolean, string
    
    # Применимость
    applicable_to = Column(JSONB)
    
    # Важность
    is_critical = Column(Boolean, default=False)
    is_kpi = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class MetricsData(Base):
    """Временные ряды метрик"""
    __tablename__ = "metrics_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    metric_id = Column(UUID(as_uuid=True), ForeignKey("metrics_catalog.id"), nullable=False)
    
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Numeric(20, 6))
    
    # Статус
    is_anomaly = Column(Boolean, default=False)
    is_critical = Column(Boolean, default=False)
    
    # Контекст
    shift = Column(String(50))  # day, night, morning
    operator_id = Column(UUID(as_uuid=True))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    equipment = relationship("Equipment")
    metric = relationship("MetricsCatalog")

