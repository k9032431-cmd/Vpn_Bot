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
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()
