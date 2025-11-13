#!/bin/bash

# 🔄 Скрипт перезапуска сервисов с применением изменений
# Промышленная аналитика Казахстана

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🔄 Перезапуск сервисов с обновлениями          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

print_status() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Остановка текущих процессов
print_status "Остановка текущих процессов..."

# Остановка по PID файлам
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
        print_success "Backend остановлен (PID: $BACKEND_PID)"
        rm backend.pid
    fi
fi

if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
        print_success "Frontend остановлен (PID: $FRONTEND_PID)"
        rm frontend.pid
    fi
fi

# Остановка процессов по имени
pkill -f "uvicorn app.main:app" 2>/dev/null && print_success "Остановлены процессы uvicorn" || true
pkill -f "vite preview" 2>/dev/null && print_success "Остановлены процессы vite preview" || true

# Проверка и освобождение портов
print_status "Проверка портов..."

# Порт 8000 (Backend)
BACKEND_PORT_PID=$(lsof -ti :8000 2>/dev/null || echo "")
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo "   Порт 8000 занят процессом $BACKEND_PORT_PID, останавливаем..."
    kill $BACKEND_PORT_PID 2>/dev/null || true
    sleep 1
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

sleep 2

echo ""

# 2. Пересборка Frontend
print_status "Пересборка Frontend с обновлениями..."
cd frontend
npm run build
print_success "Frontend пересобран"
cd ..
echo ""

# 3. Перезапуск Backend
print_status "Перезапуск Backend..."
cd backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
cd ..
sleep 3

if ps -p $BACKEND_PID > /dev/null; then
    print_success "Backend запущен (PID: $BACKEND_PID)"
else
    print_error "Не удалось запустить Backend"
    cat backend.log
    exit 1
fi
echo ""

# 4. Перезапуск Frontend Preview
print_status "Перезапуск Frontend Preview..."
cd frontend
nohup npm run preview -- --host > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..
sleep 3

if ps -p $FRONTEND_PID > /dev/null; then
    print_success "Frontend запущен (PID: $FRONTEND_PID)"
else
    print_error "Не удалось запустить Frontend"
    cat frontend.log
    exit 1
fi
echo ""

# 5. Проверка работоспособности
print_status "Проверка работоспособности..."

# Backend health check
sleep 2
HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null)
if [ "$HEALTH_CHECK" == '{"status":"healthy"}' ]; then
    print_success "Backend API работает корректно"
else
    print_error "Backend API не отвечает корректно"
    echo "   Ответ: $HEALTH_CHECK"
fi

# Frontend check
if curl -s http://localhost:4173 > /dev/null 2>&1; then
    print_success "Frontend доступен"
else
    print_error "Frontend недоступен"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✨ Сервисы успешно перезапущены! ✨            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}🌐 Доступные сервисы:${NC}"
echo -e "   • Backend API:       ${BLUE}http://localhost:8000${NC}"
echo -e "   • API Documentation: ${BLUE}http://localhost:8000/api/docs${NC}"
echo -e "   • Frontend:          ${BLUE}http://localhost:4173${NC}"
echo -e "   • Вход в систему:    ${BLUE}http://localhost:4173/login.html${NC}"
echo ""
echo -e "${YELLOW}📊 Управление:${NC}"
echo "   • Логи Backend:  tail -f backend.log"
echo "   • Логи Frontend: tail -f frontend.log"
echo "   • Диагностика:   ./check_services.sh"
echo "   • Остановка:     ./stop_production.sh"
echo ""

