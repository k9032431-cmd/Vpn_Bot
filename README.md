# ArsiCloudBot

Telegram-бот для управления VPN: ноды, облачные подключения, аккаунты,
шифрование данных. Сделан на Python + [aiogram 3](https://docs.aiogram.dev/).

Сейчас реализовано:
- команда `/start` с приветствием и главным меню;
- кнопки-заглушки: **Node**, **Cloud VPN**, **Cloud Account**,
  **Crypt/Decrypt**, **Language**, **Info**, **SOS** (каждая открывает свой
  экран с кнопкой "Назад" — функциональность будет добавляться дальше).

## Структура проекта

```
bot/
  main.py            # точка входа, запуск polling
  config.py           # загрузка BOT_TOKEN из .env
  handlers/
    start.py          # обработчик /start
    menu.py            # обработчики кнопок меню
  keyboards/
    main_menu.py       # инлайн-клавиатуры
  texts/
    ru.py               # тексты сообщений
Dockerfile
docker-compose.yml
deploy.sh              # первичная установка на сервер
update.sh              # обновление бота после изменений в GitHub
```

## 1. Получить токен бота

1. Напишите [@BotFather](https://t.me/BotFather) в Telegram.
2. Команда `/newbot`, задайте имя и username.
3. Скопируйте выданный токен — он понадобится ниже.

## 2. Установка на сервер (VPS) через Docker — рекомендуемый способ

Это самый простой вариант: не нужно вручную ставить Python и зависимости,
а повторная установка/обновление — это одна команда. Подходит, чтобы
тестировать бота каждый раз после внесения изменений.

### Первый запуск на чистом сервере

Подключитесь к серверу по SSH (Ubuntu/Debian) и выполните:

```bash
curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/vpn_bot/claude/arsicloudbot-menu-setup-ueqrl6/deploy.sh | bash
```

Скрипт сам:
1. установит Docker и Docker Compose, если их нет;
2. склонирует репозиторий в `~/arsicloudbot`;
3. создаст файл `.env` из примера и попросит вписать в него `BOT_TOKEN`;
4. соберёт образ и запустит бота в фоне (`restart: unless-stopped`, то есть
   бот сам поднимется после перезагрузки сервера).

Если предпочитаете руками — то же самое пошагово:

```bash
git clone --branch claude/arsicloudbot-menu-setup-ueqrl6 \
  https://github.com/k9032431-cmd/vpn_bot.git ~/arsicloudbot
cd ~/arsicloudbot
cp .env.example .env
nano .env               # вписать BOT_TOKEN
docker compose up -d --build
```

Проверить, что бот работает:

```bash
cd ~/arsicloudbot
docker compose logs -f
```

Напишите боту `/start` в Telegram — должно прийти приветствие с меню.

### Повторная установка / обновление после изменений в коде

Когда вы что-то поменяли в боте и запушили в GitHub, на сервере достаточно
одной команды:

```bash
cd ~/arsicloudbot
./update.sh
```

Скрипт подтянет последние изменения из текущей ветки (`git fetch` +
`git reset --hard`) и пересоберёт/перезапустит контейнер. Так можно
тестировать сколько угодно раз — старая версия каждый раз полностью
заменяется новой, никакого "мусора" не остаётся.

Если нужно снести и поставить полностью с нуля — просто удалите папку и
повторите команду установки из первого запуска:

```bash
rm -rf ~/arsicloudbot
curl -fsSL https://raw.githubusercontent.com/k9032431-cmd/vpn_bot/claude/arsicloudbot-menu-setup-ueqrl6/deploy.sh | bash
```

### Полезные команды Docker

```bash
docker compose ps              # статус контейнера
docker compose logs -f         # логи в реальном времени
docker compose restart         # перезапуск без пересборки
docker compose down            # остановить и удалить контейнер
```

## 3. Запуск без Docker (локально, для разработки)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# вписать BOT_TOKEN в .env
python -m bot.main
```

## Переменные окружения

| Переменная  | Описание                                  |
|-------------|--------------------------------------------|
| `BOT_TOKEN` | Токен Telegram-бота от @BotFather (обязателен) |
