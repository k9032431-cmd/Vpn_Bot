from __future__ import annotations

import html


def format_support_contact(raw: str) -> str:
    """Turns SUPPORT_CONTACT from .env into a clickable HTML link.

    Accepts a few common formats: a full URL, "@username", a bare
    username, or a numeric Telegram user ID (uses the tg://user?id=
    deep link, which opens that user's profile in Telegram clients).
    """
    raw = (raw or "").strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://", "tg://")):
        href = raw
        label = raw
    elif raw.startswith("@"):
        href = f"https://t.me/{raw[1:]}"
        label = raw
    elif raw.lstrip("-").isdigit():
        href = f"tg://user?id={raw}"
        label = raw
    else:
        href = f"https://t.me/{raw}"
        label = f"@{raw}"
    return f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
