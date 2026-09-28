from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import config
from bot.texts.support import build_sos_chat_url
from bot.texts.translations import t


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Bot API 9.4 button "style" (primary/success/danger/default) -- used
    # sparingly so it actually reads as a hierarchy: the four
    # infrastructure-management sections in blue, SOS in red for urgency,
    # everything else left at the client's default color.
    builder.button(text=t(lang, "btn_node"), callback_data="menu:node", style="primary")
    builder.button(text=t(lang, "btn_panel"), callback_data="menu:panel", style="primary")
    builder.button(text=t(lang, "btn_profile"), callback_data="menu:profile")
    builder.button(text=t(lang, "btn_whois"), callback_data="menu:whois")
    builder.button(text=t(lang, "btn_cloud_vps"), callback_data="menu:cloud_vps", style="primary")
    builder.button(text=t(lang, "btn_cloud_account"), callback_data="menu:cloud_account", style="primary")
    builder.button(text=t(lang, "btn_crypt"), callback_data="menu:crypt")
    builder.button(text=t(lang, "btn_language"), callback_data="menu:language")
    builder.button(text=t(lang, "btn_info"), callback_data="menu:info")

    # When a support contact is configured, SOS opens a chat with the admin
    # directly (pre-filled greeting) instead of a menu screen.
    sos_url = build_sos_chat_url(config.support_contact, t(lang, "sos_greeting"))
    if sos_url:
        builder.button(text=t(lang, "btn_sos"), url=sos_url, style="danger")
    else:
        builder.button(text=t(lang, "btn_sos"), callback_data="menu:sos", style="danger")

    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()


def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    return builder.as_markup()
