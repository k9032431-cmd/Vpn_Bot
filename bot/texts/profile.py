from __future__ import annotations

import html

from .premium_emoji import e
from .translations import LANGUAGE_LABELS, t


def profile_text(lang: str, user, panels_count: int) -> str:
    name = " ".join(filter(None, [user.first_name, user.last_name])) or "—"
    username = f"@{user.username}" if user.username else t(lang, "profile_no_username")
    return t(
        lang,
        "profile_text",
        icon=e("profile", "👤"),
        name=html.escape(name),
        username=html.escape(username),
        user_id=user.id,
        language=LANGUAGE_LABELS.get(lang, lang),
        panels_count=panels_count,
    )
