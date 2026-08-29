#!/usr/bin/env bash
# Быстрое обновление и перезапуск бота на сервере после того,
# как в GitHub-репозиторий были залиты изменения.
# Запускать из директории с проектом: ./update.sh
set -euo pipefail

cd "$(dirname "$0")"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

echo "==> Получаю последние изменения из GitHub (ветка $CURRENT_BRANCH)..."
git fetch origin "$CURRENT_BRANCH"
git reset --hard "origin/$CURRENT_BRANCH"

echo "==> Пересобираю образ и перезапускаю контейнер..."
docker compose up -d --build

echo "==> Готово. Последние строки логов:"
docker compose logs --tail=30 bot
