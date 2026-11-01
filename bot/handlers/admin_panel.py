from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.config import config
from bot.handlers.admin_emoji import show_emoji_sections
from bot.keyboards.admin_panel import admin_panel_back_keyboard, admin_panel_keyboard
from bot.services.user_stats import user_stats
from bot.texts import admin_panel as texts

router = Router(name="admin_panel")


def _is_admin(user_id: int) -> bool:
    return config.is_admin(user_id)


@router.callback_query(F.data == "menu:admin")
async def cb_admin_panel_open(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(texts.admin_panel_text(lang), reply_markup=admin_panel_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "adminpanel:emoji")
async def cb_admin_panel_emoji(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await show_emoji_sections(callback, lang)
    await callback.answer()


@router.callback_query(F.data == "adminpanel:stats")
async def cb_admin_panel_stats(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    if not _is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    total = await user_stats.total_count()
    new_24h = await user_stats.count_new_within(24)
    new_7d = await user_stats.count_new_within(24 * 7)
    await callback.message.edit_text(
        texts.admin_stats_text(lang, total, new_24h, new_7d), reply_markup=admin_panel_back_keyboard(lang)
    )
    await callback.answer()
