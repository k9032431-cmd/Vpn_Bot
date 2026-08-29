#!/usr/bin/env bash
# Первичная установка бота на чистый сервер (Ubuntu/Debian).
# Использование:
#   curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/Vpn_Bot/<BRANCH>/deploy.sh | bash
# или, если репозиторий уже склонирован:
#   ./deploy.sh
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/k9032431-cmd/Vpn_Bot.git}"
BRANCH="${BRANCH:-claude/arsicloudbot-menu-setup-ueqrl6}"
APP_DIR="${APP_DIR:-$HOME/arsicloudbot}"

echo "==> Проверяю Docker..."
if ! command -v docker &> /dev/null; then
    echo "Docker не найден, устанавливаю..."
    curl -fsSL https://get.docker.com | sh
fi

if ! docker compose version &> /dev/null; then
    echo "Docker Compose plugin не найден, устанавливаю..."
    sudo apt-get update -y
    sudo apt-get install -y docker-compose-plugin
fi

if [ -d "$APP_DIR/.git" ]; then
    echo "==> Репозиторий уже склонирован в $APP_DIR, обновляю..."
    cd "$APP_DIR"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git reset --hard "origin/$BRANCH"
else
    echo "==> Клонирую репозиторий в $APP_DIR..."
    git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
    cd "$APP_DIR"
fi

if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "!!! Создан файл .env — впишите в него BOT_TOKEN, полученный от @BotFather:"
    echo "    nano $APP_DIR/.env"
    echo ""
    read -rp "Нажмите Enter после того, как впишете токен и сохраните файл..." _
fi

echo "==> Собираю образ и запускаю бота..."
docker compose up -d --build

echo ""
echo "Готово! Бот запущен."
echo "Логи:      cd $APP_DIR && docker compose logs -f"
echo "Обновить:  cd $APP_DIR && ./update.sh"
