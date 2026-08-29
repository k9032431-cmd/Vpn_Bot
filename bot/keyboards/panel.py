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
