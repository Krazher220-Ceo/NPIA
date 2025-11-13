#!/bin/bash

echo "🐳 Установка Docker Desktop..."
echo ""

# Проверка, установлен ли Docker Desktop
if [ -d "/Applications/Docker.app" ]; then
    echo "✅ Docker Desktop уже установлен в /Applications/Docker.app"
    echo ""
    echo "📝 Следующие шаги:"
    echo "   1. Откройте Docker Desktop из Applications:"
    echo "      open -a Docker"
    echo ""
    echo "   2. Дождитесь полной загрузки (иконка Docker в строке меню перестанет анимироваться)"
    echo ""
    echo "   3. Проверьте установку:"
    echo "      docker --version"
    echo "      docker compose version"
    echo ""
    echo "   4. Запустите базу данных проекта:"
    echo "      docker-compose up -d"
else
    echo "❌ Docker Desktop не найден"
    echo ""
    echo "Установка через Homebrew (требует пароль администратора):"
    echo "  brew install --cask docker"
    echo ""
    echo "Или скачайте вручную с https://www.docker.com/products/docker-desktop/"
fi

