"""
Скрипт для добавления только новых данных (подписки, циклы, обслуживание и т.д.)
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.factory import Factory
from app.models.equipment import Equipment
from app.models.user import User
from app.models.integrations import ReportTemplate
from sqlalchemy import select
from app.db.seed_extended import (
    seed_subscriptions, seed_production_cycles, seed_maintenance_logs,
    seed_external_systems, seed_report_templates, seed_generated_reports,
    seed_access_rights, seed_audit_logs
)

async def main():
    """Добавление только новых данных"""
    print("🌱 Добавление новых данных...")
    
    async with AsyncSessionLocal() as db:
        # Получаем существующие данные
        factories_result = await db.execute(select(Factory))
        factories = factories_result.scalars().all()
        
        equipment_result = await db.execute(select(Equipment))
        equipment_list = equipment_result.scalars().all()
        
        users_result = await db.execute(select(User))
        users = users_result.scalars().all()
        
        if not factories:
            print("❌ Нет заводов в БД. Сначала запустите полный seed скрипт.")
            return
        
        print(f"📊 Найдено: {len(factories)} заводов, {len(equipment_list)} оборудования, {len(users)} пользователей")
        
        # Подписки
        try:
            await seed_subscriptions(db, factories)
            print("✅ Созданы подписки")
        except Exception as e:
            print(f"⚠️  Подписки: {str(e)[:100]}")
        
        # Производственные циклы
        try:
            await seed_production_cycles(db, factories, equipment_list)
            print("✅ Созданы производственные циклы")
        except Exception as e:
            print(f"⚠️  Циклы: {str(e)[:100]}")
        
        # Обслуживание
        try:
            await seed_maintenance_logs(db, equipment_list)
            print("✅ Создан журнал обслуживания")
        except Exception as e:
            print(f"⚠️  Обслуживание: {str(e)[:100]}")
        
        # Интеграции
        try:
            await seed_external_systems(db, factories)
            print("✅ Созданы внешние системы")
        except Exception as e:
            print(f"⚠️  Интеграции: {str(e)[:100]}")
        
        # Шаблоны отчетов
        try:
            await seed_report_templates(db, users)
            print("✅ Созданы шаблоны отчетов")
        except Exception as e:
            print(f"⚠️  Шаблоны: {str(e)[:100]}")
        
        # Сгенерированные отчеты
        try:
            await seed_generated_reports(db, factories, users)
            print("✅ Созданы сгенерированные отчеты")
        except Exception as e:
            print(f"⚠️  Отчеты: {str(e)[:100]}")
        
        # Права доступа
        try:
            await seed_access_rights(db, users)
            print("✅ Созданы права доступа")
        except Exception as e:
            print(f"⚠️  Права: {str(e)[:100]}")
        
        # Аудит логи
        try:
            await seed_audit_logs(db, users)
            print("✅ Созданы аудит логи")
        except Exception as e:
            print(f"⚠️  Аудит: {str(e)[:100]}")
    
    print("🎉 Новые данные добавлены!")

if __name__ == "__main__":
    asyncio.run(main())

