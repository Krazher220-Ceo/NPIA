"""
Скрипт для заполнения базы данных тестовыми данными (seed data)
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.sql import func
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.factory import Industry, Factory
from app.models.equipment import EquipmentType, Equipment
from app.models.metrics import MetricsCatalog
from app.models.user import User
from app.models.analytics import KPICalculation, Anomaly, Recommendation
from app.models.subscription import Subscription
from app.models.production import ProductionCycle, MaintenanceLog
from app.models.management import AccessRight, AuditLog
from app.models.integrations import ExternalSystem, ReportTemplate, GeneratedReport
from app.core.security import get_password_hash
from datetime import datetime, timedelta, date
from decimal import Decimal
import uuid


async def create_tables():
    """Создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_industries(db: AsyncSession):
    """Создание отраслей промышленности"""
    # Проверка существующих данных
    existing = await db.scalar(select(func.count(Industry.id)))
    if existing and existing > 0:
        print("⚠️  Отрасли уже существуют, пропускаем...")
        result = await db.execute(select(Industry))
        return result.scalars().all()
    
    industries_data = [
        {"name_ru": "Металлургия", "name_kk": "Металлургия", "name_en": "Metallurgy", "code": "METAL"},
        {"name_ru": "Нефтепереработка", "name_kk": "Мұнай өңдеу", "name_en": "Oil Refining", "code": "OIL"},
        {"name_ru": "Химическая промышленность", "name_kk": "Химиялық өнеркәсіп", "name_en": "Chemical Industry", "code": "CHEM"},
        {"name_ru": "Пищевая промышленность", "name_kk": "Азық-түлік өнеркәсібі", "name_en": "Food Industry", "code": "FOOD"},
        {"name_ru": "Машиностроение", "name_kk": "Машина жасау", "name_en": "Mechanical Engineering", "code": "MECH"},
        {"name_ru": "Цементная промышленность", "name_kk": "Цемент өнеркәсібі", "name_en": "Cement Industry", "code": "CEMENT"},
    ]
    
    industries = []
    for data in industries_data:
        industry = Industry(**data)
        db.add(industry)
        industries.append(industry)
    
    await db.commit()
    return industries


async def seed_factories(db: AsyncSession, industries: list):
    """Создание заводов"""
    factories_data = [
        {
            "name": "АО «АрселорМиттал Темиртау»",
            "industry_id": industries[0].id,
            "region": "Карагандинская область",
            "city": "Темиртау",
            "address": "г. Темиртау, пр. Республики, 1",
            "director_name": "Иванов Иван Иванович",
            "phone": "+7 (721) 123-45-67",
            "email": "info@arcelormittal.kz",
            "production_capacity": Decimal("5000000"),
            "capacity_unit": "тонн/год",
            "equipment_count": 25,
            "employee_count": 5000,
            "status": "active",
            "subscription_plan": "corporate",
        },
        {
            "name": "Атырауский НПЗ",
            "industry_id": industries[1].id,
            "region": "Атырауская область",
            "city": "Атырау",
            "address": "г. Атырау, ул. Нефтяников, 10",
            "director_name": "Петров Петр Петрович",
            "phone": "+7 (712) 234-56-78",
            "email": "info@anpz.kz",
            "production_capacity": Decimal("5000000"),
            "capacity_unit": "тонн/год",
            "equipment_count": 18,
            "employee_count": 3000,
            "status": "active",
            "subscription_plan": "analytics",
        },
        {
            "name": "АО «КазАзот»",
            "industry_id": industries[2].id,
            "region": "Жамбылская область",
            "city": "Тараз",
            "address": "г. Тараз, промзона",
            "director_name": "Сидоров Сидор Сидорович",
            "phone": "+7 (726) 345-67-89",
            "email": "info@kazazot.kz",
            "production_capacity": Decimal("1000000"),
            "capacity_unit": "тонн/год",
            "equipment_count": 12,
            "employee_count": 1500,
            "status": "active",
            "subscription_plan": "analytics",
        },
    ]
    
    factories = []
    for data in factories_data:
        factory = Factory(**data)
        db.add(factory)
        factories.append(factory)
    
    await db.commit()
    return factories


async def seed_equipment_types(db: AsyncSession):
    """Создание типов оборудования"""
    types_data = [
        {
            "name_ru": "Прокатный стан",
            "name_kk": "Прокат станок",
            "name_en": "Rolling Mill",
            "category": "rolling",
            "maintenance_interval_days": 90,
            "average_lifespan_years": Decimal("25.0"),
        },
        {
            "name_ru": "Насос центробежный",
            "name_kk": "Орталықтан тепкіш насос",
            "name_en": "Centrifugal Pump",
            "category": "pump",
            "maintenance_interval_days": 180,
            "average_lifespan_years": Decimal("15.0"),
        },
        {
            "name_ru": "Печь обжиговая",
            "name_kk": "Күйдіру пеші",
            "name_en": "Furnace",
            "category": "furnace",
            "maintenance_interval_days": 365,
            "average_lifespan_years": Decimal("30.0"),
        },
        {
            "name_ru": "Конвейер ленточный",
            "name_kk": "Таспалы конвейер",
            "name_en": "Belt Conveyor",
            "category": "conveyor",
            "maintenance_interval_days": 60,
            "average_lifespan_years": Decimal("20.0"),
        },
    ]
    
    equipment_types = []
    for data in types_data:
        eq_type = EquipmentType(**data)
        db.add(eq_type)
        equipment_types.append(eq_type)
    
    await db.commit()
    return equipment_types


async def seed_equipment(db: AsyncSession, factories: list, equipment_types: list):
    """Создание оборудования"""
    equipment_data = [
        {
            "factory_id": factories[0].id,
            "equipment_type_id": equipment_types[0].id,
            "name": "Прокатный стан №1",
            "serial_number": "PM-001",
            "inventory_number": "INV-001",
            "manufacturer": "Siemens",
            "model": "PM-5000",
            "manufacture_year": 2015,
            "workshop": "Прокатный цех",
            "line": "Линия А",
            "status": "operational",
            "health_score": Decimal("85.5"),
            "power_consumption_kw": Decimal("5000.0"),
        },
        {
            "factory_id": factories[0].id,
            "equipment_type_id": equipment_types[1].id,
            "name": "Насос охлаждения №3",
            "serial_number": "PUMP-003",
            "inventory_number": "INV-002",
            "manufacturer": "Grundfos",
            "model": "CR-100",
            "manufacture_year": 2018,
            "workshop": "Водоочистка",
            "line": "Линия Б",
            "status": "operational",
            "health_score": Decimal("92.3"),
            "power_consumption_kw": Decimal("150.0"),
        },
        {
            "factory_id": factories[1].id,
            "equipment_type_id": equipment_types[2].id,
            "name": "Печь ректификационная №2",
            "serial_number": "FURN-002",
            "inventory_number": "INV-003",
            "manufacturer": "UOP",
            "model": "CCR-500",
            "manufacture_year": 2010,
            "workshop": "Переработка",
            "line": "Установка А",
            "status": "operational",
            "health_score": Decimal("78.2"),
            "power_consumption_kw": Decimal("8000.0"),
        },
    ]
    
    equipment_list = []
    for data in equipment_data:
        equipment = Equipment(**data)
        db.add(equipment)
        equipment_list.append(equipment)
    
    await db.commit()
    return equipment_list


async def seed_metrics_catalog(db: AsyncSession):
    """Создание каталога метрик"""
    metrics_data = [
        {
            "name_ru": "Температура",
            "name_kk": "Температура",
            "name_en": "Temperature",
            "code": "temp",
            "unit": "°C",
            "category": "temperature",
            "data_type": "numeric",
            "min_value": Decimal("-50.0"),
            "max_value": Decimal("2000.0"),
            "optimal_min": Decimal("20.0"),
            "optimal_max": Decimal("100.0"),
            "critical_min": Decimal("0.0"),
            "critical_max": Decimal("150.0"),
            "is_critical": True,
            "is_kpi": False,
        },
        {
            "name_ru": "Давление",
            "name_kk": "Қысым",
            "name_en": "Pressure",
            "code": "pressure",
            "unit": "МПа",
            "category": "pressure",
            "data_type": "numeric",
            "min_value": Decimal("0.0"),
            "max_value": Decimal("100.0"),
            "optimal_min": Decimal("1.0"),
            "optimal_max": Decimal("10.0"),
            "critical_min": Decimal("0.5"),
            "critical_max": Decimal("15.0"),
            "is_critical": True,
            "is_kpi": False,
        },
        {
            "name_ru": "Скорость",
            "name_kk": "Жылдамдық",
            "name_en": "Speed",
            "code": "speed",
            "unit": "м/мин",
            "category": "speed",
            "data_type": "numeric",
            "min_value": Decimal("0.0"),
            "max_value": Decimal("1000.0"),
            "optimal_min": Decimal("50.0"),
            "optimal_max": Decimal("200.0"),
            "critical_min": Decimal("10.0"),
            "critical_max": Decimal("300.0"),
            "is_critical": False,
            "is_kpi": True,
        },
        {
            "name_ru": "Энергопотребление",
            "name_kk": "Энергия тұтыну",
            "name_en": "Energy Consumption",
            "code": "energy",
            "unit": "кВт",
            "category": "energy",
            "data_type": "numeric",
            "min_value": Decimal("0.0"),
            "max_value": Decimal("10000.0"),
            "optimal_min": Decimal("100.0"),
            "optimal_max": Decimal("5000.0"),
            "is_critical": False,
            "is_kpi": True,
        },
    ]
    
    metrics = []
    for data in metrics_data:
        metric = MetricsCatalog(**data)
        db.add(metric)
        metrics.append(metric)
    
    await db.commit()
    return metrics


async def seed_users(db: AsyncSession, factories: list):
    """Создание пользователей"""
    users_data = [
        {
            "email": "admin@factory.kz",
            "password_hash": get_password_hash("admin123"),
            "full_name": "Администратор Системы",
            "position": "Системный администратор",
            "factory_id": factories[0].id,
            "role": "admin",
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "manager@arcelormittal.kz",
            "password_hash": get_password_hash("manager123"),
            "full_name": "Менеджер Завода",
            "position": "Директор производства",
            "factory_id": factories[0].id,
            "role": "manager",
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "engineer@anpz.kz",
            "password_hash": get_password_hash("engineer123"),
            "full_name": "Инженер Технолог",
            "position": "Ведущий инженер",
            "factory_id": factories[1].id,
            "role": "engineer",
            "is_active": True,
            "is_verified": True,
        },
    ]
    
    users = []
    for data in users_data:
        user = User(**data)
        db.add(user)
        users.append(user)
    
    await db.commit()
    return users


async def seed_kpi(db: AsyncSession, factories: list, equipment_list: list):
    """Создание KPI данных"""
    now = datetime.utcnow()
    
    # KPI для заводов
    for factory in factories:
        for i in range(7):  # Последние 7 дней
            date = now - timedelta(days=i)
            kpi = KPICalculation(
                entity_type="factory",
                entity_id=factory.id,
                period_type="daily",
                period_start=date.replace(hour=0, minute=0, second=0),
                period_end=date.replace(hour=23, minute=59, second=59),
                oee_score=Decimal("85.5") + Decimal(str(i * 0.5)),
                availability=Decimal("92.0") + Decimal(str(i * 0.3)),
                performance=Decimal("88.0") + Decimal(str(i * 0.2)),
                quality=Decimal("95.0") + Decimal(str(i * 0.1)),
                total_production=Decimal("10000") + Decimal(str(i * 100)),
                planned_production=Decimal("12000"),
                downtime_minutes=120 - i * 10,
                downtime_percentage=Decimal("8.3") - Decimal(str(i * 0.1)),
                energy_consumption_kwh=Decimal("50000") + Decimal(str(i * 500)),
            )
            db.add(kpi)
    
    # KPI для оборудования
    for equipment in equipment_list:
        for i in range(3):  # Последние 3 дня
            date = now - timedelta(days=i)
            kpi = KPICalculation(
                entity_type="equipment",
                entity_id=equipment.id,
                period_type="daily",
                period_start=date.replace(hour=0, minute=0, second=0),
                period_end=date.replace(hour=23, minute=59, second=59),
                oee_score=Decimal("80.0") + Decimal(str(i * 2)),
                availability=Decimal("90.0") + Decimal(str(i * 1)),
                performance=Decimal("85.0") + Decimal(str(i * 1.5)),
                quality=Decimal("94.0") + Decimal(str(i * 0.5)),
                downtime_minutes=60 - i * 5,
            )
            db.add(kpi)
    
    await db.commit()


async def seed_anomalies(db: AsyncSession, equipment_list: list):
    """Создание аномалий"""
    now = datetime.utcnow()
    
    anomalies_data = [
        {
            "equipment_id": equipment_list[0].id,
            "detected_at": now - timedelta(hours=2),
            "severity": "high",
            "anomaly_score": Decimal("0.85"),
            "expected_value": Decimal("85.0"),
            "actual_value": Decimal("120.0"),
            "deviation_percentage": Decimal("41.2"),
            "anomaly_type": "spike",
            "status": "new",
        },
        {
            "equipment_id": equipment_list[2].id,
            "detected_at": now - timedelta(hours=5),
            "severity": "medium",
            "anomaly_score": Decimal("0.65"),
            "expected_value": Decimal("750.0"),
            "actual_value": Decimal("650.0"),
            "deviation_percentage": Decimal("13.3"),
            "anomaly_type": "drop",
            "status": "acknowledged",
        },
    ]
    
    for data in anomalies_data:
        anomaly = Anomaly(**data)
        db.add(anomaly)
    
    await db.commit()


async def seed_recommendations(db: AsyncSession, factories: list, equipment_list: list):
    """Создание рекомендаций"""
    recommendations_data = [
        {
            "target_type": "equipment",
            "target_id": equipment_list[0].id,
            "category": "maintenance",
            "priority": "high",
            "title": "Требуется плановое обслуживание прокатного стана",
            "description": "Рекомендуется провести плановое ТО в течение 7 дней",
            "expected_benefit": "Предотвращение внепланового простоя",
            "estimated_savings": Decimal("500000"),
            "savings_currency": "KZT",
            "payback_period_days": 0,
            "implementation_cost": Decimal("100000"),
            "implementation_time_hours": 8,
            "source": "ml_model",
            "status": "new",
        },
        {
            "target_type": "factory",
            "target_id": factories[0].id,
            "category": "energy_saving",
            "priority": "medium",
            "title": "Оптимизация энергопотребления",
            "description": "Снижение энергопотребления на 15% через оптимизацию режимов работы",
            "expected_benefit": "Экономия 2.5 млн тг/месяц",
            "estimated_savings": Decimal("2500000"),
            "savings_currency": "KZT",
            "payback_period_days": 30,
            "implementation_cost": Decimal("500000"),
            "implementation_time_hours": 40,
            "source": "rule_engine",
            "status": "reviewing",
        },
    ]
    
    for data in recommendations_data:
        recommendation = Recommendation(**data)
        db.add(recommendation)
    
    await db.commit()


async def main():
    """Основная функция для заполнения БД"""
    print("🌱 Начало заполнения базы данных...")
    
    # Создание таблиц
    await create_tables()
    print("✅ Таблицы созданы")
    
    async with AsyncSessionLocal() as db:
        # Отрасли
        industries = await seed_industries(db)
        print(f"✅ Создано отраслей: {len(industries)}")
        
        # Заводы
        factories = await seed_factories(db, industries)
        print(f"✅ Создано заводов: {len(factories)}")
        
        # Типы оборудования
        equipment_types = await seed_equipment_types(db)
        print(f"✅ Создано типов оборудования: {len(equipment_types)}")
        
        # Оборудование
        equipment_list = await seed_equipment(db, factories, equipment_types)
        print(f"✅ Создано оборудования: {len(equipment_list)}")
        
        # Метрики
        metrics = await seed_metrics_catalog(db)
        print(f"✅ Создано метрик: {len(metrics)}")
        
        # Пользователи
        users = await seed_users(db, factories)
        print(f"✅ Создано пользователей: {len(users)}")
        
        # KPI
        await seed_kpi(db, factories, equipment_list)
        print("✅ Созданы KPI данные")
        
        # Аномалии
        await seed_anomalies(db, equipment_list)
        print("✅ Созданы аномалии")
        
        # Рекомендации
        await seed_recommendations(db, factories, equipment_list)
        print("✅ Созданы рекомендации")
        
        # Импорт расширенных функций seed
        from app.db.seed_extended import (
            seed_subscriptions, seed_production_cycles, seed_maintenance_logs,
            seed_external_systems, seed_report_templates, seed_generated_reports,
            seed_access_rights, seed_audit_logs
        )
        
        # Подписки
        await seed_subscriptions(db, factories)
        print("✅ Созданы подписки")
        
        # Производственные циклы
        await seed_production_cycles(db, factories, equipment_list)
        print("✅ Созданы производственные циклы")
        
        # Обслуживание
        await seed_maintenance_logs(db, equipment_list)
        print("✅ Создан журнал обслуживания")
        
        # Интеграции
        await seed_external_systems(db, factories)
        print("✅ Созданы внешние системы")
        
        # Шаблоны отчетов
        await seed_report_templates(db, users)
        print("✅ Созданы шаблоны отчетов")
        
        # Сгенерированные отчеты
        await seed_generated_reports(db, factories, users)
        print("✅ Созданы сгенерированные отчеты")
        
        # Права доступа
        await seed_access_rights(db, users)
        print("✅ Созданы права доступа")
        
        # Аудит логи
        await seed_audit_logs(db, users)
        print("✅ Созданы аудит логи")
    
    print("🎉 База данных успешно заполнена!")


if __name__ == "__main__":
    asyncio.run(main())

