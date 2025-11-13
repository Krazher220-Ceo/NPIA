#!/bin/bash

# 🔍 Скрипт диагностики сервисов
# Проверяет доступность PostgreSQL, Redis и других компонентов

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           🔍 Диагностика сервисов системы               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Проверка Docker
echo -e "${YELLOW}▶ Проверка Docker...${NC}"
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker запущен"
    docker --version
else
    echo -e "${RED}✗${NC} Docker не запущен или недоступен"
    echo "  Запустите Docker Desktop или выполните: sudo systemctl start docker"
    exit 1
fi
echo ""

# 2. Проверка Docker Compose
echo -e "${YELLOW}▶ Проверка Docker Compose...${NC}"
if command -v docker-compose > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker Compose установлен"
    docker-compose --version
else
    echo -e "${RED}✗${NC} Docker Compose не установлен"
    exit 1
fi
echo ""

# 3. Проверка контейнеров
echo -e "${YELLOW}▶ Проверка Docker контейнеров...${NC}"
POSTGRES_STATUS=$(docker inspect -f '{{.State.Status}}' factory_analytics_db 2>/dev/null || echo "not_found")
REDIS_STATUS=$(docker inspect -f '{{.State.Status}}' factory_analytics_redis 2>/dev/null || echo "not_found")

if [ "$POSTGRES_STATUS" == "running" ]; then
    echo -e "${GREEN}✓${NC} PostgreSQL: running"
else
    echo -e "${RED}✗${NC} PostgreSQL: $POSTGRES_STATUS"
    echo "  Запустите: docker-compose up -d postgres"
fi

if [ "$REDIS_STATUS" == "running" ]; then
    echo -e "${GREEN}✓${NC} Redis: running"
else
    echo -e "${RED}✗${NC} Redis: $REDIS_STATUS"
    echo "  Запустите: docker-compose up -d redis"
fi
echo ""

# 4. Проверка портов
echo -e "${YELLOW}▶ Проверка портов...${NC}"

check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Порт $port ($service): открыт"
    else
        echo -e "${RED}✗${NC} Порт $port ($service): закрыт"
    fi
}

check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 8000 "Backend API"
check_port 4173 "Frontend (prod)"
check_port 5173 "Frontend (dev)"
echo ""

# 5. Проверка подключения к PostgreSQL
echo -e "${YELLOW}▶ Проверка подключения к PostgreSQL...${NC}"
if [ "$POSTGRES_STATUS" == "running" ]; then
    if docker exec factory_analytics_db pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} PostgreSQL принимает подключения"
        
        # Проверка существования БД
        DB_EXISTS=$(docker exec factory_analytics_db psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='factory_analytics'" 2>/dev/null)
        if [ "$DB_EXISTS" == "1" ]; then
            echo -e "${GREEN}✓${NC} База данных factory_analytics существует"
            
            # Подсчет таблиц
            TABLE_COUNT=$(docker exec factory_analytics_db psql -U postgres -d factory_analytics -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null)
            echo -e "${GREEN}✓${NC} Количество таблиц в БД: $TABLE_COUNT"
        else
            echo -e "${YELLOW}⚠${NC} База данных factory_analytics не существует"
            echo "  Запустите миграции: cd backend && alembic upgrade head"
        fi
    else
        echo -e "${RED}✗${NC} PostgreSQL не принимает подключения"
    fi
else
    echo -e "${RED}✗${NC} PostgreSQL контейнер не запущен"
fi
echo ""

# 6. Проверка подключения к Redis
echo -e "${YELLOW}▶ Проверка подключения к Redis...${NC}"
if [ "$REDIS_STATUS" == "running" ]; then
    if docker exec factory_analytics_redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis работает корректно"
    else
        echo -e "${RED}✗${NC} Redis не отвечает на ping"
    fi
else
    echo -e "${RED}✗${NC} Redis контейнер не запущен"
fi
echo ""

# 7. Проверка Backend API (если запущен)
echo -e "${YELLOW}▶ Проверка Backend API...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    HEALTH_CHECK=$(curl -s http://localhost:8000/health 2>/dev/null)
    if [ "$HEALTH_CHECK" == '{"status":"healthy"}' ]; then
        echo -e "${GREEN}✓${NC} Backend API работает (http://localhost:8000)"
        echo -e "${GREEN}✓${NC} Health check: OK"
    else
        echo -e "${YELLOW}⚠${NC} Backend API запущен, но health check не прошёл"
        echo "  Ответ: $HEALTH_CHECK"
    fi
else
    echo -e "${YELLOW}⚠${NC} Backend API не запущен"
    echo "  Запустите: cd backend && source venv/bin/activate && uvicorn app.main:app"
fi
echo ""

# 8. Проверка Frontend (если запущен)
echo -e "${YELLOW}▶ Проверка Frontend...${NC}"
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend (dev) работает (http://localhost:5173)"
elif lsof -Pi :4173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend (prod) работает (http://localhost:4173)"
else
    echo -e "${YELLOW}⚠${NC} Frontend не запущен"
    echo "  Dev: cd frontend && npm run dev"
    echo "  Prod: cd frontend && npm run build && npm run preview"
fi
echo ""

# 9. Итоговый статус
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Итоговый статус                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$POSTGRES_STATUS" == "running" ] && [ "$REDIS_STATUS" == "running" ]; then
    echo -e "${GREEN}✓ Инфраструктура (Docker): OK${NC}"
else
    echo -e "${RED}✗ Инфраструктура (Docker): ТРЕБУЕТ ВНИМАНИЯ${NC}"
fi

if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend: Запущен${NC}"
else
    echo -e "${YELLOW}⚠ Backend: Не запущен${NC}"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 || lsof -Pi :4173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend: Запущен${NC}"
else
    echo -e "${YELLOW}⚠ Frontend: Не запущен${NC}"
fi

echo ""
echo -e "${BLUE}💡 Для запуска используйте:${NC}"
echo "   • Всё сразу: ./start_production.sh"
echo "   • Только Docker: docker-compose up -d"
echo "   • Остановка: ./stop_production.sh"
echo ""

