from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.keyboards.admin_emoji import (
    admin_emoji_section_keyboard,
    admin_emoji_sections_keyboard,
    admin_emoji_slot_keyboard,
    admin_emoji_waiting_cancel_keyboard,
)
from bot.services import emoji_overrides
from bot.states.admin_emoji import AdminEmojiStates
from bot.texts import admin_emoji as texts
from bot.texts.premium_emoji import slot as get_slot
from bot.utils.messages import advance_screen, track_prompt

router = Router(name="admin_emoji")


def _is_admin(user_id: int) -> bool:
    return config.is_admin(user_id)


@router.callback_query(F.data == "menu:admin_emoji")
async def cb_admin_emoji_open(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(texts.admin_emoji_sections_text(lang), reply_markup=admin_emoji_sections_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "adminemoji:sections")
async def cb_admin_emoji_sections(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(texts.admin_emoji_sections_text(lang), reply_markup=admin_emoji_sections_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("adminemoji:section:"))
async def cb_admin_emoji_section(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    section = callback.data.split(":", 2)[2]
    await state.clear()
    await callback.message.edit_text(
        texts.admin_emoji_section_text(lang, section), reply_markup=admin_emoji_section_keyboard(lang, section)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adminemoji:slot:"))
async def cb_admin_emoji_slot(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    key = callback.data.split(":", 2)[2]
    slot = get_slot(key)
    if slot is None:
        await callback.answer()
        return
    await state.clear()
    has_override = bool(emoji_overrides.get(key))
    await callback.message.edit_text(
        texts.admin_emoji_slot_text(lang, slot, has_override),
        reply_markup=admin_emoji_slot_keyboard(lang, key, slot.section, has_override),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adminemoji:setask:"))
async def cb_admin_emoji_set_ask(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    key = callback.data.split(":", 2)[2]
    slot = get_slot(key)
    if slot is None:
        await callback.answer()
        return
    await state.update_data(editing_key=key)
    await state.set_state(AdminEmojiStates.waiting_emoji)
    await callback.message.edit_text(
        texts.admin_emoji_waiting_text(lang, slot), reply_markup=admin_emoji_waiting_cancel_keyboard(lang, key)
    )
    await track_prompt(callback, state)
    await callback.answer()


@router.callback_query(F.data.startswith("adminemoji:reset:"))
async def cb_admin_emoji_reset(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    key = callback.data.split(":", 2)[2]
    slot = get_slot(key)
    if slot is None:
        await callback.answer()
        return
    emoji_overrides.clear_override(key)
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        texts.admin_emoji_slot_text(lang, slot, False),
        reply_markup=admin_emoji_slot_keyboard(lang, key, slot.section, False),
    )


def _extract_custom_emoji_id(message: Message) -> str | None:
    for entity in message.entities or []:
        if entity.type == "custom_emoji" and entity.custom_emoji_id:
            return entity.custom_emoji_id
    return None


@router.message(AdminEmojiStates.waiting_emoji)
async def process_admin_emoji_input(message: Message, state: FSMContext, lang: str) -> None:
    if not _is_admin(message.from_user.id):
        await state.clear()
        return
    data = await state.get_data()
    key = data.get("editing_key")
    slot = get_slot(key) if key else None
    if slot is None:
        await state.clear()
        return

    custom_id = _extract_custom_emoji_id(message)
    if not custom_id:
        text = (message.text or "").strip()
        if text.isdigit() and len(text) >= 5:
            custom_id = text

    if not custom_id:
        await advance_screen(
            message, state, texts.admin_emoji_invalid_text(lang),
            reply_markup=admin_emoji_waiting_cancel_keyboard(lang, key),
        )
        return

    emoji_overrides.set_override(key, custom_id)
    await advance_screen(
        message, state, texts.admin_emoji_set_ok_text(lang, slot),
        reply_markup=admin_emoji_slot_keyboard(lang, key, slot.section, True),
    )
    await state.clear()
