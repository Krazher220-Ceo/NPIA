#!/bin/bash
# Скрипт для запуска всего проекта

echo "🚀 Запуск проекта промышленной аналитики..."
echo ""

# Проверка Docker
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker не запущен. Запустите Docker Desktop и попробуйте снова."
    exit 1
fi

# Запуск базы данных
echo "📦 Запуск базы данных..."
docker-compose up -d

# Ожидание готовности БД
echo "⏳ Ожидание готовности PostgreSQL..."
sleep 5

# Проверка backend
echo ""
echo "🔍 Проверка backend..."
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Backend не запущен"
    echo "   Запустите в отдельном терминале:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   uvicorn app.main:app --reload"
else
    echo "✅ Backend работает"
fi

# Проверка frontend
echo ""
echo "🔍 Проверка frontend..."
if ! curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "⚠️  Frontend не запущен"
    echo "   Запустите в отдельном терминале:"
    echo "   cd frontend"
    echo "   npm run dev"
else
    echo "✅ Frontend работает"
fi

echo ""
echo "✅ Готово!"
echo ""
echo "📱 Откройте в браузере:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/docs"
echo ""
echo "🔑 Тестовые учетные данные:"
echo "   Email: admin@factory.kz"
echo "   Пароль: admin123"

