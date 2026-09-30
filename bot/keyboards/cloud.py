from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.cloud import (
    ACTIVE_PROVIDERS,
    PROVIDERS,
    account_list_label,
    azure_port_rule_label,
    azure_vm_list_label,
    azure_zone_label,
    backup_list_label,
    hetzner_address_list_label,
    hetzner_ip_list_label,
    hetzner_server_list_label,
    ip_list_label,
    server_list_label,
    storage_list_label,
)
from bot.texts.premium_emoji import button_icon
from bot.texts.translations import t

PAGE_SIZE = 5


def provider_list_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for provider in PROVIDERS:
        builder.button(
            text=t(lang, f"btn_cloud_provider_{provider}"), callback_data=f"cprov:{provider}", style="primary",
            icon_custom_emoji_id=button_icon(provider),
        )
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back", style="danger")
    builder.adjust(*([1] * len(PROVIDERS)), 1)
    return builder.as_markup()


def provider_soon_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_provider_list"), callback_data="menu:cloud_vps", style="primary")
    builder.adjust(1)
    return builder.as_markup()


def account_list_keyboard(lang: str, provider: str, accounts: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for account in accounts:
        builder.button(text=account_list_label(account), callback_data=f"cview:{account['id']}", style="primary")
        rows.append(1)
    if provider in ACTIVE_PROVIDERS:
        builder.button(text=t(lang, "btn_cloud_account_add"), callback_data=f"cadd:{provider}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_provider_list"), callback_data="menu:cloud_vps", style="primary")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def cloud_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="csetup:cancel", style="danger")
    return builder.as_markup()


def cloud_error_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_provider_list"), callback_data="menu:cloud_vps", style="primary")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back", style="primary")
    builder.adjust(1, 1)
    return builder.as_markup()


def account_dashboard_keyboard(lang: str, account_id: str, provider: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows = [1]
    builder.button(text=t(lang, "btn_cloud_servers"), callback_data=f"cacc:servers:{account_id}", style="primary")
    if provider == "hetzner":
        builder.button(text=t(lang, "btn_cloud_addresses"), callback_data=f"hzaddr:menu:{account_id}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_account_remove"), callback_data=f"cacc:rmask:{account_id}", style="danger")
    builder.button(text=t(lang, "btn_cloud_account_list"), callback_data=f"cprov:{provider}", style="primary")
    rows += [1, 1]
    builder.adjust(*rows)
    return builder.as_markup()


def account_remove_confirm_keyboard(lang: str, account_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_account_remove_confirm"), callback_data=f"cacc:rm:{account_id}", style="danger")
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}", style="primary")
    builder.adjust(1, 1)
    return builder.as_markup()


def servers_list_keyboard(lang: str, account_id: str, servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for server in servers:
        builder.button(text=server_list_label(server), callback_data=f"csrv:view:{account_id}:{server.uuid}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_server_add"), callback_data=f"csrv:add:{account_id}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}", style="primary")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def server_detail_keyboard(lang: str, account_id: str, server) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if server.state == "stopped":
        builder.button(text=t(lang, "btn_cloud_server_start"), callback_data=f"csrv:start:{account_id}:{server.uuid}", style="primary")
    else:
        builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"csrv:stop:{account_id}:{server.uuid}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_restart"), callback_data=f"csrv:restart:{account_id}:{server.uuid}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_plan"), callback_data=f"cplan:start:{account_id}:{server.uuid}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_storage"), callback_data=f"csto:list:{account_id}:{server.uuid}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_ips"), callback_data=f"cip:list:{account_id}:{server.uuid}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_delete"), callback_data=f"csrv:delask:{account_id}:{server.uuid}", style="danger")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"cacc:servers:{account_id}", style="primary")
    builder.adjust(2, 1, 2, 1, 1)
    return builder.as_markup()


def server_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_cloud_server_delete_confirm"), callback_data=f"csrv:del:{account_id}:{server_uuid}"
    , style="danger")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"cacc:servers:{account_id}", style="primary")
    builder.adjust(1, 1)
    return builder.as_markup()


def paginated_pick_keyboard(
    lang: str,
    options: list[tuple[str, str]],
    page: int,
    nav_prefix: str,
    cancel_callback: str = "ccreate:cancel",
) -> InlineKeyboardMarkup:
    """Renders one page (PAGE_SIZE items) of a (label, callback_data) list —
    e.g. zones/plans/templates — with ◀️/▶️ navigation when there's more
    than one page, so a long UpCloud catalog never overflows one screen."""
    total_pages = max(1, -(-len(options) // PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))
    page_options = options[page * PAGE_SIZE : (page + 1) * PAGE_SIZE]

    builder = InlineKeyboardBuilder()
    for label, callback_data in page_options:
        builder.button(text=label, callback_data=callback_data, style="primary")
    rows = [1] * len(page_options)

    nav_count = 0
    if page > 0:
        builder.button(text="◀️", callback_data=f"{nav_prefix}:{page - 1}", style="primary")
        nav_count += 1
    if page < total_pages - 1:
        builder.button(text="▶️", callback_data=f"{nav_prefix}:{page + 1}", style="primary")
        nav_count += 1
    if nav_count:
        rows.append(nav_count)

    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=cancel_callback, style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def create_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="ccreate:cancel", style="danger")
    builder.adjust(1)
    return builder.as_markup()


def create_auth_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_auth_password"), callback_data="ccreate:auth:password", style="primary")
    builder.button(text=t(lang, "btn_cloud_auth_key"), callback_data="ccreate:auth:key", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="ccreate:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def create_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_create_confirm"), callback_data="ccreate:confirm", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="ccreate:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Generic "server must be stopped first" gate ---
# UpCloud refuses several operations (plan change, delete, backup restore)
# while the server is running — this same keyboard (stop it / go back)
# covers all of them.


def must_stop_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"csrv:stop:{account_id}:{server_uuid}", style="primary")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def back_to_server_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    # No "Stop" button here on purpose: while the server is in 'maintenance'
    # (UpCloud's own transient state right after another action), stopping
    # it would fail with the exact same "not allowed" error — there's
    # nothing to do but wait, so only offer a way back.
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}", style="danger")
    builder.adjust(1)
    return builder.as_markup()


# --- Plan change ---


def plan_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_plan_confirm"), callback_data="cplan:confirm", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="cplan:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Storage / disks ---
#
# Every callback below carries account_id + server_uuid (+ a storage/backup
# list-position index where relevant) explicitly, the same "re-fetch by
# index" addressing already used for Marzban hosts and 3X-UI inbounds/
# clients — no server-side state to go stale, and it survives the user
# jumping around between screens.


def storage_list_keyboard(lang: str, account_id: str, server_uuid: str, storages: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, storage in enumerate(storages):
        builder.button(text=storage_list_label(storage), callback_data=f"csto:view:{account_id}:{server_uuid}:{i}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_storage_add"), callback_data=f"csto:add:{account_id}:{server_uuid}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def storage_detail_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_resize"), callback_data=f"csto:rsz:{tail}", style="primary")
    builder.button(text=t(lang, "btn_cloud_storage_backups"), callback_data=f"cbak:list:{tail}", style="primary")
    builder.button(text=t(lang, "btn_cloud_storage_backup_create"), callback_data=f"cbak:mk:{tail}", style="primary")
    builder.button(text=t(lang, "btn_cloud_storage_detach"), callback_data=f"csto:dt:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_storage_delete"), callback_data=f"csto:del:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csto:list:{account_id}:{server_uuid}", style="danger")
    builder.adjust(1, 1, 1, 1, 1, 1)
    return builder.as_markup()


def storage_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_delete_confirm"), callback_data=f"csto:delc:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csto:view:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def storage_detach_confirm_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_detach_confirm"), callback_data=f"csto:dtc:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csto:view:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def storage_wizard_cancel_keyboard(lang: str, cancel_callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=cancel_callback, style="danger")
    builder.adjust(1)
    return builder.as_markup()


def storage_attach_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_attach_confirm"), callback_data="csto:confirm_attach", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="csto:cancel_attach", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def storage_resize_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_resize_confirm"), callback_data="csto:confirm_resize", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="csto:cancel_resize", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Backups ---


def backups_list_keyboard(
    lang: str, account_id: str, server_uuid: str, storage_index: int, backups: list
) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}"
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for j, backup in enumerate(backups):
        builder.button(text=backup_list_label(backup), callback_data=f"cbak:view:{tail}:{j}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_backup_create_confirm"), callback_data=f"cbak:mk:{tail}", style="success")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"csto:view:{tail}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def backup_create_confirm_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_create_confirm"), callback_data=f"cbak:mkc:{tail}", style="success")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:list:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def backup_detail_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int, backup_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}:{backup_index}"
    list_tail = f"{account_id}:{server_uuid}:{storage_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_restore"), callback_data=f"cbak:rs:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_backup_delete"), callback_data=f"cbak:dl:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:list:{list_tail}", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def backup_restore_confirm_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int, backup_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}:{backup_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_restore_confirm"), callback_data=f"cbak:rsc:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:view:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def backup_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int, backup_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}:{backup_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_delete_confirm"), callback_data=f"cbak:dlc:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:view:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- IP addresses ---


def ips_list_keyboard(lang: str, account_id: str, server_uuid: str, ips: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, ip in enumerate(ips):
        builder.button(text=ip_list_label(ip), callback_data=f"cip:rm:{account_id}:{server_uuid}:{i}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_ip_add"), callback_data=f"cip:add:{account_id}:{server_uuid}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def ip_add_confirm_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_ip_add_confirm"), callback_data=f"cip:addc:{tail}", style="success")
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"cip:list:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def ip_remove_confirm_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_ip_remove_confirm"), callback_data=f"cip:rmc:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"cip:list:{account_id}:{server_uuid}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Azure ---


def azure_vms_list_keyboard(lang: str, account_id: str, vms: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for vm in vms:
        builder.button(text=azure_vm_list_label(vm), callback_data=f"azvm:view:{account_id}:{vm.name}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_server_add"), callback_data=f"azvm:add:{account_id}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}", style="primary")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def azure_vm_detail_keyboard(lang: str, account_id: str, vm) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if vm.power_state == "deallocated":
        builder.button(text=t(lang, "btn_cloud_server_start"), callback_data=f"azvm:start:{account_id}:{vm.name}", style="primary")
    else:
        builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"azvm:stop:{account_id}:{vm.name}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_restart"), callback_data=f"azvm:restart:{account_id}:{vm.name}", style="primary")
    builder.button(text=t(lang, "btn_azure_vm_ports"), callback_data=f"azports:list:{account_id}:{vm.name}", style="primary")
    builder.button(text=t(lang, "btn_azure_vm_reimage"), callback_data=f"azvm:reimageask:{account_id}:{vm.name}", style="danger")
    builder.button(text=t(lang, "btn_cloud_server_delete"), callback_data=f"azvm:delask:{account_id}:{vm.name}", style="danger")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"azvm:list:{account_id}", style="primary")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def azure_vm_reimage_confirm_keyboard(lang: str, account_id: str, vm_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_azure_vm_reimage"), callback_data=f"azvm:reimage:{account_id}:{vm_name}", style="danger")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"azvm:view:{account_id}:{vm_name}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Azure: ports / firewall ---


def azure_ports_list_keyboard(lang: str, account_id: str, vm_name: str, rules: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, rule in enumerate(rules):
        builder.button(text=azure_port_rule_label(lang, rule), callback_data=f"azports:delask:{account_id}:{vm_name}:{i}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_azure_port_add"), callback_data=f"azports:add:{account_id}:{vm_name}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_azure_ports_back"), callback_data=f"azvm:view:{account_id}:{vm_name}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def azure_port_cancel_keyboard(lang: str, account_id: str, vm_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=f"azports:cancel:{account_id}:{vm_name}", style="danger")
    builder.adjust(1)
    return builder.as_markup()


def azure_port_protocol_keyboard(lang: str, account_id: str, vm_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_azure_proto_tcp"), callback_data="azports:proto:tcp", style="primary")
    builder.button(text=t(lang, "btn_azure_proto_udp"), callback_data="azports:proto:udp", style="primary")
    builder.button(text=t(lang, "btn_azure_proto_any"), callback_data="azports:proto:any", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=f"azports:cancel:{account_id}:{vm_name}", style="danger")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def azure_port_delete_confirm_keyboard(lang: str, account_id: str, vm_name: str, index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_cloud_server_delete_confirm"), callback_data=f"azports:del:{account_id}:{vm_name}:{index}"
    , style="danger")
    builder.button(text=t(lang, "btn_azure_ports_back"), callback_data=f"azports:list:{account_id}:{vm_name}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def azure_vm_delete_confirm_keyboard(lang: str, account_id: str, vm_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_server_delete_confirm"), callback_data=f"azvm:del:{account_id}:{vm_name}", style="danger")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"azvm:list:{account_id}", style="primary")
    builder.adjust(1, 1)
    return builder.as_markup()


def azure_create_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="azcreate:cancel", style="danger")
    builder.adjust(1)
    return builder.as_markup()


def azure_create_auth_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_auth_password"), callback_data="azcreate:auth:password", style="primary")
    builder.button(text=t(lang, "btn_cloud_auth_key"), callback_data="azcreate:auth:key", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="azcreate:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def azure_password_mode_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_azure_pw_generate"), callback_data="azcreate:pwmode:generate", style="primary")
    builder.button(text=t(lang, "btn_azure_pw_custom"), callback_data="azcreate:pwmode:custom", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="azcreate:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def azure_zone_keyboard(lang: str, zones: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=azure_zone_label(lang, None), callback_data="azcreate:zone:none", style="primary")
    for zone in zones:
        builder.button(text=azure_zone_label(lang, zone), callback_data=f"azcreate:zone:{zone}", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="azcreate:cancel", style="danger")
    builder.adjust(1)
    return builder.as_markup()


def azure_create_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_create_confirm"), callback_data="azcreate:confirm", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="azcreate:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Hetzner ---


def hetzner_servers_list_keyboard(lang: str, account_id: str, servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for server in servers:
        builder.button(text=hetzner_server_list_label(server), callback_data=f"hzsrv:view:{account_id}:{server.id}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_server_add"), callback_data=f"hzsrv:add:{account_id}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}", style="primary")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def hetzner_server_detail_keyboard(lang: str, account_id: str, server) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if server.status == "off":
        builder.button(text=t(lang, "btn_cloud_server_start"), callback_data=f"hzsrv:start:{account_id}:{server.id}", style="primary")
    else:
        builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"hzsrv:stop:{account_id}:{server.id}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_restart"), callback_data=f"hzsrv:restart:{account_id}:{server.id}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_plan"), callback_data=f"hzplan:start:{account_id}:{server.id}", style="primary")
    builder.button(text=t(lang, "btn_cloud_server_ips"), callback_data=f"hzip:list:{account_id}:{server.id}", style="primary")
    builder.button(
        text=t(lang, "btn_hetzner_server_rebuild"), callback_data=f"hzsrv:rebuildask:{account_id}:{server.id}"
    , style="danger")
    builder.button(text=t(lang, "btn_cloud_server_delete"), callback_data=f"hzsrv:delask:{account_id}:{server.id}", style="danger")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"hzsrv:list:{account_id}", style="primary")
    builder.adjust(2, 2, 1, 1, 1)
    return builder.as_markup()


def hetzner_server_delete_confirm_keyboard(
    lang: str, account_id: str, server_id: int, has_attached_ips: bool = False
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if has_attached_ips:
        builder.button(
            text=t(lang, "btn_hetzner_server_delete_with_ips"), callback_data=f"hzsrv:delwithip:{account_id}:{server_id}"
        , style="danger")
        builder.button(
            text=t(lang, "btn_hetzner_server_delete_keep_ips"), callback_data=f"hzsrv:del:{account_id}:{server_id}"
        , style="danger")
        builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"hzsrv:list:{account_id}", style="primary")
        builder.adjust(1, 1, 1)
    else:
        builder.button(text=t(lang, "btn_cloud_server_delete_confirm"), callback_data=f"hzsrv:del:{account_id}:{server_id}", style="danger")
        builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"hzsrv:list:{account_id}", style="primary")
        builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_server_rebuild_confirm_keyboard(lang: str, account_id: str, server_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_hetzner_server_rebuild"), callback_data=f"hzsrv:rebuild:{account_id}:{server_id}", style="danger")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"hzsrv:view:{account_id}:{server_id}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_create_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzcreate:cancel", style="danger")
    builder.adjust(1)
    return builder.as_markup()


def hetzner_create_auth_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_auth_password"), callback_data="hzcreate:auth:password", style="primary")
    builder.button(text=t(lang, "btn_cloud_auth_key"), callback_data="hzcreate:auth:key", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzcreate:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def hetzner_create_ipv6_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_hetzner_ipv6_on"), callback_data="hzcreate:ipv6:on", style="primary")
    builder.button(text=t(lang, "btn_hetzner_ipv6_off"), callback_data="hzcreate:ipv6:off", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzcreate:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def hetzner_create_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_create_confirm"), callback_data="hzcreate:confirm", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzcreate:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_ips_list_keyboard(lang: str, account_id: str, server_id: int, ips: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, ip in enumerate(ips):
        builder.button(text=hetzner_ip_list_label(ip), callback_data=f"hzip:rm:{account_id}:{server_id}:{i}", style="primary")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_ip_add"), callback_data=f"hzip:add:{account_id}:{server_id}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"hzsrv:view:{account_id}:{server_id}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def hetzner_ip_add_confirm_keyboard(lang: str, account_id: str, server_id: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_id}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_ip_add_confirm"), callback_data=f"hzip:addc:{tail}", style="success")
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"hzip:list:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_ip_remove_confirm_keyboard(lang: str, account_id: str, server_id: int, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_id}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_ip_remove_confirm"), callback_data=f"hzip:rmc:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"hzip:list:{account_id}:{server_id}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_must_stop_keyboard(lang: str, account_id: str, server_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"hzsrv:stop:{account_id}:{server_id}", style="primary")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"hzsrv:view:{account_id}:{server_id}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_plan_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_plan_confirm"), callback_data="hzplan:confirm", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzplan:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Hetzner: standalone IP addresses (Primary + Floating, account-level) ---


def hetzner_addresses_menu_keyboard(lang: str, account_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_hetzner_address_category_primary"), callback_data=f"hzaddr:list:{account_id}:p", style="primary")
    builder.button(text=t(lang, "btn_hetzner_address_category_floating"), callback_data=f"hzaddr:list:{account_id}:f", style="primary")
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}", style="primary")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def hetzner_addresses_list_keyboard(lang: str, account_id: str, kind: str, addresses: list) -> InlineKeyboardMarkup:
    kind_char = "p" if kind == "primary" else "f"
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for address in addresses:
        builder.button(
            text=hetzner_address_list_label(kind, address), callback_data=f"hzaddr:view:{account_id}:{kind_char}:{address.id}"
        , style="primary")
        rows.append(1)
    buy_key = "btn_hetzner_address_buy_primary" if kind == "primary" else "btn_hetzner_address_buy_floating"
    buy_prefix = "hzaddr:buyp" if kind == "primary" else "hzaddr:buyf"
    builder.button(text=t(lang, buy_key), callback_data=f"{buy_prefix}:{account_id}", style="primary")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_addresses_back"), callback_data=f"hzaddr:menu:{account_id}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def hetzner_address_detail_keyboard(lang: str, account_id: str, kind: str, address) -> InlineKeyboardMarkup:
    kind_char = "p" if kind == "primary" else "f"
    tail = f"{account_id}:{kind_char}:{address.id}"
    builder = InlineKeyboardBuilder()
    if address.server_id:
        builder.button(text=t(lang, "btn_hetzner_address_unassign"), callback_data=f"hzaddr:unassign:{tail}", style="primary")
    else:
        builder.button(text=t(lang, "btn_hetzner_address_assign"), callback_data=f"hzaddr:assignask:{tail}", style="primary")
    builder.button(text=t(lang, "btn_hetzner_address_delete"), callback_data=f"hzaddr:delask:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_addresses_back"), callback_data=f"hzaddr:list:{account_id}:{kind_char}", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def hetzner_address_delete_confirm_keyboard(lang: str, account_id: str, kind: str, address_id: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{'p' if kind == 'primary' else 'f'}:{address_id}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_hetzner_address_delete_confirm"), callback_data=f"hzaddr:del:{tail}", style="danger")
    builder.button(text=t(lang, "btn_cloud_addresses_back"), callback_data=f"hzaddr:view:{tail}", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def hetzner_address_create_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="IPv4", callback_data="hzaddrcreate:type:ipv4", style="primary")
    builder.button(text="IPv6", callback_data="hzaddrcreate:type:ipv6", style="primary")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzaddrcreate:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def hetzner_address_create_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_create_confirm"), callback_data="hzaddrcreate:confirm", style="success")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="hzaddrcreate:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


