#!/bin/bash

echo "🔍 Проверка зависимостей проекта..."
echo ""

# Проверка Python
echo "📦 Python:"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "  ✅ Python $PYTHON_VERSION установлен"
    # Проверка версии >= 3.11
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        echo "  ✅ Версия соответствует требованиям (>= 3.11)"
    else
        echo "  ⚠️  Версия ниже требуемой (нужна >= 3.11)"
    fi
else
    echo "  ❌ Python не установлен"
    echo "     Установите через: brew install python@3.11"
fi

echo ""

# Проверка Node.js
echo "📦 Node.js:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2)
    echo "  ✅ Node.js v$NODE_VERSION установлен"
    # Проверка версии >= 18
    if node -e "process.exit(parseInt(process.version.slice(1).split('.')[0]) >= 18 ? 0 : 1)"; then
        echo "  ✅ Версия соответствует требованиям (>= 18)"
    else
        echo "  ⚠️  Версия ниже требуемой (нужна >= 18)"
    fi
else
    echo "  ❌ Node.js не установлен"
    echo "     Установите через: brew install node"
fi

echo ""

# Проверка Docker
echo "📦 Docker:"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo "  ✅ Docker $DOCKER_VERSION установлен"
    
    # Проверка, запущен ли Docker daemon
    if docker info &> /dev/null; then
        echo "  ✅ Docker daemon запущен"
    else
        echo "  ⚠️  Docker daemon не запущен"
        echo "     Запустите Docker Desktop из Applications"
    fi
else
    echo "  ❌ Docker не установлен"
    echo "     Установите Docker Desktop:"
    echo "     1. brew install --cask docker"
    echo "     2. Откройте Docker Desktop из Applications"
    echo "     3. Запустите приложение и дождитесь полной загрузки"
fi

echo ""

# Проверка Docker Compose
echo "📦 Docker Compose:"
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    if docker compose version &> /dev/null; then
        COMPOSE_VERSION=$(docker compose version | cut -d' ' -f4)
        echo "  ✅ Docker Compose $COMPOSE_VERSION установлен (плагин)"
    else
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
        echo "  ✅ Docker Compose $COMPOSE_VERSION установлен (standalone)"
    fi
else
    echo "  ⚠️  Docker Compose не найден (обычно входит в Docker Desktop)"
fi

echo ""

# Проверка PostgreSQL (опционально, если не используется Docker)
echo "📦 PostgreSQL (опционально):"
if command -v psql &> /dev/null; then
    PSQL_VERSION=$(psql --version | cut -d' ' -f3)
    echo "  ✅ PostgreSQL $PSQL_VERSION установлен"
    echo "  ℹ️  Можно использовать локальный PostgreSQL или Docker"
else
    echo "  ℹ️  PostgreSQL не установлен (будет использоваться через Docker)"
fi

echo ""
echo "✅ Проверка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "   1. Если Docker не установлен, установите его: brew install --cask docker"
echo "   2. Запустите Docker Desktop из Applications"
echo "   3. Запустите базу данных: docker-compose up -d"
echo "   4. Следуйте инструкциям в SETUP.md"

