"""
Модель для заявок на роль руководителя
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class Application(Base):
    """Заявки на роль руководителя"""
    __tablename__ = "applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Данные заявителя
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), nullable=False)
    description = Column(Text)  # Краткое описание опыта/роли
    
    # Выбранный тарифный план
    plan_code = Column(String(50), nullable=True)  # basic, analytics, ip (для ИП)
    
    # Статус заявки
    status = Column(String(50), default="new")  # new, approved, rejected
    
    # Данные созданного аккаунта (если одобрена)
    created_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_username = Column(String(255), nullable=True)
    password_pdf_url = Column(String(500), nullable=True)  # URL к PDF с паролем
    
    # Метаданные
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связи
    created_user = relationship("User", foreign_keys=[created_user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

