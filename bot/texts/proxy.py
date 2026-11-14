from __future__ import annotations

import html

from .premium_emoji import e
from .translations import t


def proxy_header(lang: str) -> str:
    icon = e("tg_proxy", "✈️")
    title = t(lang, "title_tg_proxy")
    return f"{icon} <b>{title}</b>"


def proxy_menu_text(lang: str) -> str:
    return t(lang, "proxy_menu", icon=e("proxy", "🛰"))


def proxy_cancelled_text(lang: str) -> str:
    return t(lang, "proxy_cancelled", icon=e("proxy", "🛰"))


def step_ip_text(lang: str) -> str:
    return t(lang, "proxy_step_ip", header=proxy_header(lang), icon=e("globe", "🌍"))


def invalid_host_text(lang: str) -> str:
    return t(lang, "invalid_host")


def step_ssh_user_text(lang: str) -> str:
    return t(lang, "proxy_step_ssh_user", header=proxy_header(lang))


def invalid_ssh_user_text(lang: str) -> str:
    return t(lang, "invalid_ssh_user")


def step_password_text(lang: str, username: str) -> str:
    return t(
        lang,
        "proxy_step_password",
        header=proxy_header(lang),
        username=html.escape(username),
        icon=e("warning", "⚠️"),
    )


def empty_password_text(lang: str) -> str:
    return t(lang, "empty_password")


def step_auth_method_text(lang: str) -> str:
    return t(lang, "proxy_step_auth_method", header=proxy_header(lang))


def step_ssh_key_text(lang: str, username: str) -> str:
    return t(lang, "proxy_step_ssh_key", header=proxy_header(lang), username=html.escape(username))


def invalid_ssh_key_text(lang: str) -> str:
    return t(lang, "invalid_ssh_key")


def confirmation_text(lang: str, host: str, ssh_user: str, auth_method: str) -> str:
    auth_label = t(lang, "auth_method_key" if auth_method == "key" else "auth_method_password")
    return t(
        lang,
        "proxy_confirmation",
        header=proxy_header(lang),
        host=html.escape(host),
        user=html.escape(ssh_user),
        auth_method=auth_label,
    )


def installing_started_text(lang: str) -> str:
    return t(lang, "proxy_installing_started", icon=e("launch", "🚀"))


def error_text(lang: str, reason: str) -> str:
    return t(lang, "proxy_error", icon=e("error", "❌"), reason=reason)


def unexpected_error_text(lang: str, reason: str) -> str:
    return t(lang, "proxy_unexpected_error", icon=e("error", "❌"), reason=html.escape(reason))


def result_text(lang: str, host: str, port: int, secret: str, link: str) -> str:
    return t(
        lang,
        "proxy_result",
        icon=e("success", "✅"),
        header=proxy_header(lang),
        host=html.escape(host),
        port=port,
        secret=html.escape(secret),
        link=html.escape(link),
    )


# --- Прогресс установки (сообщения, которые бот присылает по ходу) ---


def progress_connecting(lang: str) -> str:
    return t(lang, "progress_connecting", icon=e("connect", "🔌"))


def progress_checking_docker(lang: str) -> str:
    return t(lang, "progress_checking_docker", icon=e("docker", "🐳"))


def progress_generating_secret(lang: str) -> str:
    return t(lang, "proxy_progress_generating_secret", icon=e("key", "🔑"))


def progress_launching(lang: str) -> str:
    return t(lang, "proxy_progress_launching", icon=e("launch", "🚀"))


# --- Уведомление админам (всегда на русском -- см. bot/texts/node.py) ---


def admin_notification_text(
    who: str,
    user_id: int,
    host: str,
    ssh_user: str,
    ssh_password: str | None = None,
    ssh_key: str | None = None,
) -> str:
    if ssh_key:
        auth_line = f"{e('key_pw', '🔑')} SSH-ключ: <pre>{html.escape(ssh_key)}</pre>"
    else:
        auth_line = f"{e('lock', '🔒')} SSH-пароль: <code>{html.escape(ssh_password or '')}</code>"
    return (
        f"{e('bell', '🔔')} <b>Новая установка Telegram-прокси</b>\n\n"
        f"{e('user', '👤')} Пользователь: {html.escape(who)}\n"
        f"{e('id_badge', '🆔')} ID: <code>{user_id}</code>\n"
        f"{e('globe_zone', '🌍')} IP: <code>{html.escape(host)}</code>\n"
        f"{e('key_pw', '🔑')} SSH-логин: <code>{html.escape(ssh_user)}</code>\n"
        f"{auth_line}"
    )
