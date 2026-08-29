from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import config
from bot.texts.support import build_sos_chat_url
from bot.texts.translations import t


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_node"), callback_data="menu:node")
    builder.button(text=t(lang, "btn_panel"), callback_data="menu:panel")
    builder.button(text=t(lang, "btn_cloud_vpn"), callback_data="menu:cloud_vpn")
    builder.button(text=t(lang, "btn_cloud_account"), callback_data="menu:cloud_account")
    builder.button(text=t(lang, "btn_crypt"), callback_data="menu:crypt")
    builder.button(text=t(lang, "btn_language"), callback_data="menu:language")
    builder.button(text=t(lang, "btn_info"), callback_data="menu:info")

    # When a support contact is configured, SOS opens a chat with the admin
    # directly (pre-filled greeting) instead of a menu screen.
    sos_url = build_sos_chat_url(config.support_contact, t(lang, "sos_greeting"))
    if sos_url:
        builder.button(text=t(lang, "btn_sos"), url=sos_url)
    else:
        builder.button(text=t(lang, "btn_sos"), callback_data="menu:sos")

    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    return builder.as_markup()
