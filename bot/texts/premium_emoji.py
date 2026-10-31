"""Единое место для премиум-эмодзи Telegram.

Каждый слот ниже можно настроить без правки кода -- через раздел
"⚙️ Эмодзи" в главном меню бота (виден только админам из ADMIN_IDS):
откройте слот и либо перешлите/отправьте боту сообщение с самим
премиум-эмодзи (бот сам считает его custom_emoji_id из сообщения), либо
введите этот ID вручную, если он уже известен (например, от
@itisemojibot). Изменение действует сразу, без перезапуска бота.

SLOTS ниже -- это ещё и заводские значения по умолчанию (default_id) на
случай, если админ ничего не переопределил: пока для слота нет
переопределения через бота, используется именно это значение, а если
оно тоже пустое -- обычный эмодзи-заглушка (fallback) из того же слота.

Важно: один и тот же ключ слота используется в двух местах --
  - в ТЕКСТЕ сообщений через e(key, fallback) (тег <tg-emoji>);
  - на КНОПКАХ через button_icon(key) (поле icon_custom_emoji_id,
    Bot API 9.4+, см. bot/keyboards/*.py). Показ иконки на кнопке Telegram
    разрешает только если у аккаунта, на который зарегистрирован бот
    (BotFather), есть активная Premium-подписка, либо у бота куплен
    username на Fragment -- иначе иконка на кнопке может не показаться.
"""

from __future__ import annotations

from dataclasses import dataclass

from bot.services import emoji_overrides


@dataclass(frozen=True)
class EmojiSlot:
    key: str
    section: str
    label: str
    fallback: str
    default_id: str = ""


SLOTS: tuple[EmojiSlot, ...] = (
    # ══════════════════════════════════════════════════════════
    # Главное меню (/start)
    # ══════════════════════════════════════════════════════════
    EmojiSlot("welcome", "Главное меню", "Приветствие — шапка /start", "👋", "6008263495932448198"),
    EmojiSlot("node", "Главное меню", "Node — кнопка и заголовки раздела", "🖥", "5974492756494519709"),
    EmojiSlot("panel", "Главное меню", "Panel — кнопка и заголовки раздела", "⚙️", "5974582963692637085"),
    EmojiSlot("profile", "Главное меню", "Профиль — кнопка и заголовок раздела", "👤", "5974048815789903111"),
    EmojiSlot("cloud_vps", "Главное меню", "Cloud VPS — кнопка и список провайдеров", "☁️", "6048537430036844009"),
    EmojiSlot("cloud_account", "Главное меню", "Cloud Account — кнопка раздела", "👤", "5972226216353074147"),
    EmojiSlot("crypt", "Главное меню", "Crypt/Decrypt — кнопка и заголовок раздела", "🔐", "6003424016977628379"),
    EmojiSlot("whois", "Главное меню", "Arsi WhoIs — кнопка и заголовок раздела", "🌐", "5974475701179387553"),
    EmojiSlot("language", "Главное меню", "Язык — заголовок экрана выбора языка", "🌐", "5974056615450513203"),
    EmojiSlot("info", "Главное меню", "Инфо — заголовок раздела", "ℹ️", "5976801477509778431"),
    EmojiSlot("sos", "Главное меню", "SOS — заголовок раздела (без админ-контакта)", "🆘", "5974229895906069525"),

    # ══════════════════════════════════════════════════════════
    # Node — установка ноды (Marzban / PasarGuard)
    # ══════════════════════════════════════════════════════════
    EmojiSlot("connect", "Node", "Подключаюсь по SSH — шаг установки", "🔌", "5926791488200510744"),
    EmojiSlot("docker", "Node", "Docker — проверка/установка Docker и Compose", "🐳", "5929098607192969118"),
    EmojiSlot("files", "Node", "Загрузка файлов — шаг загрузки конфигурации на сервер", "📁", "5931718859366075705"),
    EmojiSlot("key", "Node", "Сертификат/ключ — доступ (PasarGuard) и запрос ключа", "🔑", "5197288647275071607"),
    EmojiSlot("launch", "Node", "Запуск контейнера — финальный шаг установки", "🚀", "5195033767969839232"),
    EmojiSlot("globe", "Node", "IP-адрес сервера — шаг ввода IP/домена ноды", "🌍", "5447410659077661506"),
    EmojiSlot("marzban", "Node", "Заголовок Marzban Node", "🅼", "5368712770722221269"),
    EmojiSlot("pasarguard", "Node", "Заголовок PasarGuard", "🅿️", "6019252539126455216"),

    # ══════════════════════════════════════════════════════════
    # Panel — управление панелью
    # ══════════════════════════════════════════════════════════
    EmojiSlot("threexui", "Panel", "Заголовок панели 3X-UI", "3️⃣", "5841233794044010002"),

    # ══════════════════════════════════════════════════════════
    # Cloud VPS — провайдеры (заголовки дашбордов и мастеров)
    # ══════════════════════════════════════════════════════════
    EmojiSlot("upcloud", "Cloud VPS", "UpCloud — дашборд аккаунта", "☁️", "6233173572966159962"),
    EmojiSlot("azure", "Cloud VPS", "Azure — дашборд, мастер подключения и создания VM", "🔷", "6235420094265037090"),
    EmojiSlot("hetzner", "Cloud VPS", "Hetzner — дашборд и мастер создания сервера", "🟥", "6233041343808017275"),
    EmojiSlot("exoscale", "Cloud VPS", "Exoscale — дашборд и мастер создания сервера", "🟧", ""),

    # ══════════════════════════════════════════════════════════
    # Общие статусные значки (используются во всех разделах)
    # ══════════════════════════════════════════════════════════
    EmojiSlot("success", "Общие", "Успех — любое сообщение об успешном завершении", "✅", "5841497371891997804"),
    EmojiSlot("error", "Общие", "Ошибка — любое сообщение об ошибке", "❌", "5837218716881788980"),
    EmojiSlot("warning", "Общие", "Предупреждение — подтверждения удаления и предупреждения", "⚠️", "5839104731510741826"),
)

_BY_KEY: dict[str, EmojiSlot] = {slot.key: slot for slot in SLOTS}

# Kept for any external/legacy reference to the flat key->id mapping.
IDS: dict[str, str] = {slot.key: slot.default_id for slot in SLOTS}


def slot(key: str) -> EmojiSlot | None:
    return _BY_KEY.get(key)


def sections() -> list[str]:
    seen: list[str] = []
    for s in SLOTS:
        if s.section not in seen:
            seen.append(s.section)
    return seen


def slots_in_section(section: str) -> list[EmojiSlot]:
    return [s for s in SLOTS if s.section == section]


def current_id(key: str) -> str:
    """The id actually in effect for this slot right now: an admin
    override if one was ever set through the bot, else the factory
    default_id above."""
    return emoji_overrides.get(key) or _BY_KEY.get(key, EmojiSlot(key, "", "", "")).default_id


def e(key: str, fallback: str) -> str:
    """Возвращает премиум-эмодзи (если для ключа есть ID) либо fallback."""
    custom_id = current_id(key)
    if custom_id:
        return f'<tg-emoji emoji-id="{custom_id}">{fallback}</tg-emoji>'
    return fallback


def button_icon(key: str) -> str | None:
    """ID для icon_custom_emoji_id у InlineKeyboardButton/KeyboardButton
    (Bot API 9.4+) -- None, если для этого ключа ID нет, тогда кнопка
    просто остаётся без иконки. Показ такой иконки на кнопке сам Telegram
    разрешает только если у аккаунта, на который зарегистрирован бот
    (BotFather), есть активная Premium-подписка, либо у бота куплен
    username на Fragment."""
    return current_id(key) or None
