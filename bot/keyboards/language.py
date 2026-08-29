from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import LANGUAGE_LABELS, LANGUAGES, t


def language_picker_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code in LANGUAGES:
        builder.button(text=LANGUAGE_LABELS[code], callback_data=f"lang:{code}")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()
