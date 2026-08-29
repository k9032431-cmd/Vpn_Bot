from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.language import language_picker_keyboard
from bot.keyboards.main_menu import main_menu_keyboard
from bot.services.user_prefs import user_prefs
from bot.texts.main import language_prompt_text, language_saved_text
from bot.texts.translations import LANGUAGES

router = Router(name="language")


@router.callback_query(F.data == "menu:language")
async def cb_language_menu(callback: CallbackQuery, lang: str) -> None:
    await callback.message.edit_text(
        language_prompt_text(lang), reply_markup=language_picker_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data.in_({f"lang:{code}" for code in LANGUAGES}))
async def cb_set_language(callback: CallbackQuery) -> None:
    new_lang = callback.data.split(":", 1)[1]
    await user_prefs.set_language(callback.from_user.id, new_lang)
    await callback.message.edit_text(
        language_saved_text(new_lang), reply_markup=main_menu_keyboard(new_lang)
    )
    await callback.answer()
