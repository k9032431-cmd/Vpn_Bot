from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.main_menu import back_keyboard, main_menu_keyboard
from bot.texts.ru import SECTION_TEXTS, WELCOME_TEXT

router = Router(name="menu")


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("menu:"))
async def cb_section(callback: CallbackQuery, state: FSMContext) -> None:
    section = callback.data.split(":", 1)[1]
    text = SECTION_TEXTS.get(section)
    if text is None:
        await callback.answer()
        return
    # Leaving to another section drops any in-progress node-setup dialog
    # (e.g. a pending IP/password prompt), so a stray text message later
    # can't be misread as SSH credentials.
    await state.clear()
    await callback.message.edit_text(text, reply_markup=back_keyboard())
    await callback.answer()
