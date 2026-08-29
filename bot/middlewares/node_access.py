from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.config import config
from bot.texts.node import access_denied_text


class NodeAccessMiddleware(BaseMiddleware):
    """Gates the entire Node router to employees only.

    Registered on node.router itself, so it covers every step of the
    flow (menu, IP/SSH/cert prompts, confirmation, install) — not just
    the entry point — which matters if someone's access is revoked
    mid-conversation.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None and config.is_node_authorized(user.id):
            return await handler(event, data)

        lang = data.get("lang", "ru")
        text = access_denied_text(lang, user.id if user else 0)
        if isinstance(event, CallbackQuery):
            if event.message is not None:
                try:
                    await event.message.edit_text(text)
                except Exception:
                    pass
            await event.answer()
        elif isinstance(event, Message):
            await event.answer(text)
        return None
