from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.cloud import (
    ACTIVE_PROVIDERS,
    PROVIDERS,
    account_list_label,
    backup_list_label,
    ip_list_label,
    server_list_label,
    storage_list_label,
)
from bot.texts.translations import t

PAGE_SIZE = 5


def provider_list_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for provider in PROVIDERS:
        builder.button(text=t(lang, f"btn_cloud_provider_{provider}"), callback_data=f"cprov:{provider}")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    builder.adjust(*([1] * len(PROVIDERS)), 1)
    return builder.as_markup()


def provider_soon_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_provider_list"), callback_data="menu:cloud_vps")
    builder.adjust(1)
    return builder.as_markup()


def account_list_keyboard(lang: str, provider: str, accounts: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for account in accounts:
        builder.button(text=account_list_label(account), callback_data=f"cview:{account['id']}")
        rows.append(1)
    if provider in ACTIVE_PROVIDERS:
        builder.button(text=t(lang, "btn_cloud_account_add"), callback_data=f"cadd:{provider}")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_provider_list"), callback_data="menu:cloud_vps")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def cloud_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="csetup:cancel")
    return builder.as_markup()


def cloud_error_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_provider_list"), callback_data="menu:cloud_vps")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()


def account_dashboard_keyboard(lang: str, account_id: str, provider: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_servers"), callback_data=f"cacc:servers:{account_id}")
    builder.button(text=t(lang, "btn_cloud_account_remove"), callback_data=f"cacc:rmask:{account_id}")
    builder.button(text=t(lang, "btn_cloud_account_list"), callback_data=f"cprov:{provider}")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def account_remove_confirm_keyboard(lang: str, account_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_account_remove_confirm"), callback_data=f"cacc:rm:{account_id}")
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def servers_list_keyboard(lang: str, account_id: str, servers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for server in servers:
        builder.button(text=server_list_label(server), callback_data=f"csrv:view:{account_id}:{server.uuid}")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_server_add"), callback_data=f"csrv:add:{account_id}")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_account_dashboard"), callback_data=f"cview:{account_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def server_detail_keyboard(lang: str, account_id: str, server) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if server.state == "stopped":
        builder.button(text=t(lang, "btn_cloud_server_start"), callback_data=f"csrv:start:{account_id}:{server.uuid}")
    else:
        builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"csrv:stop:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_server_restart"), callback_data=f"csrv:restart:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_server_plan"), callback_data=f"cplan:start:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_server_storage"), callback_data=f"csto:list:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_server_ips"), callback_data=f"cip:list:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_server_delete"), callback_data=f"csrv:delask:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"cacc:servers:{account_id}")
    builder.adjust(2, 1, 2, 1, 1)
    return builder.as_markup()


def server_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_cloud_server_delete_confirm"), callback_data=f"csrv:del:{account_id}:{server_uuid}"
    )
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"cacc:servers:{account_id}")
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
        builder.button(text=label, callback_data=callback_data)
    rows = [1] * len(page_options)

    nav_count = 0
    if page > 0:
        builder.button(text="◀️", callback_data=f"{nav_prefix}:{page - 1}")
        nav_count += 1
    if page < total_pages - 1:
        builder.button(text="▶️", callback_data=f"{nav_prefix}:{page + 1}")
        nav_count += 1
    if nav_count:
        rows.append(nav_count)

    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=cancel_callback)
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def create_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="ccreate:cancel")
    builder.adjust(1)
    return builder.as_markup()


def create_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_create_confirm"), callback_data="ccreate:confirm")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="ccreate:cancel")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- Plan change ---


def plan_must_stop_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_server_stop"), callback_data=f"csrv:stop:{account_id}:{server_uuid}")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}")
    builder.adjust(1, 1)
    return builder.as_markup()


def plan_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_plan_confirm"), callback_data="cplan:confirm")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="cplan:cancel")
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
        builder.button(text=storage_list_label(storage), callback_data=f"csto:view:{account_id}:{server_uuid}:{i}")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_storage_add"), callback_data=f"csto:add:{account_id}:{server_uuid}")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def storage_detail_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_resize"), callback_data=f"csto:rsz:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_backups"), callback_data=f"cbak:list:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_backup_create"), callback_data=f"cbak:mk:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_detach"), callback_data=f"csto:dt:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_delete"), callback_data=f"csto:del:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csto:list:{account_id}:{server_uuid}")
    builder.adjust(1, 1, 1, 1, 1, 1)
    return builder.as_markup()


def storage_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_delete_confirm"), callback_data=f"csto:delc:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csto:view:{tail}")
    builder.adjust(1, 1)
    return builder.as_markup()


def storage_detach_confirm_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_detach_confirm"), callback_data=f"csto:dtc:{tail}")
    builder.button(text=t(lang, "btn_cloud_storage_back"), callback_data=f"csto:view:{tail}")
    builder.adjust(1, 1)
    return builder.as_markup()


def storage_wizard_cancel_keyboard(lang: str, cancel_callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=cancel_callback)
    builder.adjust(1)
    return builder.as_markup()


def storage_attach_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_attach_confirm"), callback_data="csto:confirm_attach")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="csto:cancel_attach")
    builder.adjust(1, 1)
    return builder.as_markup()


def storage_resize_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_storage_resize_confirm"), callback_data="csto:confirm_resize")
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="csto:cancel_resize")
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
        builder.button(text=backup_list_label(backup), callback_data=f"cbak:view:{tail}:{j}")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_backup_create_confirm"), callback_data=f"cbak:mk:{tail}")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"csto:view:{tail}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def backup_create_confirm_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_create_confirm"), callback_data=f"cbak:mkc:{tail}")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:list:{tail}")
    builder.adjust(1, 1)
    return builder.as_markup()


def backup_detail_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int, backup_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}:{backup_index}"
    list_tail = f"{account_id}:{server_uuid}:{storage_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_restore"), callback_data=f"cbak:rs:{tail}")
    builder.button(text=t(lang, "btn_cloud_backup_delete"), callback_data=f"cbak:dl:{tail}")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:list:{list_tail}")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def backup_restore_confirm_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int, backup_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}:{backup_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_restore_confirm"), callback_data=f"cbak:rsc:{tail}")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:view:{tail}")
    builder.adjust(1, 1)
    return builder.as_markup()


def backup_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str, storage_index: int, backup_index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{storage_index}:{backup_index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_backup_delete_confirm"), callback_data=f"cbak:dlc:{tail}")
    builder.button(text=t(lang, "btn_cloud_backups_back"), callback_data=f"cbak:view:{tail}")
    builder.adjust(1, 1)
    return builder.as_markup()


# --- IP addresses ---


def ips_list_keyboard(lang: str, account_id: str, server_uuid: str, ips: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, ip in enumerate(ips):
        builder.button(text=ip_list_label(ip), callback_data=f"cip:rm:{account_id}:{server_uuid}:{i}")
        rows.append(1)
    builder.button(text=t(lang, "btn_cloud_ip_add"), callback_data=f"cip:add:{account_id}:{server_uuid}")
    rows.append(1)
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"csrv:view:{account_id}:{server_uuid}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def ip_add_confirm_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_ip_add_confirm"), callback_data=f"cip:addc:{tail}")
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"cip:list:{tail}")
    builder.adjust(1, 1)
    return builder.as_markup()


def ip_remove_confirm_keyboard(lang: str, account_id: str, server_uuid: str, index: int) -> InlineKeyboardMarkup:
    tail = f"{account_id}:{server_uuid}:{index}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_ip_remove_confirm"), callback_data=f"cip:rmc:{tail}")
    builder.button(text=t(lang, "btn_cloud_ips_back"), callback_data=f"cip:list:{account_id}:{server_uuid}")
    builder.adjust(1, 1)
    return builder.as_markup()
