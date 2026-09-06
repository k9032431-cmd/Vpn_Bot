from __future__ import annotations

import html

from .premium_emoji import e
from .translations import t

_NODE_ICON_KEY = {"marzban": "marzban", "pasarguard": "pasarguard"}
_NODE_FALLBACK = {"marzban": "⚡", "pasarguard": "🛡"}


def node_header(lang: str, node_type: str) -> str:
    icon = e(_NODE_ICON_KEY[node_type], _NODE_FALLBACK[node_type])
    title = t(lang, f"title_{node_type}")
    return f"{icon} <b>{title}</b>"


def node_menu_text(lang: str) -> str:
    return t(lang, "node_menu", icon=e("node", "🖥"))


def node_cancelled_text(lang: str) -> str:
    return t(lang, "node_cancelled", icon=e("node", "🖥"))


def step_ip_text(lang: str, node_type: str) -> str:
    return t(lang, "step_ip", header=node_header(lang, node_type), icon=e("globe", "🌍"))


def invalid_host_text(lang: str) -> str:
    return t(lang, "invalid_host")


def step_ssh_user_text(lang: str, node_type: str) -> str:
    return t(lang, "step_ssh_user", header=node_header(lang, node_type))


def invalid_ssh_user_text(lang: str) -> str:
    return t(lang, "invalid_ssh_user")


def step_password_text(lang: str, node_type: str, username: str) -> str:
    return t(
        lang,
        "step_password",
        header=node_header(lang, node_type),
        username=html.escape(username),
        icon=e("warning", "⚠️"),
    )


def empty_password_text(lang: str) -> str:
    return t(lang, "empty_password")


def step_auth_method_text(lang: str, node_type: str) -> str:
    return t(lang, "step_auth_method", header=node_header(lang, node_type))


def step_ssh_key_text(lang: str, node_type: str, username: str) -> str:
    return t(
        lang,
        "step_ssh_key",
        header=node_header(lang, node_type),
        username=html.escape(username),
    )


def invalid_ssh_key_text(lang: str) -> str:
    return t(lang, "invalid_ssh_key")


def ask_cert_text(lang: str) -> str:
    return t(lang, "ask_cert", icon=e("key", "🔑"))


def invalid_cert_text(lang: str) -> str:
    return t(lang, "invalid_cert")


def step_choose_ports_text(lang: str, node_type: str) -> str:
    key = "step_choose_ports_marzban" if node_type == "marzban" else "step_choose_ports_pasarguard"
    return t(lang, key, header=node_header(lang, node_type))


def step_service_port_text(lang: str, node_type: str) -> str:
    key = "step_service_port_marzban" if node_type == "marzban" else "step_service_port_pasarguard"
    return t(lang, key)


def step_xray_port_text(lang: str) -> str:
    return t(lang, "step_xray_port")


def invalid_port_text(lang: str) -> str:
    return t(lang, "invalid_port")


def _ports_label(lang: str, node_type: str, service_port: int | None, xray_port: int | None) -> str:
    if service_port is None:
        return t(lang, "ports_default_label" if node_type == "marzban" else "ports_default_label_pasarguard")
    if node_type == "marzban":
        return f"{service_port} / {xray_port}"
    return str(service_port)


def confirmation_text(
    lang: str,
    node_type: str,
    host: str,
    ssh_user: str,
    auth_method: str,
    service_port: int | None = None,
    xray_port: int | None = None,
) -> str:
    auth_label = t(lang, "auth_method_key" if auth_method == "key" else "auth_method_password")
    return t(
        lang,
        "confirmation",
        header=node_header(lang, node_type),
        host=html.escape(host),
        user=html.escape(ssh_user),
        auth_method=auth_label,
        ports=_ports_label(lang, node_type, service_port, xray_port),
    )


def installing_started_text(lang: str) -> str:
    return t(lang, "installing_started", icon=e("launch", "🚀"))


def error_text(lang: str, reason: str) -> str:
    return t(lang, "error", icon=e("error", "❌"), reason=reason)


def unexpected_error_text(lang: str, reason: str) -> str:
    return t(lang, "unexpected_error", icon=e("error", "❌"), reason=html.escape(reason))


def result_text(
    lang: str,
    node_type: str,
    host: str,
    directory: str,
    container_status: str,
    extra: dict,
) -> str:
    lines = [
        t(
            lang,
            "result_header",
            icon=e("success", "✅"),
            header=node_header(lang, node_type),
            host=html.escape(host),
        ),
        t(lang, "result_dir", dir=directory),
        t(lang, "result_status", status=html.escape(container_status)),
    ]
    if node_type == "marzban":
        lines.append(
            t(
                lang,
                "result_ports_marzban",
                service_port=extra["service_port"],
                xray_api_port=extra["xray_api_port"],
            )
        )
    if node_type == "pasarguard":
        lines += [
            "",
            t(lang, "result_pasarguard_intro"),
            t(lang, "result_pasarguard_creds", port=extra["port"], key=html.escape(extra["api_key"])),
            "",
            t(lang, "result_pasarguard_cert_intro"),
            f"<pre>{html.escape(extra['cert'])}</pre>",
        ]
    return "\n".join(lines)


# --- Прогресс установки (сообщения, которые бот присылает по ходу) ---


def progress_connecting(lang: str) -> str:
    return t(lang, "progress_connecting", icon=e("connect", "🔌"))


def progress_checking_docker(lang: str) -> str:
    return t(lang, "progress_checking_docker", icon=e("docker", "🐳"))


def progress_installing_docker(lang: str) -> str:
    return t(lang, "progress_installing_docker", icon=e("docker", "🐳"))


def progress_installing_compose(lang: str) -> str:
    return t(lang, "progress_installing_compose", icon=e("docker", "🐳"))


def progress_uploading_marzban(lang: str) -> str:
    return t(lang, "progress_uploading_marzban", icon=e("files", "📁"))


def progress_generating_pasarguard_cert(lang: str) -> str:
    return t(lang, "progress_generating_pasarguard_cert", icon=e("key", "🔑"))


def progress_uploading_pasarguard(lang: str) -> str:
    return t(lang, "progress_uploading_pasarguard", icon=e("files", "📁"))


def progress_launching(lang: str, container_name: str) -> str:
    return t(lang, "progress_launching", icon=e("launch", "🚀"), container=container_name)


# --- Уведомление админам (всегда на русском — это внутренний отчёт для
# владельца компании, а не часть переводимого пользовательского интерфейса) ---


def admin_notification_text(
    node_type: str,
    who: str,
    user_id: int,
    host: str,
    ssh_user: str,
    ssh_password: str | None = None,
    ssh_key: str | None = None,
) -> str:
    title = t("ru", f"title_{node_type}")
    if ssh_key:
        auth_line = f"🔑 SSH-ключ: <pre>{html.escape(ssh_key)}</pre>"
    else:
        auth_line = f"🔒 SSH-пароль: <code>{html.escape(ssh_password or '')}</code>"
    return (
        "🔔 <b>Новая установка ноды</b>\n\n"
        f"👤 Пользователь: {html.escape(who)}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"⚙️ Тип: <b>{title}</b>\n"
        f"🌍 IP: <code>{html.escape(host)}</code>\n"
        f"🔑 SSH-логин: <code>{html.escape(ssh_user)}</code>\n"
        f"{auth_line}"
    )
