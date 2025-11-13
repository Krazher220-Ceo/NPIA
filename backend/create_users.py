"""
Быстрое создание тестовых пользователей
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.factory import Factory
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_test_users():
    """Создание тестовых пользователей"""
    async with AsyncSessionLocal() as db:
        # Проверка существующих пользователей
        existing = await db.scalar(select(User).where(User.email == "admin@factory.kz"))
        if existing:
            print("✅ Пользователи уже существуют")
            return
        
        # Получаем первый завод для привязки
        factory_result = await db.execute(select(Factory).limit(1))
        factory = factory_result.scalar_one_or_none()
        
        if not factory:
            print("❌ Нет заводов в БД. Сначала запустите полный seed скрипт.")
            return
        
        # Создание пользователей
        users_data = [
            {
                "email": "admin@factory.kz",
                "password_hash": get_password_hash("admin123"),
                "full_name": "Администратор Системы",
                "position": "Системный администратор",
                "factory_id": factory.id,
                "role": "admin",
                "is_active": True,
                "is_verified": True,
            },
            {
                "email": "manager@arcelormittal.kz",
                "password_hash": get_password_hash("manager123"),
                "full_name": "Менеджер Завода",
                "position": "Директор производства",
                "factory_id": factory.id,
                "role": "manager",
                "is_active": True,
                "is_verified": True,
            },
            {
                "email": "engineer@anpz.kz",
                "password_hash": get_password_hash("engineer123"),
                "full_name": "Инженер Технолог",
                "position": "Ведущий инженер",
                "factory_id": factory.id,
                "role": "engineer",
                "is_active": True,
                "is_verified": True,
            },
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        await db.commit()
        print("✅ Создано 3 тестовых пользователя:")
        print("   - admin@factory.kz / admin123")
        print("   - manager@arcelormittal.kz / manager123")
        print("   - engineer@anpz.kz / engineer123")

if __name__ == "__main__":
    asyncio.run(create_test_users())

