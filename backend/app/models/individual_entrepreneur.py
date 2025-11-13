"""
Модель для индивидуальных предпринимателей (ИП)
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base

# Связующая таблица для связи ИП с заводами
ip_factory_association = Table(
    'ip_factory_association',
    Base.metadata,
    Column('ip_id', UUID(as_uuid=True), ForeignKey('individual_entrepreneurs.id'), primary_key=True),
    Column('factory_id', UUID(as_uuid=True), ForeignKey('factories.id'), primary_key=True)
)


class IndividualEntrepreneur(Base):
    """Индивидуальные предприниматели"""
    __tablename__ = "individual_entrepreneurs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Данные ИП
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), nullable=False)
    bin = Column(String(20), nullable=True)  # БИН (Бизнес-идентификационный номер)
    
    # Тарифный план
    plan_code = Column(String(50), nullable=False)  # basic, analytics, ip
    # Для ИП тарифа: можно связывать несколько заводов и делать общую аналитику
    
    # Лимиты
    factory_limit = Column(String(50), nullable=True)  # null = безлимит для ИП тарифа
    
    # Статус
    is_active = Column(Boolean, default=True)
    
    # Связи
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Связанный аккаунт пользователя
    factories = relationship("Factory", secondary=ip_factory_association, backref="individual_entrepreneurs")
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

