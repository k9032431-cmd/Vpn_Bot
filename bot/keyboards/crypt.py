from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.translations import t


def crypt_action_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_crypt_encrypt"), callback_data="crypt:action:encrypt")
    builder.button(text=t(lang, "btn_crypt_decrypt"), callback_data="crypt:action:decrypt")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def crypt_vpn_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_crypt_vpn_happ"), callback_data="crypt:vpn:happ")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:crypt")
    builder.adjust(1, 1)
    return builder.as_markup()


def crypt_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="crypt:cancel")
    return builder.as_markup()


def crypt_result_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_crypt_again"), callback_data="menu:crypt")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()
