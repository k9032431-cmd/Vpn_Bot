from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🖥 Node", callback_data="menu:node")
    builder.button(text="☁️ Cloud VPN", callback_data="menu:cloud_vpn")
    builder.button(text="👤 Cloud Account", callback_data="menu:cloud_account")
    builder.button(text="🔐 Crypt/Decrypt", callback_data="menu:crypt")
    builder.button(text="🌐 Language", callback_data="menu:language")
    builder.button(text="ℹ️ Info", callback_data="menu:info")
    builder.button(text="🆘 SOS", callback_data="menu:sos")
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu:back")
    return builder.as_markup()
