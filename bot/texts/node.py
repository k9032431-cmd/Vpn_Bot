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


def ask_cert_text(lang: str) -> str:
    return t(lang, "ask_cert", icon=e("key", "🔑"))


def invalid_cert_text(lang: str) -> str:
    return t(lang, "invalid_cert")


def confirmation_text(lang: str, node_type: str, host: str, ssh_user: str) -> str:
    return t(
        lang,
        "confirmation",
        header=node_header(lang, node_type),
        host=html.escape(host),
        user=html.escape(ssh_user),
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
