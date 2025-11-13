"""
Модели для заводов и отраслей
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
# POINT требует PostGIS расширение, закомментировано для базовой установки
# from sqlalchemy.dialects.postgresql import POINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class Industry(Base):
    """Отрасли промышленности"""
    __tablename__ = "industries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_ru = Column(String(200), nullable=False)
    name_kk = Column(String(200))
    name_en = Column(String(200))
    code = Column(String(50), unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))


class Factory(Base):
    """Справочник заводов"""
    __tablename__ = "factories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(300), nullable=False)
    industry_id = Column(UUID(as_uuid=True), ForeignKey("industries.id"))
    
    # Адрес
    region = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    # coordinates = Column(POINT)  # PostGIS для геолокации (требует расширение)
    
    # Контакты
    director_name = Column(String(200))
    phone = Column(String(50))
    email = Column(String(100))
    
    # Технические данные
    production_capacity = Column(Numeric(15, 2))
    capacity_unit = Column(String(50))
    equipment_count = Column(Integer, default=0)
    employee_count = Column(Integer)
    
    # Статус
    status = Column(String(50), default="active")
    subscription_plan = Column(String(50))
    subscription_expires_at = Column(Date)
    
    # Метаданные
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    industry = relationship("Industry", backref="factories")
    equipment = relationship("Equipment", back_populates="factory", cascade="all, delete-orphan")

