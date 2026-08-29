from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def node_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ Marzban Node", callback_data="node:marzban")
    builder.button(text="🛡 PasarGuard", callback_data="node:pasarguard")
    builder.button(text="⬅️ Назад", callback_data="menu:back")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="nodesetup:cancel")
    return builder.as_markup()


def confirm_install_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Установить", callback_data="nodeinstall:confirm")
    builder.button(text="❌ Отмена", callback_data="nodeinstall:cancel")
    builder.adjust(1, 1)
    return builder.as_markup()


def node_result_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🖥 В меню Node", callback_data="menu:node")
    builder.button(text="🏠 Главное меню", callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()
