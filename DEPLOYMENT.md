# 🚀 Руководство по развертыванию в production

## 📋 Содержание

1. [Подготовка сервера](#подготовка-сервера)
2. [Быстрый запуск](#быстрый-запуск)
3. [Ручное развертывание](#ручное-развертывание)
4. [Настройка безопасности](#настройка-безопасности)
5. [Мониторинг](#мониторинг)
6. [Резервное копирование](#резервное-копирование)

---

## Подготовка сервера

### Требования к серверу

**Минимальные требования:**
- OS: Ubuntu 20.04+ / CentOS 8+ / macOS
- CPU: 2 ядра
- RAM: 4 GB
- Disk: 20 GB SSD
- Python 3.11+
- Node.js 18+
- Docker + Docker Compose

**Рекомендуемые требования для production:**
- OS: Ubuntu 22.04 LTS
- CPU: 4+ ядра
- RAM: 8+ GB
- Disk: 50+ GB SSD
- PostgreSQL 15+ (может быть в Docker или внешний)
- Redis 7+
- Nginx (reverse proxy)
- SSL сертификат

### Установка зависимостей

#### Ubuntu/Debian

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Python 3.11+
sudo apt install -y python3 python3-pip python3-venv

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose
sudo apt install -y docker-compose-plugin

# Git (если нужно)
sudo apt install -y git
```

#### macOS

```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 3
brew install python@3.11

# Node.js
brew install node@18

# Docker Desktop
# Скачать с https://www.docker.com/products/docker-desktop
```

---

## Быстрый запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd 1
```

### 2. Настройка переменных окружения

```bash
# Скопируйте шаблон
cp env.template backend/.env

# Отредактируйте .env файл
nano backend/.env
```

**Важно:** Измените следующие параметры для production:
- `SECRET_KEY` - используйте сильный случайный ключ (минимум 32 символа)
- `DATABASE_URL` - укажите реальные учетные данные БД
- `CORS_ORIGINS` - укажите реальные домены вашего приложения

### 3. Автоматический запуск

```bash
# Сделайте скрипт исполняемым
chmod +x start_production.sh stop_production.sh

# Запустите платформу
./start_production.sh
```

Скрипт автоматически:
- ✅ Проверит все зависимости
- ✅ Запустит PostgreSQL и Redis в Docker
- ✅ Установит Python зависимости
- ✅ Применит миграции БД
- ✅ Заполнит тестовыми данными
- ✅ Соберет frontend для production
- ✅ Запустит Backend и Frontend

### 4. Проверка работы

Откройте в браузере:
- Frontend: http://localhost:4173
- API Docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

### 5. Остановка

```bash
./stop_production.sh
```

---

## Ручное развертывание

Если автоматический скрипт не подходит, следуйте этой инструкции:

### Шаг 1: Запуск БД

```bash
# Через Docker
docker-compose up -d

# Проверка
docker-compose ps
```

### Шаг 2: Backend

```bash
cd backend

# Виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Зависимости
pip install --upgrade pip
pip install -r requirements.txt

# Миграции
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
alembic upgrade head

# Тестовые данные (опционально)
python3 -c "import asyncio; from app.db.seed import main; asyncio.run(main())"

# Запуск
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Для production с Gunicorn:
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Шаг 3: Frontend

```bash
cd frontend

# Зависимости
npm install

# Production сборка
npm run build

# Запуск preview
npm run preview -- --host 0.0.0.0
```

---

## Настройка безопасности

### 1. Firewall

```bash
# Ubuntu UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 2. Nginx Reverse Proxy

Создайте `/etc/nginx/sites-available/factory-analytics`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:4173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активация:

```bash
sudo ln -s /etc/nginx/sites-available/factory-analytics /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL сертификат (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Systemd сервисы

**Backend service** `/etc/systemd/system/factory-backend.service`:

```ini
[Unit]
Description=Factory Analytics Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project/backend
Environment="PATH=/path/to/project/backend/venv/bin"
ExecStart=/path/to/project/backend/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Активация:

```bash
sudo systemctl daemon-reload
sudo systemctl enable factory-backend
sudo systemctl start factory-backend
sudo systemctl status factory-backend
```

---

## Мониторинг

### Логи

```bash
# Backend логи
tail -f backend.log

# Frontend логи
tail -f frontend.log

# Docker логи
docker-compose logs -f

# Systemd логи
sudo journalctl -u factory-backend -f
```

### Проверка здоровья

```bash
# Backend health check
curl http://localhost:8000/health

# База данных
docker exec -it factory_analytics_db psql -U postgres -c "SELECT count(*) FROM users;"

# Redis
docker exec -it factory_analytics_redis redis-cli ping
```

---

## Резервное копирование

### База данных

```bash
# Создание бэкапа
docker exec factory_analytics_db pg_dump -U postgres factory_analytics > backup_$(date +%Y%m%d_%H%M%S).sql

# Восстановление
docker exec -i factory_analytics_db psql -U postgres factory_analytics < backup_20250113_120000.sql
```

### Автоматический бэкап (cron)

Создайте `/usr/local/bin/factory-backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/factory-analytics"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# БД
docker exec factory_analytics_db pg_dump -U postgres factory_analytics > $BACKUP_DIR/db_$DATE.sql

# Удаление старых бэкапов (>7 дней)
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
```

Добавьте в crontab (`crontab -e`):

```bash
0 2 * * * /usr/local/bin/factory-backup.sh
```

---

## Обновление приложения

```bash
# Остановка сервисов
./stop_production.sh

# Обновление кода
git pull origin main

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
cd ..

# Frontend
cd frontend
npm install
npm run build
cd ..

# Запуск
./start_production.sh
```

---

## Troubleshooting

### Backend не запускается

1. Проверьте логи: `cat backend.log`
2. Проверьте БД: `docker ps | grep postgres`
3. Проверьте миграции: `cd backend && alembic current`

### Frontend не загружается

1. Проверьте логи: `cat frontend.log`
2. Проверьте сборку: `cd frontend && npm run build`
3. Проверьте порт 4173: `lsof -i :4173`

### Ошибки БД

1. Проверьте подключение: `docker exec -it factory_analytics_db psql -U postgres`
2. Проверьте миграции: `alembic history`
3. Пересоздайте БД: `docker-compose down -v && docker-compose up -d`

---

## Контакты

По вопросам развертывания:
- Email: Krazher220@icloud.com
- Телефон: +7 (705) 669-76-77

---

**Последнее обновление:** 13 января 2025
**Версия документа:** 1.0

