#!/bin/bash

# 🚀 Скрипт быстрого запуска проекта
# Национальная платформа промышленной аналитики Казахстана

set -e

echo "🏭 Запуск платформы промышленной аналитики Казахстана"
echo "=================================================="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция проверки команды
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 не установлен${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 установлен${NC}"
        return 0
    fi
}

# Проверка зависимостей
echo "📋 Проверка зависимостей..."
check_command python3 || exit 1
check_command node || exit 1
check_command docker || exit 1
check_command docker-compose || exit 1
echo ""

# Проверка версий
echo "📊 Версии:"
python3 --version
node --version
docker --version
echo ""

# Шаг 1: Запуск Docker контейнеров
echo -e "${YELLOW}🐳 Шаг 1: Запуск PostgreSQL и Redis...${NC}"
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Контейнеры уже запущены${NC}"
else
    docker-compose up -d
    echo -e "${GREEN}✅ Контейнеры запущены${NC}"
    echo "   Ожидание готовности PostgreSQL (10 секунд)..."
    sleep 10
fi
echo ""

# Шаг 2: Backend setup
echo -e "${YELLOW}⚙️  Шаг 2: Настройка Backend...${NC}"
cd backend

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "   Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
if [ ! -f "venv/.deps_installed" ]; then
    echo "   Установка Python зависимостей..."
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    touch venv/.deps_installed
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
else
    echo -e "${GREEN}✅ Зависимости уже установлены${NC}"
fi

# Миграции БД
echo "   Применение миграций БД..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
alembic upgrade head -q 2>/dev/null || alembic upgrade head
echo -e "${GREEN}✅ Миграции применены${NC}"

# Заполнение тестовыми данными (если нужно)
if [ ! -f ".seed_done" ]; then
    echo "   Заполнение БД тестовыми данными..."
    python3 -c "import asyncio; from app.db.seed import main; asyncio.run(main())" 2>/dev/null || true
    touch .seed_done
    echo -e "${GREEN}✅ Тестовые данные добавлены${NC}"
else
    echo -e "${GREEN}✅ Тестовые данные уже есть${NC}"
fi

cd ..
echo ""

# Шаг 3: Frontend setup
echo -e "${YELLOW}🎨 Шаг 3: Настройка Frontend...${NC}"
cd frontend

# Установка зависимостей
if [ ! -d "node_modules" ]; then
    echo "   Установка Node.js зависимостей..."
    npm install --silent
    echo -e "${GREEN}✅ Зависимости установлены${NC}"
else
    echo -e "${GREEN}✅ Зависимости уже установлены${NC}"
fi

cd ..
echo ""

# Шаг 4: Запуск сервисов
echo -e "${YELLOW}🚀 Шаг 4: Запуск сервисов...${NC}"
echo ""
echo -e "${GREEN}✅ Все готово!${NC}"
echo ""
echo "📝 Для запуска выполните следующие команды:"
echo ""
echo "1️⃣  Backend (в первом терминале):"
echo -e "   ${YELLOW}cd backend${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}"
echo -e "   ${YELLOW}uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload${NC}"
echo ""
echo "2️⃣  Frontend (во втором терминале):"
echo -e "   ${YELLOW}cd frontend${NC}"
echo -e "   ${YELLOW}npm run dev${NC}"
echo ""
echo "3️⃣  Или для production сборки:"
echo -e "   ${YELLOW}cd frontend${NC}"
echo -e "   ${YELLOW}npm run build${NC}"
echo -e "   ${YELLOW}npm run preview${NC}"
echo ""
echo "🌐 После запуска:"
echo "   • Backend API:     http://localhost:8000"
echo "   • API Docs:        http://localhost:8000/api/docs"
echo "   • Frontend (dev):  http://localhost:5173"
echo "   • Frontend (prod): http://localhost:4173"
echo "   • Лендинг:         http://localhost:5173/index_landing.html"
echo "   • Вход:            http://localhost:5173/login.html"
echo ""
echo "🔑 Тестовые учетные данные:"
echo "   • admin@factory.kz / admin123 (администратор)"
echo "   • manager@arcelormittal.kz / manager123 (менеджер)"
echo "   • engineer@anpz.kz / engineer123 (инженер)"
echo ""
echo -e "${GREEN}✨ Готово к работе!${NC}"

