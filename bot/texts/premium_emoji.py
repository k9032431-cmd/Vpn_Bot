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
    EmojiSlot("aws", "Cloud VPS", "AWS — в списке провайдеров (скоро)", "🟧", ""),
    EmojiSlot("azure", "Cloud VPS", "Azure — дашборд, мастер подключения и создания VM", "🔷", "6235420094265037090"),
    EmojiSlot("hetzner", "Cloud VPS", "Hetzner — дашборд и мастер создания сервера", "🟥", "6233041343808017275"),
    EmojiSlot("exoscale", "Cloud VPS", "Exoscale — дашборд и мастер создания сервера", "🟧", ""),
    EmojiSlot("linode", "Cloud VPS", "Linode — в списке провайдеров (скоро)", "🟩", ""),
    EmojiSlot("kamatera", "Cloud VPS", "Kamatera — в списке провайдеров (скоро)", "🟪", ""),
    EmojiSlot("digitalocean", "Cloud VPS", "DigitalOcean — дашборд и мастер создания сервера", "💧", ""),

    # ══════════════════════════════════════════════════════════
    # Общие статусные значки (используются во всех разделах)
    # ══════════════════════════════════════════════════════════
    EmojiSlot("success", "Общие", "Успех — любое сообщение об успешном завершении (и ✅ по всему тексту бота)", "✅", "5841497371891997804"),
    EmojiSlot("error", "Общие", "Ошибка — любое сообщение об ошибке", "❌", "5837218716881788980"),
    EmojiSlot("warning", "Общие", "Предупреждение — подтверждения удаления и ⚠️ по всему тексту бота", "⚠️", "5839104731510741826"),

    # ══════════════════════════════════════════════════════════
    # Значки в тексте сообщений — ниже идут все мелкие inline-значки,
    # которые раньше были просто вшиты в текст и никак не настраивались.
    # Группы условные (по смыслу), чтобы было проще искать.
    # ══════════════════════════════════════════════════════════

    EmojiSlot("globe_net", "Значки — сеть/сервер", "Сеть/IP (общий значок)", "🌐"),
    EmojiSlot("server", "Значки — сеть/сервер", "Сервер (имя/заголовок карточки)", "🖥"),
    EmojiSlot("port", "Значки — сеть/сервер", "Порт/подключение", "🔌"),
    EmojiSlot("globe_zone", "Значки — сеть/сервер", "Регион/зона (глобус)", "🌍"),
    EmojiSlot("antenna", "Значки — сеть/сервер", "Инбаунды/приём (раздел Panel)", "📡"),
    EmojiSlot("network_node", "Значки — сеть/сервер", "Нода — в тексте (не на кнопке)", "🖧"),
    EmojiSlot("signal", "Значки — сеть/сервер", "Статус сети/сигнал", "📶"),
    EmojiSlot("link", "Значки — сеть/сервер", "Ссылка", "🔗"),
    EmojiSlot("location", "Значки — сеть/сервер", "Локация/регион сервера", "📍"),
    EmojiSlot("ip_primary", "Значки — сеть/сервер", "Основной IP (Hetzner)", "🟩"),

    EmojiSlot("key_pw", "Значки — доступ/статус", "Пароль/ключ доступа", "🔑"),
    EmojiSlot("lock_auth", "Значки — доступ/статус", "Способ авторизации", "🔐"),
    EmojiSlot("lock", "Значки — доступ/статус", "Заблокировано/приватно", "🔒"),
    EmojiSlot("user", "Значки — доступ/статус", "Пользователь/логин", "👤"),
    EmojiSlot("users", "Значки — доступ/статус", "Пользователи (группой)", "👥"),
    EmojiSlot("crown", "Значки — доступ/статус", "Админ/главный пользователь", "👑"),
    EmojiSlot("shield", "Значки — доступ/статус", "Защита", "🛡"),
    EmojiSlot("status_green", "Значки — доступ/статус", "Статус: работает/активен", "🟢"),
    EmojiSlot("status_red", "Значки — доступ/статус", "Статус: остановлен/ошибка", "🔴"),
    EmojiSlot("status_pending", "Значки — доступ/статус", "Статус: в процессе (запуск/миграция и т.п.)", "🚧"),
    EmojiSlot("status_yellow", "Значки — доступ/статус", "Статус: подключается", "🟡"),
    EmojiSlot("status_gray", "Значки — доступ/статус", "Статус: неизвестно/отключено", "⚪"),
    EmojiSlot("status_hourglass", "Значки — доступ/статус", "Статус: истекает срок/лимит", "⏳"),
    EmojiSlot("status_paused", "Значки — доступ/статус", "Статус: на паузе", "⏸"),
    EmojiSlot("status_expired", "Значки — доступ/статус", "Статус: срок истёк", "⌛"),
    EmojiSlot("status_forbidden", "Значки — доступ/статус", "Статус: отключено/запрещено", "⛔"),

    EmojiSlot("gear", "Значки — панель и диски", "Настройки/конфигурация", "⚙"),
    EmojiSlot("edit", "Значки — панель и диски", "Редактирование/ввод", "✏"),
    EmojiSlot("package", "Значки — панель и диски", "Пакет/лимит данных", "📦"),
    EmojiSlot("tag", "Значки — панель и диски", "Тег/тип", "🏷"),
    EmojiSlot("disk_os", "Значки — панель и диски", "Диск/ОС сервера", "💿"),
    EmojiSlot("disk_header", "Значки — панель и диски", "Заголовок раздела дисков", "💾"),
    EmojiSlot("disk_item", "Значки — панель и диски", "Карточка одного диска", "💽"),
    EmojiSlot("numbers", "Значки — панель и диски", "Номер/количество", "🔢"),
    EmojiSlot("note", "Значки — панель и диски", "Заметка/описание", "📝"),
    EmojiSlot("dna", "Значки — панель и диски", "Конфигурация ядра панели", "🧬"),
    EmojiSlot("name_tag", "Значки — панель и диски", "Имя/домен", "📛"),
    EmojiSlot("traffic", "Значки — панель и диски", "Статус (светофор)", "🚦"),
    EmojiSlot("home", "Значки — панель и диски", "Хост", "🏠"),

    EmojiSlot("money", "Значки — действия/интерфейс", "Цена/стоимость", "💰"),
    EmojiSlot("forbidden", "Значки — действия/интерфейс", "Запрещено/отменено", "🚫"),
    EmojiSlot("clipboard", "Значки — действия/интерфейс", "Список/буфер", "📋"),
    EmojiSlot("sync", "Значки — действия/интерфейс", "Синхронизация/перезапуск", "🔄"),
    EmojiSlot("folder", "Значки — действия/интерфейс", "Папка/файлы", "📁"),
    EmojiSlot("ruler", "Значки — действия/интерфейс", "Размер", "📏"),
    EmojiSlot("tools", "Значки — действия/интерфейс", "Инструменты", "🛠"),
    EmojiSlot("mail_in", "Значки — действия/интерфейс", "Входящее уведомление", "📩"),
    EmojiSlot("page", "Значки — действия/интерфейс", "Страница/документ", "📄"),
    EmojiSlot("scroll", "Значки — действия/интерфейс", "Сертификат", "📜"),
    EmojiSlot("chat", "Значки — действия/интерфейс", "Сообщение/комментарий", "💬"),
    EmojiSlot("inbox", "Значки — действия/интерфейс", "Входящее", "📥"),
    EmojiSlot("outbox", "Значки — действия/интерфейс", "Исходящее", "📤"),
    EmojiSlot("thinking", "Значки — действия/интерфейс", "Некорректный ввод", "🤔"),
    EmojiSlot("launch2", "Значки — действия/интерфейс", "Запуск — в тексте (не на кнопке)", "🚀"),
    EmojiSlot("point_down", "Значки — действия/интерфейс", "Указатель вниз (подсказка)", "👇"),
    EmojiSlot("bell", "Значки — действия/интерфейс", "Уведомление админам", "🔔"),

    EmojiSlot("arrow_right", "Значки — разное", "Стрелка-результат", "→"),
    EmojiSlot("arrow_down", "Значки — разное", "Скачано (трафик)", "⬇"),
    EmojiSlot("arrow_up", "Значки — разное", "Загружено (трафик)", "⬆"),
    EmojiSlot("new_badge", "Значки — разное", "Пометка «новое»", "🆕"),
    EmojiSlot("id_badge", "Значки — разное", "ID", "🆔"),
    EmojiSlot("trash", "Значки — разное", "Удалено — в тексте (не на кнопке)", "🗑"),
    EmojiSlot("plus_icon", "Значки — разное", "Добавление — в тексте (не на кнопке)", "➕"),
    EmojiSlot("party", "Значки — разное", "Поздравление/готово", "🎉"),
    EmojiSlot("pin", "Значки — разное", "Важная пометка", "📌"),
    EmojiSlot("cleanup", "Значки — разное", "Раздел «остатки ресурсов» (Azure)", "🧹"),
    EmojiSlot("map_pin", "Значки — разное", "Зона доступности", "🗺"),
    EmojiSlot("cloud_small", "Значки — разное", "Облако — маленький значок в тексте", "☁"),

    EmojiSlot("chart", "Значки — статистика", "Статистика", "📊"),
    EmojiSlot("stat_trend", "Значки — статистика", "Рост/тренд в статистике", "📈"),

    EmojiSlot("whois_city", "Значки — WhoIs", "Город", "🏙"),
    EmojiSlot("whois_provider", "Значки — WhoIs", "Провайдер", "🏢"),
    EmojiSlot("whois_org", "Значки — WhoIs", "Организация", "🏬"),
    EmojiSlot("whois_timezone", "Значки — WhoIs", "Часовой пояс", "🕒"),
    EmojiSlot("whois_proxy", "Значки — WhoIs", "Прокси", "🎭"),
    EmojiSlot("whois_tor", "Значки — WhoIs", "Tor", "🕵"),
    EmojiSlot("whois_hosting", "Значки — WhoIs", "Хостинг", "🏭"),
    EmojiSlot("whois_registrar", "Значки — WhoIs", "Регистратор", "🏛"),
    EmojiSlot("whois_created", "Значки — WhoIs", "Дата регистрации", "📅"),
    EmojiSlot("whois_dns_mx", "Значки — WhoIs", "DNS MX", "📧"),
    EmojiSlot("whois_resources", "Значки — WhoIs", "Ресурсы сервера (CPU/RAM)", "🧠"),
)

# Character -> slot key, for the automatic pass over message body text (see
# apply_field_icons below) -- every inline icon that used to be a hardcoded
# unicode character and nothing else. Never applied to button labels:
# Telegram's button text is plain text only, it can't carry a <tg-emoji> tag
# at all, so those stay plain unicode forever regardless of this map.
_FIELD_ICON_MAP: dict[str, str] = {
    slot_.fallback: slot_.key for slot_ in SLOTS if slot_.section.startswith("Значки —")
}
# A few characters are intentionally reused from slots outside that section
# (same symbol, same meaning, already has its own slot) instead of a
# second, redundant one. (apply_field_icons handles the "with/without the
# U+FE0F variation selector" spelling of a character on its own -- only the
# bare codepoint needs to be listed here.)
_FIELD_ICON_MAP["✅"] = "success"
_FIELD_ICON_MAP["⚠"] = "warning"
_FIELD_ICON_MAP["👋"] = "welcome"

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


def section_index(section: str) -> int:
    """A stable, short ASCII stand-in for a section name in callback_data
    -- some section names (Cyrillic, "Значки — действия/интерфейс") are
    long enough in UTF-8 that embedding them directly would push
    callback_data past Telegram's 64-byte limit, silently breaking the
    whole keyboard. Position in sections() is stable within one running
    process; a restart with a changed SLOTS list only affects buttons
    already drawn before the restart, which is harmless since they're
    re-sent on every navigation anyway."""
    return sections().index(section)


def section_by_index(index: int) -> str | None:
    all_sections = sections()
    return all_sections[index] if 0 <= index < len(all_sections) else None


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


def apply_field_icons(text: str) -> str:
    """Replaces every hardcoded inline icon in a raw message-body template
    with its live premium-emoji render, before that template's own
    {placeholder}s are filled in (see translations.t) -- so this only ever
    touches characters that were literally written into the template
    itself, never a value some other {placeholder} supplies (an IP, a
    hostname, an already-resolved <tg-emoji> tag passed in as the
    {icon}-style kwarg every section already used before this existed).

    Deliberately never called for a button's own label text: Telegram
    button labels are plain text, they can't carry a <tg-emoji> tag at
    all, so this would just leave the raw tag visible as text."""
    for char, key in _FIELD_ICON_MAP.items():
        variant = char + "️"
        if variant in text:
            text = text.replace(variant, e(key, char))
        if char in text:
            text = text.replace(char, e(key, char))
    return text


def field_icon(char: str) -> str:
    """Для статусных словарей вида {"running": "🟢"}, которые используются
    и в подписи кнопки (должна остаться обычным текстом), и в тексте
    экрана (можно сделать премиум-эмодзи). apply_field_icons() этого не
    видит -- она трогает только буквальные символы самого шаблона
    перевода, а не значения, подставляемые через {kwargs} (как тут). Зови
    это явно в тех местах, где символ идёт в текст экрана, а не в
    подпись кнопки."""
    key = _FIELD_ICON_MAP.get(char)
    return e(key, char) if key else char


def button_icon(key: str) -> str | None:
    """ID для icon_custom_emoji_id у InlineKeyboardButton/KeyboardButton
    (Bot API 9.4+) -- None, если для этого ключа ID нет, тогда кнопка
    просто остаётся без иконки. Показ такой иконки на кнопке сам Telegram
    разрешает только если у аккаунта, на который зарегистрирован бот
    (BotFather), есть активная Premium-подписка, либо у бота куплен
    username на Fragment."""
    return current_id(key) or None
