from __future__ import annotations

import datetime
import html
from urllib.parse import urlparse

from .premium_emoji import e
from .translations import t

_PANEL_ICON_KEY = {"marzban": "marzban", "pasarguard": "pasarguard", "3xui": "threexui"}
_PANEL_FALLBACK = {"marzban": "⚡", "pasarguard": "🛡", "3xui": "3️⃣"}

_STATUS_EMOJI = {
    "active": "🟢",
    "disabled": "🔴",
    "expired": "⌛",
    "limited": "🚧",
    "on_hold": "⏸",
}

_PANEL_ERR_KEYS = {
    "wrong_credentials": "panel_err_wrong_credentials",
    "connect_failed": "panel_err_connect_failed",
    "bad_response": "panel_err_bad_response",
}


def _host_label(url: str) -> str:
    return urlparse(url).netloc or url


def panel_list_label(lang: str, panel: dict) -> str:
    # Button captions can't use premium emoji (Telegram limitation), so
    # this always uses the plain unicode fallback.
    icon = _PANEL_FALLBACK[panel["type"]]
    title = t(lang, f"title_panel_{panel['type']}")
    return f"{icon} {title} — {_host_label(panel['url'])}"


def panel_header(lang: str, panel_type: str, url: str) -> str:
    # Includes the host so multiple panels of the same type (e.g. two
    # Marzban instances) are still distinguishable on screen.
    icon = e(_PANEL_ICON_KEY[panel_type], _PANEL_FALLBACK[panel_type])
    title = t(lang, f"title_panel_{panel_type}")
    return f"{icon} <b>{title}</b> — <code>{html.escape(_host_label(url))}</code>"


def panel_list_header_text(lang: str, has_panels: bool) -> str:
    key = "panel_list_header" if has_panels else "panel_list_empty"
    return t(lang, key, icon=e("panel", "⚙️"))


def panel_add_menu_text(lang: str) -> str:
    return t(lang, "panel_add_menu", icon=e("panel", "⚙️"))


def panel_cancelled_text(lang: str) -> str:
    return t(lang, "panel_cancelled", icon=e("panel", "⚙️"))


def step_url_text(lang: str, panel_type: str) -> str:
    icon = e(_PANEL_ICON_KEY[panel_type], _PANEL_FALLBACK[panel_type])
    title = t(lang, f"title_panel_{panel_type}")
    return t(lang, "step_panel_url", header=f"{icon} <b>{title}</b>")


def invalid_url_text(lang: str) -> str:
    return t(lang, "invalid_panel_url")


def step_username_text(lang: str, panel_type: str) -> str:
    icon = e(_PANEL_ICON_KEY[panel_type], _PANEL_FALLBACK[panel_type])
    title = t(lang, f"title_panel_{panel_type}")
    return t(lang, "step_panel_username", header=f"{icon} <b>{title}</b>")


def invalid_username_text(lang: str) -> str:
    return t(lang, "invalid_panel_username")


def step_password_text(lang: str, panel_type: str, username: str) -> str:
    icon = e(_PANEL_ICON_KEY[panel_type], _PANEL_FALLBACK[panel_type])
    title = t(lang, f"title_panel_{panel_type}")
    return t(
        lang,
        "step_panel_password",
        header=f"{icon} <b>{title}</b>",
        username=html.escape(username),
        icon=e("warning", "⚠️"),
    )


def empty_password_text(lang: str) -> str:
    return t(lang, "empty_panel_password")


def connecting_text(lang: str) -> str:
    return t(lang, "panel_connecting")


def _error_reason(lang: str, reason: str) -> str:
    if reason.startswith("detail:"):
        return html.escape(reason.split(":", 1)[1])
    if reason.startswith("http:"):
        status = reason.split(":", 1)[1]
        return t(lang, "panel_err_http", status=status)
    key = _PANEL_ERR_KEYS.get(reason, "panel_err_bad_response")
    return t(lang, key)


def login_error_text(lang: str, reason: str) -> str:
    return t(lang, "panel_login_error", icon=e("error", "❌"), reason=_error_reason(lang, reason))


def action_error_text(lang: str, reason: str) -> str:
    return t(lang, "panel_action_error", icon=e("error", "❌"), reason=_error_reason(lang, reason))


def connected_text(lang: str, panel_type: str, url: str) -> str:
    return t(
        lang,
        "panel_connected",
        icon=e("success", "✅"),
        header=panel_header(lang, panel_type, url),
    )


def dashboard_text(lang: str, panel: dict) -> str:
    return t(lang, "panel_dashboard", header=panel_header(lang, panel["type"], panel["url"]))


def _humanize_bytes(n: int) -> str:
    value = float(n or 0)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def stats_text_marzban_family(lang: str, panel: dict, stats) -> str:
    return t(
        lang,
        "panel_stats_marzban",
        header=panel_header(lang, panel["type"], panel["url"]),
        version=html.escape(stats.version),
        total=stats.total_users,
        active=stats.active,
        disabled=stats.disabled,
        expired=stats.expired,
        limited=stats.limited,
        on_hold=stats.on_hold,
        online=stats.online_users,
        down=_humanize_bytes(stats.incoming_bandwidth),
        up=_humanize_bytes(stats.outgoing_bandwidth),
    )


def stats_text_3xui(lang: str, panel: dict, inbounds_count: int, clients_count: int) -> str:
    return t(
        lang,
        "panel_stats_3xui",
        header=panel_header(lang, panel["type"], panel["url"]),
        inbounds_count=inbounds_count,
        clients_count=clients_count,
    )


def _page_count(total: int, page_size: int) -> int:
    return max(1, -(-total // page_size))


def users_list_text_marzban_family(
    lang: str, panel: dict, users: list[dict], offset: int, total: int, page_size: int
) -> str:
    # Usernames are shown as tappable buttons (see panel_users_keyboard),
    # so this is just the screen's header/range line.
    header = panel_header(lang, panel["type"], panel["url"])
    if not total:
        return t(lang, "panel_users_list_empty", header=header)
    return t(
        lang,
        "panel_users_list_header",
        header=header,
        start=offset + 1,
        end=offset + len(users),
        total=total,
        page=offset // page_size + 1,
        pages=_page_count(total, page_size),
    )


def users_list_text_3xui(
    lang: str, panel: dict, page_labels: list[str], offset: int, total: int, page_size: int
) -> str:
    header = panel_header(lang, panel["type"], panel["url"])
    if not total:
        return t(lang, "panel_users_list_empty", header=header)
    lines = [
        t(
            lang,
            "panel_users_list_header",
            header=header,
            start=offset + 1,
            end=offset + len(page_labels),
            total=total,
            page=offset // page_size + 1,
            pages=_page_count(total, page_size),
        )
    ]
    lines.extend(f"👤 <code>{html.escape(label)}</code>" for label in page_labels)
    return "\n".join(lines)


def status_label(lang: str, status: str) -> str:
    return t(lang, f"status_{status}") if status in _STATUS_EMOJI else status


def format_limit(lang: str, data_limit: int | None) -> str:
    if not data_limit:
        return t(lang, "limit_unlimited")
    gb = data_limit / (1024**3)
    gb_text = f"{gb:.0f}" if gb == int(gb) else f"{gb:.1f}"
    return t(lang, "limit_gb", gb=gb_text)


def format_expire(lang: str, expire: int | None) -> str:
    if not expire:
        return t(lang, "expire_never")
    dt = datetime.datetime.fromtimestamp(expire, tz=datetime.timezone.utc)
    return dt.strftime("%Y-%m-%d")


def remove_confirm_text(lang: str, panel: dict) -> str:
    return t(lang, "panel_remove_confirm", header=panel_header(lang, panel["type"], panel["url"]))


def removed_text(lang: str) -> str:
    return t(lang, "panel_removed")


# --- Управление пользователями (Marzban/PasarGuard) ---


def create_user_step_username_text(lang: str, panel: dict) -> str:
    return t(lang, "panel_create_user_step_username", header=panel_header(lang, panel["type"], panel["url"]))


def invalid_new_username_text(lang: str) -> str:
    return t(lang, "panel_create_user_invalid_username")


def create_user_step_limits_text(lang: str, panel: dict, username: str) -> str:
    return t(
        lang,
        "panel_create_user_step_limits",
        header=panel_header(lang, panel["type"], panel["url"]),
        username=html.escape(username),
    )


def invalid_limits_text(lang: str) -> str:
    return t(lang, "panel_invalid_limits")


def create_user_confirm_text(
    lang: str, panel: dict, username: str, data_limit: int | None, expire: int | None
) -> str:
    return t(
        lang,
        "panel_create_user_confirm",
        header=panel_header(lang, panel["type"], panel["url"]),
        username=html.escape(username),
        limit=format_limit(lang, data_limit),
        expire=format_expire(lang, expire),
    )


def create_user_success_text(lang: str, username: str, sub_link: str) -> str:
    return t(
        lang,
        "panel_create_user_success",
        icon=e("success", "✅"),
        username=html.escape(username),
        sub_link=html.escape(sub_link),
    )


def edit_user_prompt_text(lang: str, panel: dict, username: str) -> str:
    return t(
        lang,
        "panel_edit_user_prompt",
        header=panel_header(lang, panel["type"], panel["url"]),
        username=html.escape(username),
    )


def edit_user_success_text(lang: str, username: str) -> str:
    return t(lang, "panel_edit_user_success", icon=e("success", "✅"), username=html.escape(username))


def user_detail_text(lang: str, panel: dict, user: dict) -> str:
    status = str(user.get("status", ""))
    username = str(user.get("username", "?"))
    return t(
        lang,
        "panel_user_detail",
        header=panel_header(lang, panel["type"], panel["url"]),
        username=html.escape(username),
        status_emoji=_STATUS_EMOJI.get(status, "•"),
        status_label=status_label(lang, status),
        used=_humanize_bytes(int(user.get("used_traffic", 0) or 0)),
        limit=format_limit(lang, user.get("data_limit")),
        expire=format_expire(lang, user.get("expire")),
        sub_link=html.escape(str(user.get("subscription_url") or "—")),
    )


def user_not_found_text(lang: str) -> str:
    return t(lang, "panel_user_not_found")


def delete_confirm_user_text(lang: str, panel: dict, username: str) -> str:
    return t(
        lang,
        "panel_delete_confirm_user",
        header=panel_header(lang, panel["type"], panel["url"]),
        username=html.escape(username),
    )


def delete_success_text(lang: str, username: str) -> str:
    return t(lang, "panel_delete_success", icon=e("success", "✅"), username=html.escape(username))


def toggle_success_text(lang: str, username: str, new_status: str) -> str:
    return t(
        lang,
        "panel_toggle_success",
        icon=e("success", "✅"),
        username=html.escape(username),
        status_label=status_label(lang, new_status),
    )


def reset_success_text(lang: str, username: str) -> str:
    return t(lang, "panel_reset_success", icon=e("success", "✅"), username=html.escape(username))


# --- Управление нодами (Marzban/PasarGuard) ---

_NODE_STATUS_EMOJI = {
    "connected": "🟢",
    "connecting": "🟡",
    "error": "🔴",
    "disabled": "⚪",
}


def node_status_label(lang: str, status: str) -> str:
    key = f"node_status_{status}"
    label = t(lang, key)
    return label if label != key else status


def nodes_list_text(lang: str, panel: dict, nodes: list) -> str:
    header = panel_header(lang, panel["type"], panel["url"])
    if not nodes:
        return t(lang, "panel_nodes_list_empty", header=header)
    return t(lang, "panel_nodes_list_header", header=header, count=len(nodes))


def node_list_label(node) -> str:
    emoji = _NODE_STATUS_EMOJI.get(node.status, "•")
    return f"{emoji} {node.name} — {node.address}"


def node_detail_text(lang: str, panel: dict, node) -> str:
    message = html.escape(node.message) if node.message else "—"
    return t(
        lang,
        "panel_node_detail",
        header=panel_header(lang, panel["type"], panel["url"]),
        name=html.escape(node.name),
        status_emoji=_NODE_STATUS_EMOJI.get(node.status, "•"),
        status_label=node_status_label(lang, node.status),
        address=html.escape(node.address),
        port=node.port,
        api_port=node.api_port,
        xray_version=html.escape(node.xray_version or "—"),
        message=message,
    )


def create_node_step_name_text(lang: str, panel: dict) -> str:
    return t(lang, "panel_create_node_step_name", header=panel_header(lang, panel["type"], panel["url"]))


def invalid_node_name_text(lang: str) -> str:
    return t(lang, "panel_create_node_invalid_name")


def create_node_step_address_text(lang: str, panel: dict, name: str) -> str:
    return t(
        lang,
        "panel_create_node_step_address",
        header=panel_header(lang, panel["type"], panel["url"]),
        name=html.escape(name),
    )


def invalid_node_address_text(lang: str) -> str:
    return t(lang, "panel_create_node_invalid_address")


def create_node_step_port_text(lang: str, panel: dict) -> str:
    return t(lang, "panel_create_node_step_port", header=panel_header(lang, panel["type"], panel["url"]))


def invalid_node_port_text(lang: str) -> str:
    return t(lang, "panel_create_node_invalid_port")


def create_node_confirm_text(lang: str, panel: dict, name: str, address: str, port: int, api_port: int) -> str:
    return t(
        lang,
        "panel_create_node_confirm",
        header=panel_header(lang, panel["type"], panel["url"]),
        name=html.escape(name),
        address=html.escape(address),
        port=port,
        api_port=api_port,
    )


def create_node_success_text(lang: str, name: str) -> str:
    return t(lang, "panel_create_node_success", icon=e("success", "✅"), name=html.escape(name))


def node_delete_confirm_text(lang: str, panel: dict, node) -> str:
    return t(
        lang,
        "panel_node_delete_confirm",
        header=panel_header(lang, panel["type"], panel["url"]),
        name=html.escape(node.name),
    )


def node_delete_success_text(lang: str, name: str) -> str:
    return t(lang, "panel_node_delete_success", icon=e("success", "✅"), name=html.escape(name))


def node_reconnect_success_text(lang: str, name: str) -> str:
    return t(lang, "panel_node_reconnect_success", icon=e("success", "✅"), name=html.escape(name))


# --- Уведомление админам (всегда на русском, как и для Node) ---


def admin_panel_notification_text(
    panel_type: str,
    who: str,
    user_id: int,
    url: str,
    username: str,
    password: str,
) -> str:
    title = t("ru", f"title_panel_{panel_type}")
    return (
        "🔔 <b>Подключена новая панель</b>\n\n"
        f"👤 Пользователь: {html.escape(who)}\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"⚙️ Панель: <b>{title}</b>\n"
        f"🌍 URL: <code>{html.escape(url)}</code>\n"
        f"🔑 Логин: <code>{html.escape(username)}</code>\n"
        f"🔒 Пароль: <code>{html.escape(password)}</code>"
    )
