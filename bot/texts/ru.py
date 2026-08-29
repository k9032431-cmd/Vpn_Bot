from .premium_emoji import e

WELCOME_TEXT = (
    f"{e('welcome', '👋')} <b>ArsiCloudBot</b>\n"
    "<i>Ваш помощник по VPN — всегда под рукой</i>\n\n"
    "Выберите раздел 👇"
)

SECTION_TEXTS = {
    "cloud_vpn": (
        f"{e('cloud_vpn', '☁️')} <b>Cloud VPN</b>\n"
        "<i>Скоро здесь можно будет управлять облачными VPN-подключениями.</i>"
    ),
    "cloud_account": (
        f"{e('cloud_account', '👤')} <b>Cloud Account</b>\n"
        "<i>Управление аккаунтом появится совсем скоро.</i>"
    ),
    "crypt": (
        f"{e('crypt', '🔐')} <b>Crypt / Decrypt</b>\n"
        "<i>Шифрование и дешифрование данных — уже в работе.</i>"
    ),
    "language": (
        f"{e('language', '🌐')} <b>Language</b>\n"
        "<i>Выбор языка интерфейса добавим совсем скоро.</i>"
    ),
    "info": (
        f"{e('info', 'ℹ️')} <b>ArsiCloudBot</b>\n"
        "<i>Помощник по управлению VPN</i>\n\n"
        "Версия <code>0.1.0</code>"
    ),
    "sos": (
        f"{e('sos', '🆘')} <b>SOS</b>\n"
        "<i>Что-то пошло не так? Мы рядом.</i>\n\n"
        "Опишите проблему в поддержку — разберёмся вместе."
    ),
}
