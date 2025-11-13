"""
Расширенные функции seed для дополнительных данных
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subscription import Subscription
from app.models.production import ProductionCycle, MaintenanceLog
from app.models.management import AccessRight, AuditLog
from app.models.integrations import ExternalSystem, ReportTemplate, GeneratedReport
from app.models.factory import Factory
from app.models.equipment import Equipment
from app.models.user import User
from sqlalchemy import select
from datetime import datetime, timedelta, date
from decimal import Decimal
import uuid


async def seed_subscriptions(db: AsyncSession, factories: list):
    """Создание подписок"""
    plans = {
        "basic": {"price": 150000, "limit": 10},
        "analytics": {"price": 450000, "limit": 50},
        "corporate": {"price": 1200000, "limit": None},
    }
    
    subscriptions_data = [
        {
            "factory_id": factories[0].id,
            "plan": "corporate",
            "start_date": date.today() - timedelta(days=90),
            "end_date": date.today() + timedelta(days=275),
            "equipment_limit": None,
            "equipment_count": factories[0].equipment_count,
            "monthly_price": Decimal(str(plans["corporate"]["price"])),
            "currency": "KZT",
            "is_trial": False,
            "is_active": True,
        },
        {
            "factory_id": factories[1].id,
            "plan": "analytics",
            "start_date": date.today() - timedelta(days=60),
            "end_date": date.today() + timedelta(days=305),
            "equipment_limit": 50,
            "equipment_count": factories[1].equipment_count,
            "monthly_price": Decimal(str(plans["analytics"]["price"])),
            "currency": "KZT",
            "is_trial": False,
            "is_active": True,
        },
        {
            "factory_id": factories[2].id,
            "plan": "analytics",
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today() + timedelta(days=335),
            "equipment_limit": 50,
            "equipment_count": factories[2].equipment_count,
            "monthly_price": Decimal(str(plans["analytics"]["price"])),
            "currency": "KZT",
            "is_trial": True,
            "is_active": True,
        },
    ]
    
    for data in subscriptions_data:
        subscription = Subscription(**data)
        db.add(subscription)
    
    await db.commit()


async def seed_production_cycles(db: AsyncSession, factories: list, equipment_list: list):
    """Создание производственных циклов"""
    now = datetime.utcnow()
    
    cycles_data = []
    for i in range(10):  # 10 циклов за последние 3 дня
        cycle_time = now - timedelta(hours=i*6)
        factory = factories[i % len(factories)]
        equipment = equipment_list[i % len(equipment_list)] if equipment_list else None
        
        cycles_data.append({
            "factory_id": factory.id,
            "equipment_id": equipment.id if equipment else None,
            "start_time": cycle_time,
            "end_time": cycle_time + timedelta(hours=4),
            "duration_minutes": 240,
            "product_name": f"Продукт {i+1}",
            "planned_quantity": Decimal("1000"),
            "actual_quantity": Decimal("950") + Decimal(str(i * 10)),
            "quantity_unit": "кг",
            "defect_quantity": Decimal("5") + Decimal(str(i)),
            "quality_percentage": Decimal("95.5") + Decimal(str(i * 0.1)),
            "oee_score": Decimal("82.0") + Decimal(str(i * 0.5)),
            "availability": Decimal("90.0") + Decimal(str(i * 0.3)),
            "performance": Decimal("88.0") + Decimal(str(i * 0.2)),
            "quality": Decimal("94.0") + Decimal(str(i * 0.1)),
            "energy_consumed_kwh": Decimal("5000") + Decimal(str(i * 100)),
            "raw_material_consumed": Decimal("2000") + Decimal(str(i * 50)),
            "raw_material_unit": "кг",
            "shift": ["day", "night", "morning"][i % 3],
            "status": "completed",
        })
    
    for data in cycles_data:
        cycle = ProductionCycle(**data)
        db.add(cycle)
    
    await db.commit()


async def seed_maintenance_logs(db: AsyncSession, equipment_list: list):
    """Создание журнала обслуживания"""
    now = datetime.utcnow()
    
    logs_data = [
        {
            "equipment_id": equipment_list[0].id,
            "type": "planned",
            "title": "Плановое ТО прокатного стана",
            "description": "Замена масла, проверка подшипников",
            "scheduled_date": date.today() - timedelta(days=5),
            "start_time": now - timedelta(days=5, hours=8),
            "end_time": now - timedelta(days=5, hours=12),
            "duration_minutes": 240,
            "cost": Decimal("150000"),
            "cost_currency": "KZT",
            "downtime_cost": Decimal("500000"),
            "technician_name": "Иванов И.И.",
            "status": "completed",
        },
        {
            "equipment_id": equipment_list[1].id,
            "type": "unplanned",
            "title": "Ремонт насоса охлаждения",
            "description": "Замена уплотнительных колец",
            "scheduled_date": date.today() - timedelta(days=2),
            "start_time": now - timedelta(days=2, hours=14),
            "end_time": now - timedelta(days=2, hours=18),
            "duration_minutes": 240,
            "cost": Decimal("80000"),
            "cost_currency": "KZT",
            "downtime_cost": Decimal("200000"),
            "technician_name": "Петров П.П.",
            "status": "completed",
        },
        {
            "equipment_id": equipment_list[2].id,
            "type": "inspection",
            "title": "Технический осмотр печи",
            "description": "Проверка состояния футеровки",
            "scheduled_date": date.today() + timedelta(days=7),
            "cost": Decimal("50000"),
            "cost_currency": "KZT",
            "status": "scheduled",
        },
    ]
    
    for data in logs_data:
        log = MaintenanceLog(**data)
        db.add(log)
    
    await db.commit()


async def seed_external_systems(db: AsyncSession, factories: list):
    """Создание внешних систем"""
    systems_data = [
        {
            "factory_id": factories[0].id,
            "system_type": "erp",
            "name": "SAP ERP",
            "connection_type": "api",
            "endpoint_url": "https://sap.example.com/api",
            "sync_frequency": "hourly",
            "is_active": True,
            "last_sync_at": datetime.utcnow() - timedelta(minutes=30),
        },
        {
            "factory_id": factories[1].id,
            "system_type": "mes",
            "name": "MES System",
            "connection_type": "database",
            "endpoint_url": "postgresql://mes.local:5432/mesdb",
            "sync_frequency": "real-time",
            "is_active": True,
            "last_sync_at": datetime.utcnow() - timedelta(minutes=5),
        },
        {
            "factory_id": factories[0].id,
            "system_type": "1c",
            "name": "1С:Предприятие",
            "connection_type": "api",
            "endpoint_url": "https://1c.example.com/api",
            "sync_frequency": "daily",
            "is_active": True,
            "last_sync_at": datetime.utcnow() - timedelta(hours=12),
        },
    ]
    
    for data in systems_data:
        system = ExternalSystem(**data)
        db.add(system)
    
    await db.commit()


async def seed_report_templates(db: AsyncSession, users: list):
    """Создание шаблонов отчетов"""
    templates_data = [
        {
            "name": "Ежедневный отчет OEE",
            "description": "Отчет по общей эффективности оборудования за день",
            "report_type": "oee",
            "format": "pdf",
            "schedule": "daily",
            "recipients": ["manager@arcelormittal.kz"],
            "created_by": users[0].id,
            "is_public": False,
        },
        {
            "name": "Отчет по простоям",
            "description": "Анализ простоев оборудования за период",
            "report_type": "downtime",
            "format": "excel",
            "schedule": "weekly",
            "recipients": ["admin@factory.kz"],
            "created_by": users[0].id,
            "is_public": True,
        },
        {
            "name": "Энергетический отчет",
            "description": "Потребление энергии и оптимизация",
            "report_type": "energy",
            "format": "pdf",
            "schedule": "monthly",
            "recipients": ["engineer@anpz.kz"],
            "created_by": users[1].id,
            "is_public": False,
        },
    ]
    
    for data in templates_data:
        template = ReportTemplate(**data)
        db.add(template)
    
    await db.commit()


async def seed_generated_reports(db: AsyncSession, factories: list, users: list):
    """Создание сгенерированных отчетов"""
    now = datetime.utcnow()
    
    # Получаем шаблоны
    from app.models.integrations import ReportTemplate
    template_result = await db.execute(select(ReportTemplate).limit(1))
    template = template_result.scalar_one_or_none()
    
    if not template:
        return
    
    reports_data = [
        {
            "template_id": template.id,
            "factory_id": factories[0].id,
            "period_start": date.today() - timedelta(days=7),
            "period_end": date.today(),
            "file_url": "/reports/oee_report_2025_11_10.pdf",
            "file_size_bytes": 245760,
            "generated_by": users[0].id,
            "generated_at": now - timedelta(hours=2),
        },
        {
            "template_id": template.id,
            "factory_id": factories[1].id,
            "period_start": date.today() - timedelta(days=30),
            "period_end": date.today(),
            "file_url": "/reports/monthly_report_2025_11.xlsx",
            "file_size_bytes": 512000,
            "generated_by": users[1].id,
            "generated_at": now - timedelta(days=1),
        },
    ]
    
    for data in reports_data:
        report = GeneratedReport(**data)
        db.add(report)
    
    await db.commit()


async def seed_access_rights(db: AsyncSession, users: list):
    """Создание прав доступа"""
    # Admin получает полные права
    admin = next((u for u in users if u.role == "admin"), None)
    manager = next((u for u in users if u.role == "manager"), None)
    
    if admin and manager:
        rights_data = [
            {
                "user_id": admin.id,
                "resource_type": "factory",
                "permissions": ["read", "write", "delete", "execute"],
            },
            {
                "user_id": manager.id,
                "resource_type": "equipment",
                "permissions": ["read", "write"],
            },
            {
                "user_id": manager.id,
                "resource_type": "reports",
                "permissions": ["read", "execute"],
            },
        ]
        
        for data in rights_data:
            right = AccessRight(**data)
            db.add(right)
        
        await db.commit()


async def seed_audit_logs(db: AsyncSession, users: list):
    """Создание аудит логов"""
    now = datetime.utcnow()
    
    logs_data = [
        {
            "user_id": users[0].id,
            "action": "login",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0",
        },
        {
            "user_id": users[1].id,
            "action": "update",
            "entity_type": "equipment",
            "changes": {"old": {"status": "operational"}, "new": {"status": "maintenance"}},
            "ip_address": "192.168.1.101",
        },
        {
            "user_id": users[0].id,
            "action": "export",
            "entity_type": "report",
            "ip_address": "192.168.1.100",
        },
    ]
    
    for data in logs_data:
        log = AuditLog(**data)
        db.add(log)
    
    await db.commit()

