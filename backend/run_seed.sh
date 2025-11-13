#!/bin/bash
# Скрипт для заполнения БД тестовыми данными

cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 -c "import asyncio; from app.db.seed import main; asyncio.run(main())"

