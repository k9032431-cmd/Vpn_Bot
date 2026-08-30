from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import t


def whois_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="whois:cancel")
    return builder.as_markup()


def whois_again_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_whois_again"), callback_data="menu:whois")
    # A dedicated callback (not the shared "menu:back") — the result above
    # this keyboard was sent as a reply to the query, and editing a reply
    # in place keeps Telegram's quoted-message header forever; this always
    # sends a fresh, non-reply message instead.
    builder.button(text=t(lang, "btn_main_menu"), callback_data="whois:home")
    builder.adjust(1, 1)
    return builder.as_markup()
