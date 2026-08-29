from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import t


def panel_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_marzban"), callback_data="panel:marzban")
    builder.button(text=t(lang, "btn_panel_pasarguard"), callback_data="panel:pasarguard")
    builder.button(text=t(lang, "btn_panel_3xui"), callback_data="panel:3xui")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def panel_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="panelsetup:cancel")
    return builder.as_markup()


def panel_error_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_menu"), callback_data="menu:panel")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_dashboard_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_stats"), callback_data="paneldash:stats")
    builder.button(text=t(lang, "btn_panel_users"), callback_data="paneldash:users")
    builder.button(text=t(lang, "btn_panel_disconnect"), callback_data="paneldash:disconnect")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def panel_dashboard_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data="paneldash:back")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_disconnect_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_disconnect_confirm"), callback_data="paneldash:disconnect_confirm")
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data="paneldash:back")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_users_keyboard(lang: str, usernames: list[str], manageable: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    if manageable:
        for name in usernames:
            builder.button(text=f"👤 {name}", callback_data=f"paneluser:view:{name}")
            rows.append(1)
        builder.button(text=t(lang, "btn_panel_create_user"), callback_data="paneldash:create_user")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data="paneldash:back")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_user_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="paneluser:cancel")
    return builder.as_markup()


def panel_create_user_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_create_confirm"), callback_data="paneluser:create_confirm")
    builder.button(text=t(lang, "btn_cancel"), callback_data="paneluser:cancel")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_user_detail_keyboard(lang: str, username: str, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_key = "btn_panel_user_disable" if status == "active" else "btn_panel_user_enable"
    builder.button(text=t(lang, toggle_key), callback_data=f"paneluser:toggle:{username}")
    builder.button(text=t(lang, "btn_panel_user_reset"), callback_data=f"paneluser:reset:{username}")
    builder.button(text=t(lang, "btn_panel_user_edit"), callback_data=f"paneluser:edit:{username}")
    builder.button(text=t(lang, "btn_panel_user_delete"), callback_data=f"paneluser:delete_ask:{username}")
    builder.button(text=t(lang, "btn_panel_users"), callback_data="paneldash:users")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def panel_user_delete_confirm_keyboard(lang: str, username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_user_delete_confirm"), callback_data=f"paneluser:delete_confirm:{username}"
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"paneluser:view:{username}")
    builder.adjust(1, 1)
    return builder.as_markup()
