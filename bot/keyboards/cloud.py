from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.cloud import ACTIVE_PROVIDERS, PROVIDERS, account_list_label, server_list_label
from bot.texts.translations import t


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
    builder.button(text=t(lang, "btn_cloud_server_delete"), callback_data=f"csrv:delask:{account_id}:{server.uuid}")
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"cacc:servers:{account_id}")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def server_delete_confirm_keyboard(lang: str, account_id: str, server_uuid: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_cloud_server_delete_confirm"), callback_data=f"csrv:del:{account_id}:{server_uuid}"
    )
    builder.button(text=t(lang, "btn_cloud_servers_list"), callback_data=f"cacc:servers:{account_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def create_pick_keyboard(lang: str, options: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """options: list of (label, callback_data) pairs, e.g. zones/plans/templates."""
    builder = InlineKeyboardBuilder()
    for label, callback_data in options:
        builder.button(text=label, callback_data=callback_data)
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data="ccreate:cancel")
    builder.adjust(*([1] * len(options)), 1)
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
