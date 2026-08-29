from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.config import config
from bot.keyboards.main_menu import main_menu_keyboard
from bot.texts.main import welcome_text

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, lang: str) -> None:
    show_node = config.is_node_authorized(message.from_user.id)
    await message.answer(welcome_text(lang), reply_markup=main_menu_keyboard(lang, show_node))
