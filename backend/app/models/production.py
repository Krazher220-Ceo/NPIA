"""
Модели для производственных циклов и обслуживания
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class ProductionCycle(Base):
    """Производственные циклы"""
    __tablename__ = "production_cycles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id"))
    
    # Временные рамки
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Продукция
    product_name = Column(String(200))
    planned_quantity = Column(Numeric(15, 2))
    actual_quantity = Column(Numeric(15, 2))
    quantity_unit = Column(String(50))
    
    # Качество
    defect_quantity = Column(Numeric(15, 2), default=0)
    quality_percentage = Column(Numeric(5, 2))
    
    # KPI
    oee_score = Column(Numeric(5, 2))
    availability = Column(Numeric(5, 2))
    performance = Column(Numeric(5, 2))
    quality = Column(Numeric(5, 2))
    
    # Ресурсы
    energy_consumed_kwh = Column(Numeric(12, 2))
    raw_material_consumed = Column(Numeric(15, 2))
    raw_material_unit = Column(String(50))
    
    # Персонал
    shift = Column(String(50))  # day, night, morning
    operator_ids = Column(UUID(as_uuid=True))  # Упрощено - один оператор
    
    status = Column(String(50), default="in_progress")  # in_progress, completed, aborted
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    factory = relationship("Factory")
    equipment = relationship("Equipment")


class MaintenanceLog(Base):
    """Журнал обслуживания и поломок"""
    __tablename__ = "maintenance_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_id = Column(UUID(as_uuid=True), ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    
    type = Column(String(50), nullable=False)  # planned, unplanned, repair, inspection
    
    # Время
    scheduled_date = Column(Date)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    
    # Детали
    title = Column(String(300))
    description = Column(Text)
    root_cause = Column(Text)
    
    # Затраты
    cost = Column(Numeric(12, 2))
    cost_currency = Column(String(10), default="KZT")
    downtime_cost = Column(Numeric(12, 2))
    
    # Персонал
    technician_name = Column(String(200))
    contractor_company = Column(String(200))
    
    # Запчасти
    parts_used = Column(JSONB)
    
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    equipment = relationship("Equipment")

