from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import t


def node_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_marzban"), callback_data="node:marzban")
    builder.button(text=t(lang, "btn_pasarguard"), callback_data="node:pasarguard")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def auth_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_auth_password"), callback_data="nodeauth:password")
    builder.button(text=t(lang, "btn_auth_key"), callback_data="nodeauth:key")
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodesetup:cancel")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def ports_choice_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_ports_default"), callback_data="nodeports:default")
    builder.button(text=t(lang, "btn_ports_custom"), callback_data="nodeports:custom")
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodesetup:cancel")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodesetup:cancel")
    return builder.as_markup()


def confirm_install_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_install"), callback_data="nodeinstall:confirm")
    builder.button(text=t(lang, "btn_cancel"), callback_data="nodeinstall:cancel")
    builder.adjust(1, 1)
    return builder.as_markup()


def node_result_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_node_menu"), callback_data="menu:node")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()
