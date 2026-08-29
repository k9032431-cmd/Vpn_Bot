from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu_keyboard
from bot.texts.main import welcome_text

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str) -> None:
    await message.answer(welcome_text(lang), reply_markup=main_menu_keyboard(lang))
