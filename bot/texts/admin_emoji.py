from __future__ import annotations

import html

from .premium_emoji import EmojiSlot, current_id
from .premium_emoji import e as emoji_e
from .translations import t


def admin_emoji_sections_text(lang: str) -> str:
    return t(lang, "admin_emoji_sections", icon=emoji_e("warning", "⚙️"))


def admin_emoji_section_text(lang: str, section: str) -> str:
    return t(lang, "admin_emoji_section", icon=emoji_e("warning", "⚙️"), section=html.escape(section))


def _slot_status_text(lang: str, slot: EmojiSlot, overridden: bool) -> str:
    live = current_id(slot.key)
    if not live:
        return t(lang, "admin_emoji_status_empty", fallback=slot.fallback)
    key = "admin_emoji_status_override" if overridden else "admin_emoji_status_default"
    return t(lang, key, id=html.escape(live))


def admin_emoji_slot_text(lang: str, slot: EmojiSlot, overridden: bool) -> str:
    preview = f"{emoji_e(slot.key, slot.fallback)} <b>{html.escape(slot.label)}</b>"
    status = _slot_status_text(lang, slot, overridden)
    return t(lang, "admin_emoji_slot", preview=preview, status=status)


def admin_emoji_waiting_text(lang: str, slot: EmojiSlot) -> str:
    return t(
        lang, "admin_emoji_waiting",
        icon=emoji_e("warning", "⏳"), label=html.escape(slot.label), fallback=slot.fallback,
    )


def admin_emoji_invalid_text(lang: str) -> str:
    return t(lang, "admin_emoji_invalid", icon=emoji_e("error", "❌"))


def admin_emoji_set_ok_text(lang: str, slot: EmojiSlot) -> str:
    preview = emoji_e(slot.key, slot.fallback)
    return t(lang, "admin_emoji_set_ok", icon=emoji_e("success", "✅"), preview=preview, label=html.escape(slot.label))
