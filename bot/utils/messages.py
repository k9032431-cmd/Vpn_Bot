from __future__ import annotations

from aiogram.types import CallbackQuery, InlineKeyboardMarkup


async def show_text(callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup | None = None) -> None:
    """Replace the callback's message with a text screen.

    The main menu is a photo message (welcome banner), and Telegram
    rejects turning a photo message into a text one via edit_text --
    delete-and-resend handles that case, edit_text is kept for a plain
    text message already in place.
    """
    message = callback.message
    if message.photo:
        try:
            await message.delete()
        except Exception:
            pass
        await message.answer(text, reply_markup=reply_markup)
    else:
        await message.edit_text(text, reply_markup=reply_markup)
