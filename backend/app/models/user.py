"""
Модели для пользователей и аутентификации
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class User(Base):
    """Пользователи системы"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    full_name = Column(String(200))
    position = Column(String(100))
    
    # Аутентификация
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Привязка к заводу
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"))
    
    # Роль
    role = Column(String(50))  # admin, manager, engineer, operator, viewer
    
    # Настройки
    language = Column(String(10), default="ru")  # ru, kk, en
    timezone = Column(String(50), default="Asia/Almaty")
    notification_preferences = Column(JSONB)
    
    last_login_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    factory = relationship("Factory")

