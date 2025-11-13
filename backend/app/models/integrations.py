"""
Модели для интеграций и отчетов
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Date, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class ExternalSystem(Base):
    """Внешние системы"""
    __tablename__ = "external_systems"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"))
    
    system_type = Column(String(100))  # erp, mes, scada, 1c, sap
    name = Column(String(200))
    
    # Подключение
    connection_type = Column(String(50))  # api, database, file_import
    endpoint_url = Column(String(500))
    credentials_encrypted = Column(Text)
    
    # Маппинг данных
    data_mapping = Column(JSONB)
    sync_frequency = Column(String(50))  # real-time, hourly, daily
    
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    factory = relationship("Factory")


class ReportTemplate(Base):
    """Шаблоны отчетов"""
    __tablename__ = "report_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    report_type = Column(String(100))  # oee, downtime, energy, production, quality
    
    # Параметры
    parameters = Column(JSONB)
    filters = Column(JSONB)
    
    # Формат
    format = Column(String(50))  # pdf, excel, csv
    template_file_url = Column(String(500))
    
    # Планирование
    schedule = Column(String(100))  # daily, weekly, monthly, on-demand
    recipients = Column(ARRAY(String))
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    creator = relationship("User")


class GeneratedReport(Base):
    """Сгенерированные отчеты"""
    __tablename__ = "generated_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("report_templates.id"))
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"))
    
    period_start = Column(Date)
    period_end = Column(Date)
    
    file_url = Column(String(500))
    file_size_bytes = Column(Integer)
    
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    generated_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    template = relationship("ReportTemplate")
    factory = relationship("Factory")
    generator = relationship("User")

