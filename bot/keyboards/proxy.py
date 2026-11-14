from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.premium_emoji import button_icon
from bot.texts.translations import t


def proxy_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_tg_proxy"),
        callback_data="proxy:tg",
        style="primary",
        icon_custom_emoji_id=button_icon("tg_proxy"),
    )
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def auth_method_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_auth_password"), callback_data="proxyauth:password", style="primary")
    builder.button(text=t(lang, "btn_auth_key"), callback_data="proxyauth:key", style="primary")
    builder.button(text=t(lang, "btn_cancel"), callback_data="proxysetup:cancel", style="danger")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="proxysetup:cancel", style="danger")
    return builder.as_markup()


def confirm_install_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_install"), callback_data="proxyinstall:confirm", style="primary")
    builder.button(text=t(lang, "btn_cancel"), callback_data="proxyinstall:cancel", style="danger")
    builder.adjust(1, 1)
    return builder.as_markup()


def proxy_result_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_proxy_menu"), callback_data="menu:proxy", style="primary")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back", style="primary")
    builder.adjust(1, 1)
    return builder.as_markup()
