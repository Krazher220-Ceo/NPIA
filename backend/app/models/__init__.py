"""
Модели базы данных
"""
from app.models.factory import Factory, Industry
from app.models.equipment import Equipment, EquipmentType
from app.models.metrics import MetricsCatalog, MetricsData
from app.models.user import User
from app.models.analytics import KPICalculation, Anomaly, Prediction, Recommendation
from app.models.subscription import Subscription
from app.models.production import ProductionCycle, MaintenanceLog
from app.models.management import AccessRight, AuditLog
from app.models.integrations import ExternalSystem, ReportTemplate, GeneratedReport
from app.models.application import Application
from app.models.individual_entrepreneur import IndividualEntrepreneur

__all__ = [
    "Industry",
    "Factory",
    "Equipment",
    "EquipmentType",
    "MetricsCatalog",
    "MetricsData",
    "User",
    "KPICalculation",
    "Anomaly",
    "Prediction",
    "Recommendation",
    "Subscription",
    "ProductionCycle",
    "MaintenanceLog",
    "AccessRight",
    "AuditLog",
    "ExternalSystem",
    "ReportTemplate",
    "GeneratedReport",
    "Application",
    "IndividualEntrepreneur",
]

