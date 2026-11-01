from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu_keyboard
from bot.texts.main import WELCOME_BANNER, welcome_text

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str) -> None:
    name = message.from_user.first_name or message.from_user.username or ""
    await message.answer_photo(WELCOME_BANNER, caption=welcome_text(lang, name), reply_markup=main_menu_keyboard(lang))
