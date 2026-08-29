"""Единое место для премиум-эмодзи Telegram.

Как подключить свои премиум-эмодзи:
  1. Перешлите нужный эмодзи в чат с ботом @itisemojibot (или используйте
     Bot API-метод getCustomEmojiStickers) — он пришлёт вам custom_emoji_id,
     это просто длинная цифровая строка.
  2. Вставьте её строкой в словарь IDS ниже, например: "welcome": "5368324170671202286".
  3. Пока значение пустое ("") — используется обычный эмодзи-заглушка из
     вызова e(...), всё работает как есть, ничего больше менять не нужно.

Важно: премиум-эмодзи (тег <tg-emoji>) работает только в ТЕКСТЕ сообщений.
Telegram не позволяет вставлять его в подписи кнопок — там эмодзи всегда
остаются обычными юникод-символами (см. bot/keyboards/*.py).

Ниже — что за текст стоит за каждым ключом (по одному слову):
"""

from __future__ import annotations

IDS: dict[str, str] = {
    # welcome — шапка приветствия в /start
    "welcome": "",
    # node — заголовок и кнопка раздела Node
    "node": "",
    # marzban — заголовок Marzban Node
    "marzban": "",
    # pasarguard — заголовок PasarGuard
    "pasarguard": "",
    # cloud_vpn — раздел Cloud VPN
    "cloud_vpn": "",
    # cloud_account — раздел Cloud Account
    "cloud_account": "",
    # crypt — раздел Crypt/Decrypt
    "crypt": "",
    # language — раздел Language
    "language": "",
    # info — раздел Info
    "info": "",
    # sos — раздел SOS
    "sos": "",
    # success — успешное завершение установки
    "success": "",
    # error — ошибка установки
    "error": "",
    # warning — предупреждения (например, про пароль)
    "warning": "",
    # connect — шаг «подключаюсь по SSH»
    "connect": "",
    # docker — шаги проверки/установки Docker
    "docker": "",
    # files — шаг загрузки файлов конфигурации на сервер
    "files": "",
    # key — сертификат / ключ доступа
    "key": "",
    # launch — шаг запуска контейнера ноды
    "launch": "",
    # globe — IP-адрес / домен сервера
    "globe": "",
}


def e(key: str, fallback: str) -> str:
    """Возвращает премиум-эмодзи (если ID задан в IDS) либо fallback."""
    custom_id = IDS.get(key, "")
    if custom_id:
        return f'<tg-emoji emoji-id="{custom_id}">{fallback}</tg-emoji>'
    return fallback
