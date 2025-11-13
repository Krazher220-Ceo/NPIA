#!/bin/bash
# Скрипт для создания тестовых пользователей

echo "🔐 Создание тестовых пользователей..."

FACTORY_ID=$(docker exec factory_analytics_db psql -U postgres -d factory_analytics -t -c "SELECT id FROM factories LIMIT 1;" | tr -d ' ')

if [ -z "$FACTORY_ID" ]; then
    echo "❌ Нет заводов в БД. Сначала запустите seed скрипт."
    exit 1
fi

# Генерируем хеши паролей
cd "$(dirname "$0")"
ADMIN_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())")
MANAGER_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'manager123', bcrypt.gensalt()).decode())")
ENGINEER_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'engineer123', bcrypt.gensalt()).decode())")

# Создаем пользователей
docker exec factory_analytics_db psql -U postgres -d factory_analytics << EOF
INSERT INTO users (id, email, password_hash, full_name, position, factory_id, role, is_active, is_verified, language, timezone)
VALUES 
    (gen_random_uuid(), 'admin@factory.kz', '$ADMIN_HASH', 'Администратор Системы', 'Системный администратор', '$FACTORY_ID', 'admin', true, true, 'ru', 'Asia/Almaty')
    ON CONFLICT (email) DO NOTHING,
    (gen_random_uuid(), 'manager@arcelormittal.kz', '$MANAGER_HASH', 'Менеджер Завода', 'Директор производства', '$FACTORY_ID', 'manager', true, true, 'ru', 'Asia/Almaty')
    ON CONFLICT (email) DO NOTHING,
    (gen_random_uuid(), 'engineer@anpz.kz', '$ENGINEER_HASH', 'Инженер Технолог', 'Ведущий инженер', '$FACTORY_ID', 'engineer', true, true, 'ru', 'Asia/Almaty')
    ON CONFLICT (email) DO NOTHING;
EOF

echo "✅ Пользователи созданы!"
echo ""
echo "Тестовые учетные данные:"
echo "  - admin@factory.kz / admin123"
echo "  - manager@arcelormittal.kz / manager123"
echo "  - engineer@anpz.kz / engineer123"

