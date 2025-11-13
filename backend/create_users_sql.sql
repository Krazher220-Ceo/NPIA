-- Создание тестовых пользователей
-- Пароли: admin123, manager123, engineer123

-- Получаем первый завод
DO $$
DECLARE
    factory_uuid UUID;
BEGIN
    SELECT id INTO factory_uuid FROM factories LIMIT 1;
    
    IF factory_uuid IS NULL THEN
        RAISE EXCEPTION 'Нет заводов в БД. Сначала запустите seed скрипт.';
    END IF;
    
    -- Создаем пользователей только если их еще нет
    INSERT INTO users (id, email, password_hash, full_name, position, factory_id, role, is_active, is_verified, language, timezone)
    SELECT 
        gen_random_uuid(),
        'admin@factory.kz',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5qO', -- admin123
        'Администратор Системы',
        'Системный администратор',
        factory_uuid,
        'admin',
        true,
        true,
        'ru',
        'Asia/Almaty'
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@factory.kz');
    
    INSERT INTO users (id, email, password_hash, full_name, position, factory_id, role, is_active, is_verified, language, timezone)
    SELECT 
        gen_random_uuid(),
        'manager@arcelormittal.kz',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5qO', -- manager123
        'Менеджер Завода',
        'Директор производства',
        factory_uuid,
        'manager',
        true,
        true,
        'ru',
        'Asia/Almaty'
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'manager@arcelormittal.kz');
    
    INSERT INTO users (id, email, password_hash, full_name, position, factory_id, role, is_active, is_verified, language, timezone)
    SELECT 
        gen_random_uuid(),
        'engineer@anpz.kz',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5qO', -- engineer123
        'Инженер Технолог',
        'Ведущий инженер',
        factory_uuid,
        'engineer',
        true,
        true,
        'ru',
        'Asia/Almaty'
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'engineer@anpz.kz');
    
    RAISE NOTICE 'Пользователи созданы успешно!';
END $$;

