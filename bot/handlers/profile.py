from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.main_menu import back_keyboard
from bot.services.panel_store import panel_store
from bot.texts.profile import profile_text

router = Router(name="profile")


@router.callback_query(F.data == "menu:profile")
async def cb_profile(callback: CallbackQuery, lang: str) -> None:
    panels = await panel_store.list(callback.from_user.id)
    await callback.message.edit_text(
        profile_text(lang, callback.from_user, len(panels)), reply_markup=back_keyboard(lang)
    )
    await callback.answer()
