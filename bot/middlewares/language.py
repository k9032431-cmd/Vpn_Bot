from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.services.user_prefs import user_prefs
from bot.texts.translations import resolve_language


class LanguageMiddleware(BaseMiddleware):
    """Resolves the current user's interface language and injects it into
    every handler as the ``lang`` parameter.

    Priority: an explicit choice saved via the Language menu (persisted on
    disk, so it survives restarts) beats Telegram's client-reported
    language_code, which is used only as a first-time guess and is never
    written back to storage on its own.
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None:
            lang = await user_prefs.get_language(user.id)
            if lang is None:
                lang = resolve_language(user.language_code)
        else:
            lang = resolve_language(None)
        data["lang"] = lang
        return await handler(event, data)
