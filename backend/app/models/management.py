"""
Модели для управления доступом и аудита
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import uuid
from app.core.database import Base


class AccessRight(Base):
    """Права доступа (RBAC)"""
    __tablename__ = "access_rights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    resource_type = Column(String(100))  # factory, equipment, reports, analytics
    resource_id = Column(UUID(as_uuid=True))
    
    permissions = Column(ARRAY(String))  # ['read', 'write', 'delete', 'execute']
    
    granted_at = Column(DateTime(timezone=True), server_default=text("now()"))
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    expires_at = Column(DateTime(timezone=True))
    
    # Связи
    user = relationship("User", foreign_keys=[user_id])


class AuditLog(Base):
    """Журнал аудита"""
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    action = Column(String(100), nullable=False)  # create, update, delete, login, export
    entity_type = Column(String(100))
    entity_id = Column(UUID(as_uuid=True))
    
    # Детали
    changes = Column(JSONB)  # {"old": {...}, "new": {...}}
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    
    # Связи
    user = relationship("User")

