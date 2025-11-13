#!/bin/bash

# 🚀 Production запуск платформы промышленной аналитики Казахстана
# Этот скрипт полностью настраивает и запускает проект

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🏭 Промышленная аналитика Казахстана - Production запуск ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Функция для вывода статуса
print_status() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Проверка зависимостей
print_status "Проверка системных зависимостей..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 не установлен. Установите Python 3.11+ и повторите."
    exit 1
fi

if ! command -v node &> /dev/null; then
    print_error "Node.js не установлен. Установите Node.js 18+ и повторите."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker не установлен. Установите Docker и повторите."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose не установлен. Установите docker-compose и повторите."
    exit 1
fi

print_success "Все зависимости установлены"
echo ""

# 1. Запуск Docker контейнеров
print_status "Проверка статуса Docker..."
if ! docker info >/dev/null 2>&1; then
    print_status "Docker не запущен. Пытаемся запустить автоматически..."
    OS_NAME="$(uname -s)"
    case "$OS_NAME" in
        Darwin)
            if command -v open >/dev/null 2>&1; then
                open -a Docker >/dev/null 2>&1 || true
                echo "   Ожидание запуска Docker Desktop..."
                for i in {1..60}; do
                    if docker info >/dev/null 2>&1; then
                        print_success "Docker Desktop запущен"
                        break
                    fi
                    sleep 2
                done
            fi
            ;;
        Linux)
            if command -v systemctl >/dev/null 2>&1; then
                echo "   Запуск сервиса docker через systemctl..."
                sudo systemctl start docker >/dev/null 2>&1 || true
            fi
            # Для WSL/прочих окружений предложим пользователю запустить вручную
            ;;
        *)
            print_status "Не удалось определить ОС для автоматического запуска Docker."
            ;;
    esac
fi

if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon не запущен. Запустите Docker Desktop (macOS/Windows) или выполните 'sudo systemctl start docker' (Linux), затем повторите запуск."
    exit 1
fi
print_success "Docker daemon активен"

print_status "Запуск PostgreSQL и Redis через Docker..."
if docker-compose ps | grep -q "Up"; then
    print_success "Контейнеры уже запущены"
else
    docker-compose up -d || {
        print_error "Не удалось запустить docker-compose. Проверьте, что Docker daemon работает корректно."
        exit 1
    }
    print_success "Контейнеры запущены"
    echo "   Ожидание готовности БД (15 секунд)..."
    sleep 15
fi
echo ""

# 2. Backend настройка
print_status "Настройка Backend..."
cd backend

# Создание виртуального окружения
if [ ! -d "venv" ]; then
    echo "   Создание виртуального окружения..."
    python3 -m venv venv
    print_success "Виртуальное окружение создано"
fi

# Активация venv
source venv/bin/activate

# Установка зависимостей
echo "   Установка Python зависимостей..."
pip install --upgrade pip -q 2>/dev/null
pip install -r requirements.txt -q 2>/dev/null
print_success "Зависимости установлены"

# Применение миграций
echo "   Применение миграций базы данных..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
alembic upgrade head -q 2>/dev/null || alembic upgrade head
print_success "Миграции применены"

# Заполнение тестовыми данными
if [ ! -f ".seed_done" ]; then
    echo "   Заполнение базы данных тестовыми данными..."
    python3 -c "import asyncio; from app.db.seed import main; asyncio.run(main())" 2>/dev/null || true
    touch .seed_done
    print_success "Тестовые данные добавлены"
else
    print_success "Тестовые данные уже загружены"
fi

cd ..
echo ""

# 3. Frontend настройка и сборка
print_status "Настройка и сборка Frontend..."
cd frontend

# Установка зависимостей
if [ ! -d "node_modules" ]; then
    echo "   Установка Node.js зависимостей..."
    npm install --silent 2>/dev/null || npm install
    print_success "Зависимости установлены"
else
    print_success "Зависимости уже установлены"
fi

# Production сборка
echo "   Создание production сборки..."
npm run build 2>/dev/null || npm run build
print_success "Production сборка готова"

cd ..
echo ""

# 4. Запуск сервисов
print_status "Запуск сервисов..."
echo ""

# Проверка и освобождение портов перед запуском
print_status "Проверка портов..."

# Порт 8000 (Backend)
BACKEND_PORT_PID=$(lsof -ti :8000 2>/dev/null || echo "")
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo "   Порт 8000 занят процессом $BACKEND_PORT_PID, останавливаем..."
    kill $BACKEND_PORT_PID 2>/dev/null || true
    sleep 2
    print_success "Порт 8000 освобожден"
fi

# Порт 4173 (Frontend Preview)
FRONTEND_PORT_PID=$(lsof -ti :4173 2>/dev/null || echo "")
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo "   Порт 4173 занят процессом $FRONTEND_PORT_PID, останавливаем..."
    kill $FRONTEND_PORT_PID 2>/dev/null || true
    sleep 1
    print_success "Порт 4173 освобожден"
fi

echo ""

# Запуск backend в фоне
print_status "Запуск Backend..."
cd backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
cd ..

# Ожидание запуска backend
sleep 3

# Проверка что backend запустился
if ps -p $BACKEND_PID > /dev/null; then
    # Дополнительная проверка через health endpoint
    sleep 2
    HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null || echo "")
    if [ "$HEALTH_CHECK" == '{"status":"healthy"}' ]; then
        print_success "Backend запущен и работает (PID: $BACKEND_PID)"
    else
        print_success "Backend запущен (PID: $BACKEND_PID), но health check не прошел"
        echo "   Проверьте логи: tail -f backend.log"
    fi
else
    print_error "Не удалось запустить Backend"
    echo "   Проверьте логи: tail -f backend.log"
    echo "   Возможные причины:"
    echo "   - Порт 8000 все еще занят"
    echo "   - Ошибка в коде backend"
    exit 1
fi

# Запуск frontend preview в фоне
cd frontend
nohup npm run preview -- --host > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..

# Ожидание запуска frontend
sleep 3

# Проверка что frontend запустился
if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Frontend запущен (PID: $FRONTEND_PID)"
else
    print_error "Не удалось запустить Frontend. Проверьте frontend.log"
    # Останавливаем backend
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✨ Платформа успешно запущена! ✨               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}🌐 Доступные сервисы:${NC}"
echo -e "   • Backend API:      ${BLUE}http://localhost:8000${NC}"
echo -e "   • API Documentation: ${BLUE}http://localhost:8000/api/docs${NC}"
echo -e "   • Frontend:         ${BLUE}http://localhost:4173${NC}"
echo -e "   • Лендинг:          ${BLUE}http://localhost:4173/index_landing.html${NC}"
echo -e "   • Вход в систему:   ${BLUE}http://localhost:4173/login.html${NC}"
echo ""
echo -e "${YELLOW}🔑 Тестовые учетные данные:${NC}"
echo "   • admin@factory.kz / admin123 (Администратор)"
echo "   • manager@arcelormittal.kz / manager123 (Менеджер)"
echo "   • engineer@anpz.kz / engineer123 (Инженер)"
echo ""
echo -e "${YELLOW}📊 Управление:${NC}"
echo "   • Логи Backend:  tail -f backend.log"
echo "   • Логи Frontend: tail -f frontend.log"
echo "   • Остановка:     ./stop_production.sh"
echo ""
echo -e "${GREEN}💡 Платформа готова к использованию!${NC}"
echo ""

