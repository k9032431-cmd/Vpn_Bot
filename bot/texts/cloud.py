from __future__ import annotations

import html

from .premium_emoji import e
from .translations import t

PROVIDERS = ("upcloud", "aws", "azure", "linode", "kamatera")
ACTIVE_PROVIDERS = ("upcloud",)

_STATE_EMOJI = {
    "started": "🟢",
    "stopped": "🔴",
    "maintenance": "🚧",
    "error": "⚠️",
}

_CLOUD_ERR_KEYS = {
    "wrong_credentials": "cloud_err_wrong_credentials",
    "connect_failed": "cloud_err_connect_failed",
    "bad_response": "cloud_err_bad_response",
}


_PROVIDER_TITLES = {"upcloud": "UpCloud", "aws": "AWS", "azure": "Azure", "linode": "Linode", "kamatera": "Kamatera"}


def provider_title(provider: str) -> str:
    return _PROVIDER_TITLES.get(provider, provider.capitalize())


def provider_list_text(lang: str) -> str:
    return t(lang, "cloud_provider_list", icon=e("cloud_vps", "☁️"))


def provider_soon_text(lang: str) -> str:
    return t(lang, "cloud_provider_soon", icon=e("warning", "⚠️"))


def account_list_text(lang: str, provider: str, accounts: list[dict]) -> str:
    body_key = "cloud_account_list_hint" if accounts else "cloud_account_list_empty"
    body = t(lang, body_key)
    return t(
        lang,
        "cloud_account_list_header",
        icon=e("cloud_vps", "☁️"),
        provider=provider_title(provider),
        body=body,
    )


def account_list_label(account: dict) -> str:
    return f"☁️ {account['username']}"


def step_username_text(lang: str, provider: str) -> str:
    return t(lang, f"cloud_step_username_{provider}")


def step_password_text(lang: str) -> str:
    return t(lang, "cloud_step_password")


def empty_password_text(lang: str) -> str:
    return t(lang, "cloud_empty_password")


def connecting_text(lang: str) -> str:
    return t(lang, "cloud_connecting")


def _error_reason(lang: str, reason: str) -> str:
    if reason.startswith("detail:"):
        return html.escape(reason.split(":", 1)[1])
    key = _CLOUD_ERR_KEYS.get(reason, "cloud_err_bad_response")
    return t(lang, key)


def login_error_text(lang: str, reason: str) -> str:
    return t(lang, "cloud_login_error", icon=e("error", "❌"), reason=_error_reason(lang, reason))


def action_error_text(lang: str, reason: str) -> str:
    return t(lang, "cloud_action_error", icon=e("error", "❌"), reason=_error_reason(lang, reason))


def connected_text(lang: str, provider: str) -> str:
    return t(lang, "cloud_connected", icon=e("success", "✅"), provider=provider_title(provider))


def account_dashboard_text(lang: str, account: dict, credits: float) -> str:
    return t(
        lang,
        "cloud_account_dashboard",
        provider=provider_title(account["provider"]),
        username=html.escape(account["username"]),
        credits=f"{credits:.2f}",
        currency="EUR",
    )


def account_remove_confirm_text(lang: str, account: dict) -> str:
    return t(
        lang,
        "cloud_account_remove_confirm",
        icon=e("warning", "⚠️"),
        username=html.escape(account["username"]),
    )


def account_removed_text(lang: str) -> str:
    return t(lang, "cloud_account_removed", icon=e("success", "✅"))


def servers_header_text(lang: str, account: dict, has_servers: bool) -> str:
    body_key = "cloud_servers_hint" if has_servers else "cloud_servers_empty"
    return t(lang, "cloud_servers_header", username=html.escape(account["username"]), body=t(lang, body_key))


def server_list_label(server) -> str:
    icon = _STATE_EMOJI.get(server.state, "⚪️")
    return f"{icon} {server.title or server.hostname}"


def _ip_list(server) -> str:
    public = [ip.address for ip in server.ip_addresses if ip.access == "public"]
    return ", ".join(public) if public else t("ru", "cloud_server_no_ip")


def server_detail_text(lang: str, server) -> str:
    return t(
        lang,
        "cloud_server_detail",
        title=html.escape(server.title or server.hostname),
        hostname=html.escape(server.hostname),
        state=f"{_STATE_EMOJI.get(server.state, '⚪️')} {server.state}",
        zone=server.zone,
        plan=server.plan,
        cores=server.core_number,
        memory=server.memory_amount,
        ips=_ip_list(server) if server.ip_addresses else t(lang, "cloud_server_no_ip"),
    )


def server_action_ok_text(lang: str) -> str:
    return t(lang, "cloud_server_action_ok", icon=e("success", "✅"))


def server_delete_confirm_text(lang: str, server) -> str:
    return t(
        lang,
        "cloud_server_delete_confirm",
        icon=e("warning", "⚠️"),
        title=html.escape(server.title or server.hostname),
    )


def server_deleted_text(lang: str) -> str:
    return t(lang, "cloud_server_deleted", icon=e("success", "✅"))


def create_choose_zone_text(lang: str) -> str:
    return t(lang, "cloud_create_choose_zone")


def create_choose_plan_text(lang: str) -> str:
    return t(lang, "cloud_create_choose_plan")


def create_choose_template_text(lang: str) -> str:
    return t(lang, "cloud_create_choose_template")


def create_waiting_hostname_text(lang: str) -> str:
    return t(lang, "cloud_create_waiting_hostname")


def create_invalid_hostname_text(lang: str) -> str:
    return t(lang, "cloud_create_invalid_hostname")


def create_confirm_text(lang: str, hostname: str, zone: str, plan: str, template: str) -> str:
    return t(
        lang,
        "cloud_create_confirm",
        hostname=html.escape(hostname),
        zone=zone,
        plan=plan,
        template=html.escape(template),
    )


def creating_text(lang: str) -> str:
    return t(lang, "cloud_creating")


def create_success_text(lang: str, server) -> str:
    password_line = ""
    if server.password:
        password_line = t(lang, "cloud_create_password_line", password=server.password)
    return t(
        lang,
        "cloud_create_success",
        icon=e("success", "✅"),
        title=html.escape(server.title or server.hostname),
        ips=_ip_list(server) if server.ip_addresses else t(lang, "cloud_server_no_ip"),
        password_line=password_line,
    )


# --- Plan change ---


def plan_must_stop_text(lang: str) -> str:
    return t(lang, "cloud_plan_must_stop", icon=e("warning", "⚠️"))


def plan_choose_text(lang: str, current_plan: str) -> str:
    return t(lang, "cloud_plan_choose", current=current_plan)


def plan_confirm_text(lang: str, current_plan: str, new_plan: str) -> str:
    return t(lang, "cloud_plan_confirm", current=current_plan, new=new_plan)


def plan_changed_text(lang: str) -> str:
    return t(lang, "cloud_plan_changed", icon=e("success", "✅"))


# --- Storage / disks ---


def storage_header_text(lang: str, server, has_storages: bool) -> str:
    body_key = "cloud_storage_hint" if has_storages else "cloud_storage_empty"
    return t(
        lang,
        "cloud_storage_header",
        title=html.escape(server.title or server.hostname),
        body=t(lang, body_key),
    )


def storage_list_label(storage) -> str:
    return f"💽 {storage.title} — {storage.size} GB"


def storage_detail_text(lang: str, storage) -> str:
    return t(
        lang,
        "cloud_storage_detail",
        title=html.escape(storage.title),
        size=storage.size,
        type=storage.type,
        tier=storage.tier,
    )


def storage_detach_confirm_text(lang: str, storage) -> str:
    return t(lang, "cloud_storage_detach_confirm", icon=e("warning", "⚠️"), title=html.escape(storage.title))


def storage_delete_confirm_text(lang: str, storage) -> str:
    return t(lang, "cloud_storage_delete_confirm", icon=e("warning", "⚠️"), title=html.escape(storage.title))


def storage_detached_text(lang: str) -> str:
    return t(lang, "cloud_storage_detached", icon=e("success", "✅"))


def storage_deleted_text(lang: str) -> str:
    return t(lang, "cloud_storage_deleted", icon=e("success", "✅"))


def storage_waiting_size_text(lang: str) -> str:
    return t(lang, "cloud_storage_waiting_size")


def storage_invalid_size_text(lang: str) -> str:
    return t(lang, "cloud_storage_invalid_size")


def storage_confirm_attach_text(lang: str, size: int) -> str:
    return t(lang, "cloud_storage_confirm_attach", size=size)


def storage_attached_text(lang: str) -> str:
    return t(lang, "cloud_storage_attached", icon=e("success", "✅"))


def storage_waiting_resize_text(lang: str, current_size: int) -> str:
    return t(lang, "cloud_storage_waiting_resize", current=current_size)


def storage_confirm_resize_text(lang: str, title: str, old_size: int, new_size: int) -> str:
    return t(lang, "cloud_storage_confirm_resize", title=html.escape(title), old=old_size, new=new_size)


def storage_resized_text(lang: str) -> str:
    return t(lang, "cloud_storage_resized", icon=e("success", "✅"))


# --- Backups ---


def backups_header_text(lang: str, storage, has_backups: bool) -> str:
    body_key = "cloud_backups_hint" if has_backups else "cloud_backups_empty"
    return t(lang, "cloud_backups_header", title=html.escape(storage.title), body=t(lang, body_key))


def backup_list_label(backup) -> str:
    return f"🗄 {backup.title}"


def backup_detail_text(lang: str, backup) -> str:
    return f"🗄 <b>{html.escape(backup.title)}</b>\n\n📏 {backup.size} GB"


def backup_create_confirm_text(lang: str, storage) -> str:
    return t(lang, "cloud_backup_create_confirm", title=html.escape(storage.title))


def backup_created_text(lang: str) -> str:
    return t(lang, "cloud_backup_created", icon=e("success", "✅"))


def backup_restore_confirm_text(lang: str, backup) -> str:
    return t(lang, "cloud_backup_restore_confirm", icon=e("warning", "⚠️"), title=html.escape(backup.title))


def backup_restored_text(lang: str) -> str:
    return t(lang, "cloud_backup_restored", icon=e("success", "✅"))


def backup_delete_confirm_text(lang: str, backup) -> str:
    return t(lang, "cloud_backup_delete_confirm", icon=e("warning", "⚠️"), title=html.escape(backup.title))


def backup_deleted_text(lang: str) -> str:
    return t(lang, "cloud_backup_deleted", icon=e("success", "✅"))


# --- IP addresses ---


def ips_header_text(lang: str, server, has_ips: bool) -> str:
    body_key = "cloud_ips_hint" if has_ips else "cloud_ips_empty"
    return t(
        lang,
        "cloud_ips_header",
        title=html.escape(server.title or server.hostname),
        body=t(lang, body_key),
    )


def ip_list_label(ip) -> str:
    return f"🌐 {ip.address}"


def ip_add_confirm_text(lang: str, server) -> str:
    return t(lang, "cloud_ip_add_confirm", title=html.escape(server.title or server.hostname))


def ip_added_text(lang: str, address: str) -> str:
    return t(lang, "cloud_ip_added", icon=e("success", "✅"), address=address)


def ip_remove_confirm_text(lang: str, server, address: str) -> str:
    return t(
        lang,
        "cloud_ip_remove_confirm",
        icon=e("warning", "⚠️"),
        address=address,
        title=html.escape(server.title or server.hostname),
    )


def ip_removed_text(lang: str) -> str:
    return t(lang, "cloud_ip_removed", icon=e("success", "✅"))
