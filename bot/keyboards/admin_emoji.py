from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.premium_emoji import button_icon, sections, slots_in_section
from bot.texts.translations import t


def admin_emoji_sections_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for section in sections():
        builder.button(text=section, callback_data=f"adminemoji:section:{section}", style="primary")
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back", style="danger")
    builder.adjust(*([1] * len(sections())), 1)
    return builder.as_markup()


def admin_emoji_section_keyboard(lang: str, section: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    slots = slots_in_section(section)
    for slot in slots:
        builder.button(
            text=slot.label, callback_data=f"adminemoji:slot:{slot.key}", style="primary",
            icon_custom_emoji_id=button_icon(slot.key),
        )
    builder.button(text=t(lang, "btn_admin_emoji_back_sections"), callback_data="adminemoji:sections", style="danger")
    builder.adjust(*([1] * len(slots)), 1)
    return builder.as_markup()


def admin_emoji_slot_keyboard(lang: str, key: str, section: str, has_override: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows = []
    builder.button(text=t(lang, "btn_admin_emoji_set"), callback_data=f"adminemoji:setask:{key}", style="primary")
    rows.append(1)
    if has_override:
        builder.button(text=t(lang, "btn_admin_emoji_reset"), callback_data=f"adminemoji:reset:{key}", style="danger")
        rows.append(1)
    builder.button(text=t(lang, "btn_back"), callback_data=f"adminemoji:section:{section}", style="danger")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def admin_emoji_waiting_cancel_keyboard(lang: str, key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cloud_cancel"), callback_data=f"adminemoji:slot:{key}", style="danger")
    builder.adjust(1)
    return builder.as_markup()
