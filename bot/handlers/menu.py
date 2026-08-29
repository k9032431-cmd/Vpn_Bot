from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.config import config
from bot.keyboards.main_menu import back_keyboard, main_menu_keyboard
from bot.texts.main import section_text, welcome_text

router = Router(name="menu")


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    show_node = config.is_node_authorized(callback.from_user.id)
    await callback.message.edit_text(
        welcome_text(lang), reply_markup=main_menu_keyboard(lang, show_node)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("menu:"))
async def cb_section(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    section = callback.data.split(":", 1)[1]
    text = section_text(lang, section)
    if text is None:
        await callback.answer()
        return
    # Leaving to another section drops any in-progress node-setup dialog
    # (e.g. a pending IP/password prompt), so a stray text message later
    # can't be misread as SSH credentials.
    await state.clear()
    await callback.message.edit_text(text, reply_markup=back_keyboard(lang))
    await callback.answer()
