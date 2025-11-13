#!/bin/bash

# 🛑 Остановка production сервисов
# Национальная платформа промышленной аналитики Казахстана

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🛑 Остановка сервисов...${NC}"
echo ""

# Остановка Backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓${NC} Backend остановлен (PID: $BACKEND_PID)"
        rm backend.pid
    else
        echo -e "${YELLOW}⚠${NC} Backend уже не запущен"
        rm backend.pid
    fi
else
    echo -e "${YELLOW}⚠${NC} PID файл backend не найден"
fi

# Остановка Frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✓${NC} Frontend остановлен (PID: $FRONTEND_PID)"
        rm frontend.pid
    else
        echo -e "${YELLOW}⚠${NC} Frontend уже не запущен"
        rm frontend.pid
    fi
else
    echo -e "${YELLOW}⚠${NC} PID файл frontend не найден"
fi

# Остановка Docker контейнеров (опционально)
read -p "Остановить Docker контейнеры (PostgreSQL, Redis)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose down
    echo -e "${GREEN}✓${NC} Docker контейнеры остановлены"
fi

echo ""
echo -e "${GREEN}✨ Все сервисы остановлены${NC}"

