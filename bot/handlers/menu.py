from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.main_menu import back_keyboard, main_menu_keyboard
from bot.texts.main import WELCOME_BANNER, section_text, welcome_text
from bot.utils.messages import show_text

router = Router(name="menu")


@router.callback_query(F.data == "menu:back")
async def cb_back(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    # The welcome screen carries a banner photo, so a plain text message
    # can't just be edited into it -- replace it instead.
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer_photo(
        WELCOME_BANNER, caption=welcome_text(lang), reply_markup=main_menu_keyboard(lang)
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
    await show_text(callback, text, reply_markup=back_keyboard(lang))
    await callback.answer()
