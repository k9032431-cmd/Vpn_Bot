from __future__ import annotations

import html
from urllib.parse import quote


def build_sos_chat_url(raw: str, greeting: str) -> str | None:
    """Builds a link that opens a chat with the admin, pre-filled with a
    greeting, for the SOS button.

    Telegram only supports pre-filling the composer via the ``?text=``
    query param on a ``t.me/<username>`` link — a numeric user ID has no
    such option, so that case falls back to a plain tg://user deep link
    (opens the profile, without the pre-filled text).
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    encoded_text = quote(greeting, safe="")
    if raw.startswith(("http://", "https://", "tg://")):
        separator = "&" if "?" in raw else "?"
        return f"{raw}{separator}text={encoded_text}"
    if raw.startswith("@"):
        return f"https://t.me/{raw[1:]}?text={encoded_text}"
    if raw.lstrip("-").isdigit():
        return f"tg://user?id={raw}"
    return f"https://t.me/{raw}?text={encoded_text}"


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
