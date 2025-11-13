"""
Модели для подписок и биллинга
"""
from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class Subscription(Base):
    """Подписки и биллинг"""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"), nullable=False)
    
    plan = Column(String(50), nullable=False)  # basic, analytics, corporate
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    
    # Лимиты
    equipment_limit = Column(Integer)
    equipment_count = Column(Integer, default=0)
    
    # Оплата
    monthly_price = Column(Numeric(12, 2))
    currency = Column(String(10), default="KZT")
    
    is_trial = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    factory = relationship("Factory", backref="subscriptions")

