from __future__ import annotations

import html
import re

from .premium_emoji import e
from .translations import t

PROVIDERS = ("upcloud", "aws", "azure", "linode", "kamatera")
ACTIVE_PROVIDERS = ("upcloud", "azure")

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
    "timeout": "cloud_err_timeout",
    "not_found": "cloud_err_not_found",
}


_PROVIDER_TITLES = {"upcloud": "UpCloud", "aws": "AWS", "azure": "Azure", "linode": "Linode", "kamatera": "Kamatera"}

# UpCloud zone ids follow "<country>-<city><n>" (e.g. "us-nyc1") — the city
# names for the zones UpCloud actually operates are listed here for a nice
# display; unlisted zones (new ones UpCloud adds later, or test fixtures)
# just fall back to the raw zone id, so this never breaks anything.
_ZONE_CITY_NAMES = {
    "fi-hel1": "Helsinki",
    "fi-hel2": "Helsinki",
    "de-fra1": "Frankfurt",
    "uk-lon1": "London",
    "nl-ams1": "Amsterdam",
    "es-mad1": "Madrid",
    "pl-waw1": "Warsaw",
    "se-sto1": "Stockholm",
    "us-chi1": "Chicago",
    "us-nyc1": "New York",
    "us-sjo1": "San Jose",
    "sg-sin1": "Singapore",
    "au-syd1": "Sydney",
}


def provider_title(provider: str) -> str:
    return _PROVIDER_TITLES.get(provider, provider.capitalize())


def _flag_emoji(country_code: str) -> str:
    # A flag emoji is just two Unicode "regional indicator" letters — this
    # works for any real ISO country code without a lookup table.
    code = country_code.upper()
    if len(code) != 2 or not code.isalpha():
        return "🌍"
    return "".join(chr(0x1F1E6 + ord(ch) - ord("A")) for ch in code)


def zone_display(zone_id: str) -> str:
    country_code = zone_id.split("-", 1)[0] if "-" in zone_id else ""
    flag = _flag_emoji(country_code)
    city = _ZONE_CITY_NAMES.get(zone_id, zone_id)
    return f"{flag} {city}"


def _format_memory(memory_mb: int) -> str:
    if memory_mb and memory_mb % 1024 == 0:
        return f"{memory_mb // 1024} GB"
    return f"{memory_mb} MB"


def _public_ip(server, family: str) -> str | None:
    for ip in server.ip_addresses:
        if ip.access == "public" and ip.family == family:
            return ip.address
    return None


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


def account_display_name(account: dict) -> str:
    """UpCloud accounts are identified by username; Azure accounts have no
    single "login" — the subscription id is the closest equivalent."""
    if account["provider"] == "azure":
        return account.get("subscription_id", "")
    return account.get("username", "")


def account_list_label(account: dict) -> str:
    return f"☁️ {account_display_name(account)}"


def step_username_text(lang: str, provider: str) -> str:
    return t(lang, f"cloud_step_username_{provider}")


def step_password_text(lang: str) -> str:
    return t(lang, "cloud_step_password")


def empty_password_text(lang: str) -> str:
    return t(lang, "cloud_empty_password")


def connecting_text(lang: str) -> str:
    return t(lang, "cloud_connecting")


_SERVER_STATE_ERROR_RE = re.compile(r"is in state '(\w+)'")


def _error_reason(lang: str, reason: str) -> str:
    if reason.startswith("detail:"):
        msg = reason.split(":", 1)[1]
        # UpCloud blocks several operations while the server is in a given
        # state (e.g. "not allowed while the server ... is in state
        # 'started'/'maintenance'") — translate that into guidance instead
        # of showing the raw UUID-laden message.
        state_match = _SERVER_STATE_ERROR_RE.search(msg)
        if state_match:
            state = state_match.group(1)
            if state == "started":
                return t(lang, "cloud_err_state_started")
            if state == "maintenance":
                return t(lang, "cloud_err_state_maintenance")
            return t(lang, "cloud_err_state_other", state=state)
        return html.escape(msg)
    key = _CLOUD_ERR_KEYS.get(reason, "cloud_err_bad_response")
    return t(lang, key)


def login_error_text(lang: str, reason: str, provider: str | None = None) -> str:
    error_text = _error_reason(lang, reason)
    if reason == "wrong_credentials" and provider == "upcloud":
        error_text += t(lang, "cloud_err_wrong_credentials_hint_upcloud")
    return t(lang, "cloud_login_error", icon=e("error", "❌"), reason=error_text)


def action_error_text(lang: str, reason: str) -> str:
    return t(lang, "cloud_action_error", icon=e("error", "❌"), reason=_error_reason(lang, reason))


def connected_text(lang: str, provider: str) -> str:
    return t(lang, "cloud_connected", icon=e("success", "✅"), provider=provider_title(provider))


def account_dashboard_text(lang: str, account: dict, credits: float) -> str:
    return t(
        lang,
        "cloud_account_dashboard",
        provider=provider_title(account["provider"]),
        username=html.escape(account_display_name(account)),
        credits=f"{credits:.2f}",
        currency="EUR",
    )


def account_remove_confirm_text(lang: str, account: dict) -> str:
    return t(
        lang,
        "cloud_account_remove_confirm",
        icon=e("warning", "⚠️"),
        username=html.escape(account_display_name(account)),
    )


def account_removed_text(lang: str) -> str:
    return t(lang, "cloud_account_removed", icon=e("success", "✅"))


def servers_header_text(lang: str, account: dict, has_servers: bool) -> str:
    body_key = "cloud_servers_hint" if has_servers else "cloud_servers_empty"
    return t(
        lang, "cloud_servers_header", username=html.escape(account_display_name(account)), body=t(lang, body_key)
    )


def server_list_label(server) -> str:
    icon = _STATE_EMOJI.get(server.state, "⚪️")
    return f"{icon} {server.title or server.hostname}"


def server_detail_text(lang: str, server) -> str:
    no_ip = t(lang, "cloud_server_no_ip")
    return t(
        lang,
        "cloud_server_detail",
        title=html.escape(server.title or server.hostname),
        state=f"{_STATE_EMOJI.get(server.state, '⚪️')} {server.state}",
        location=zone_display(server.zone),
        plan=server.plan,
        cores=server.core_number,
        memory=_format_memory(server.memory_amount),
        hostname=html.escape(server.hostname),
        ipv4=_public_ip(server, "IPv4") or no_ip,
        ipv6=_public_ip(server, "IPv6") or no_ip,
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


def _page_suffix(lang: str, page: int, total_pages: int) -> str:
    if total_pages <= 1:
        return ""
    return t(lang, "cloud_page_indicator", page=page + 1, total=total_pages)


def create_choose_zone_text(lang: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "cloud_create_choose_zone") + _page_suffix(lang, page, total_pages)


def create_choose_plan_text(lang: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "cloud_create_choose_plan") + _page_suffix(lang, page, total_pages)


def create_choose_template_text(lang: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "cloud_create_choose_template") + _page_suffix(lang, page, total_pages)


def create_waiting_hostname_text(lang: str) -> str:
    return t(lang, "cloud_create_waiting_hostname")


def create_invalid_hostname_text(lang: str) -> str:
    return t(lang, "cloud_create_invalid_hostname")


def create_choose_auth_method_text(lang: str) -> str:
    return t(lang, "cloud_create_choose_auth_method")


def create_waiting_ssh_key_text(lang: str) -> str:
    return t(lang, "cloud_create_waiting_ssh_key")


def create_invalid_ssh_key_text(lang: str) -> str:
    return t(lang, "cloud_create_invalid_ssh_key")


def create_confirm_text(lang: str, hostname: str, zone: str, plan: str, template: str, auth_method: str) -> str:
    auth_label = t(lang, "cloud_auth_method_key" if auth_method == "key" else "cloud_auth_method_password")
    return t(
        lang,
        "cloud_create_confirm",
        hostname=html.escape(hostname),
        zone=zone,
        plan=plan,
        template=html.escape(template),
        auth_method=auth_label,
    )


def creating_text(lang: str) -> str:
    return t(lang, "cloud_creating")


def create_success_text(lang: str, server, ssh_key_used: bool = False) -> str:
    no_ip = t(lang, "cloud_server_no_ip")
    password_line = ""
    if ssh_key_used:
        password_line = t(lang, "cloud_create_ssh_key_line")
    elif server.password:
        password_line = t(lang, "cloud_create_password_line", password=html.escape(server.password))
    return t(
        lang,
        "cloud_create_success",
        icon=e("success", "✅"),
        title=html.escape(server.title or server.hostname),
        location=zone_display(server.zone),
        ipv4=_public_ip(server, "IPv4") or no_ip,
        ipv6=_public_ip(server, "IPv6") or no_ip,
        password_line=password_line,
    )


# --- Plan change ---


def plan_must_stop_text(lang: str) -> str:
    return t(lang, "cloud_plan_must_stop", icon=e("warning", "⚠️"))


def delete_must_stop_text(lang: str) -> str:
    return t(lang, "cloud_delete_must_stop", icon=e("warning", "⚠️"))


def restore_must_stop_text(lang: str) -> str:
    return t(lang, "cloud_restore_must_stop", icon=e("warning", "⚠️"))


def server_in_maintenance_text(lang: str) -> str:
    return t(lang, "cloud_server_in_maintenance", icon=e("warning", "⚠️"))


def plan_choose_text(lang: str, current_plan: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "cloud_plan_choose", current=current_plan) + _page_suffix(lang, page, total_pages)


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


# --- Azure ---


_AZURE_POWER_EMOJI = {
    "running": "🟢",
    "deallocated": "🔴",
    "stopped": "🔴",
    "starting": "🚧",
    "stopping": "🚧",
}


def azure_step_tenant_text(lang: str) -> str:
    return t(lang, "azure_step_tenant")


def azure_step_client_id_text(lang: str) -> str:
    return t(lang, "azure_step_client_id")


def azure_step_client_secret_text(lang: str) -> str:
    return t(lang, "azure_step_client_secret")


def azure_step_subscription_text(lang: str) -> str:
    return t(lang, "azure_step_subscription")


def azure_empty_field_text(lang: str) -> str:
    return t(lang, "azure_empty_field")


def azure_account_dashboard_text(lang: str, account: dict, info) -> str:
    return t(
        lang,
        "azure_account_dashboard",
        subscription_id=html.escape(account.get("subscription_id", "")),
        display_name=html.escape(info.display_name) or "—",
        state=html.escape(info.state),
    )


def azure_vms_header_text(lang: str, account: dict, has_vms: bool) -> str:
    body_key = "cloud_servers_hint" if has_vms else "cloud_servers_empty"
    return t(
        lang, "azure_vms_header", subscription_id=html.escape(account.get("subscription_id", "")), body=t(lang, body_key)
    )


def azure_vm_list_label(vm) -> str:
    icon = _AZURE_POWER_EMOJI.get(vm.power_state, "⚪️")
    return f"{icon} {vm.name}"


def azure_vm_detail_text(lang: str, vm) -> str:
    no_ip = t(lang, "cloud_server_no_ip")
    return t(
        lang,
        "azure_vm_detail",
        name=html.escape(vm.name),
        state=f"{_AZURE_POWER_EMOJI.get(vm.power_state, '⚪️')} {vm.power_state}",
        location=html.escape(vm.location),
        size=vm.vm_size,
        ip=vm.public_ip or no_ip,
        username=html.escape(vm.admin_username),
    )


def azure_vm_action_ok_text(lang: str) -> str:
    return t(lang, "cloud_server_action_ok", icon=e("success", "✅"))


def azure_vm_delete_confirm_text(lang: str, vm) -> str:
    return t(lang, "azure_vm_delete_confirm", icon=e("warning", "⚠️"), name=html.escape(vm.name))


def azure_vm_deleted_text(lang: str) -> str:
    return t(lang, "cloud_server_deleted", icon=e("success", "✅"))


def azure_create_choose_location_text(lang: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "azure_create_choose_location") + _page_suffix(lang, page, total_pages)


def azure_create_choose_size_text(lang: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "azure_create_choose_size") + _page_suffix(lang, page, total_pages)


def azure_create_choose_image_text(lang: str, page: int = 0, total_pages: int = 1) -> str:
    return t(lang, "azure_create_choose_image") + _page_suffix(lang, page, total_pages)


def azure_create_waiting_hostname_text(lang: str) -> str:
    return t(lang, "azure_create_waiting_hostname")


def azure_create_invalid_hostname_text(lang: str) -> str:
    return t(lang, "azure_create_invalid_hostname")


def azure_create_choose_auth_method_text(lang: str) -> str:
    return t(lang, "cloud_create_choose_auth_method")


def azure_create_waiting_ssh_key_text(lang: str) -> str:
    return t(lang, "cloud_create_waiting_ssh_key")


def azure_create_invalid_ssh_key_text(lang: str) -> str:
    return t(lang, "cloud_create_invalid_ssh_key")


def azure_create_confirm_text(
    lang: str, hostname: str, location: str, size: str, image_title: str, auth_method: str
) -> str:
    auth_label = t(lang, "cloud_auth_method_key" if auth_method == "key" else "cloud_auth_method_password")
    return t(
        lang,
        "azure_create_confirm",
        hostname=html.escape(hostname),
        location=location,
        size=size,
        image=html.escape(image_title),
        auth_method=auth_label,
    )


_AZURE_PROGRESS_KEYS = {
    "resource_group": "azure_progress_resource_group",
    "network": "azure_progress_network",
    "public_ip": "azure_progress_public_ip",
    "nsg": "azure_progress_nsg",
    "nic": "azure_progress_nic",
    "vm": "azure_progress_vm",
}


def azure_progress_text(lang: str, step: str) -> str:
    key = _AZURE_PROGRESS_KEYS.get(step, "azure_progress_vm")
    return t(lang, key)


def azure_create_success_text(lang: str, vm, ssh_key_used: bool = False) -> str:
    no_ip = t(lang, "cloud_server_no_ip")
    password_line = ""
    if ssh_key_used:
        password_line = t(lang, "cloud_create_ssh_key_line")
    elif vm.admin_password:
        password_line = t(lang, "cloud_create_password_line", password=html.escape(vm.admin_password))
    return t(
        lang,
        "azure_create_success",
        icon=e("success", "✅"),
        name=html.escape(vm.name),
        location=html.escape(vm.location),
        ip=vm.public_ip or no_ip,
        username=html.escape(vm.admin_username),
        password_line=password_line,
    )


def ip_removed_text(lang: str) -> str:
    return t(lang, "cloud_ip_removed", icon=e("success", "✅"))
