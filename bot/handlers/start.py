from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu_keyboard
from bot.texts.ru import WELCOME_TEXT

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())
