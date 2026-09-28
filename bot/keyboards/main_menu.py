from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import config
from bot.texts.premium_emoji import button_icon
from bot.texts.support import build_sos_chat_url
from bot.texts.translations import t


def main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Bot API 9.4 button "style" (primary/success/danger/default) -- used
    # sparingly so it actually reads as a hierarchy: the four
    # infrastructure-management sections in blue, SOS in red for urgency,
    # everything else left at the client's default color. icon_custom_emoji_id
    # (also Bot API 9.4) reuses the same IDS as the message-text premium
    # emoji -- see bot/texts/premium_emoji.py for the Premium/Fragment
    # requirement that gates whether Telegram actually shows it.
    builder.button(text=t(lang, "btn_node"), callback_data="menu:node", style="primary", icon_custom_emoji_id=button_icon("node"))
    builder.button(text=t(lang, "btn_panel"), callback_data="menu:panel", style="primary", icon_custom_emoji_id=button_icon("panel"))
    builder.button(text=t(lang, "btn_profile"), callback_data="menu:profile", icon_custom_emoji_id=button_icon("profile"))
    builder.button(text=t(lang, "btn_whois"), callback_data="menu:whois", icon_custom_emoji_id=button_icon("whois"))
    builder.button(text=t(lang, "btn_cloud_vps"), callback_data="menu:cloud_vps", style="primary", icon_custom_emoji_id=button_icon("cloud_vps"))
    builder.button(text=t(lang, "btn_cloud_account"), callback_data="menu:cloud_account", style="primary", icon_custom_emoji_id=button_icon("cloud_account"))
    builder.button(text=t(lang, "btn_crypt"), callback_data="menu:crypt", icon_custom_emoji_id=button_icon("crypt"))
    builder.button(text=t(lang, "btn_language"), callback_data="menu:language", icon_custom_emoji_id=button_icon("language"))
    builder.button(text=t(lang, "btn_info"), callback_data="menu:info", icon_custom_emoji_id=button_icon("info"))

    # When a support contact is configured, SOS opens a chat with the admin
    # directly (pre-filled greeting) instead of a menu screen.
    sos_url = build_sos_chat_url(config.support_contact, t(lang, "sos_greeting"))
    if sos_url:
        builder.button(text=t(lang, "btn_sos"), url=sos_url, style="danger", icon_custom_emoji_id=button_icon("sos"))
    else:
        builder.button(text=t(lang, "btn_sos"), callback_data="menu:sos", style="danger", icon_custom_emoji_id=button_icon("sos"))

    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()


def back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    return builder.as_markup()
