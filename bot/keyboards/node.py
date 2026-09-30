from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import t


def node_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_marzban"), callback_data="node:marzban", style="primary")
    builder.button(text=t(lang, "btn_pasarguard"), callback_data="node:pasarguard", style="primary")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def auth_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_auth_password"), callback_data="nodeauth:password", style="primary")
    builder.button(text=t(lang, "btn_auth_key"), callback_data="nodeauth:key", style="primary")
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodesetup:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodesetup:cancel", style="danger")
    return builder.as_markup()


def confirm_install_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_install"), callback_data="nodeinstall:confirm", style="primary")
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodeinstall:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def node_result_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_node_menu"), callback_data="menu:node", style="primary")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back", style="primary")
    builder.adjust(1, 1)
    return builder.as_markup()
