from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import t


def admin_panel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_admin_emoji"), callback_data="adminpanel:emoji", style="primary")
    builder.button(text=t(lang, "btn_admin_stats"), callback_data="adminpanel:stats", style="primary")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def admin_panel_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_back"), callback_data="menu:admin", style="danger")
    builder.adjust(1)
    return builder.as_markup()
