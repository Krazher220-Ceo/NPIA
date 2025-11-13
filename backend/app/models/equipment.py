"""
Модели для оборудования
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, Text, CheckConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class EquipmentType(Base):
    """Типы оборудования"""
    __tablename__ = "equipment_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_ru = Column(String(200), nullable=False)
    name_kk = Column(String(200))
    name_en = Column(String(200))
    category = Column(String(100))  # motors, pumps, furnaces, conveyors
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id"))
    
    # Характеристики по умолчанию
    default_metrics = Column(JSONB)
    maintenance_interval_days = Column(Integer)
    average_lifespan_years = Column(Numeric(5, 2))
    
    icon_url = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class Equipment(Base):
    """Оборудование"""
    __tablename__ = "equipment"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    equipment_type_id = Column(UUID(as_uuid=True), ForeignKey("equipment_types.id"))
    
    # Идентификация
    name = Column(String(300), nullable=False)
    serial_number = Column(String(100))
    inventory_number = Column(String(100))
    
    # Характеристики
    manufacturer = Column(String(200))
    model = Column(String(200))
    manufacture_year = Column(Integer)
    installation_date = Column(Date)
    
    # Местоположение на заводе
    workshop = Column(String(100))  # Цех
    line = Column(String(100))  # Линия
    position = Column(String(100))  # Позиция
    
    # Технические параметры
    rated_capacity = Column(Numeric(15, 2))
    capacity_unit = Column(String(50))
    power_consumption_kw = Column(Numeric(10, 2))
    
    # Состояние
    status = Column(String(50), default="operational")
    health_score = Column(Numeric(5, 2), default=100.00)
    
    # Обслуживание
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    maintenance_interval_days = Column(Integer)
    
    # Метаданные
    custom_fields = Column(JSONB)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Ограничения
    __table_args__ = (
        CheckConstraint('health_score >= 0 AND health_score <= 100', name='check_health_score'),
    )
    
    # Связи
    factory = relationship("Factory", back_populates="equipment")
    equipment_type = relationship("EquipmentType")

