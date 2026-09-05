from __future__ import annotations

from bot.config import config

from .premium_emoji import e
from .support import format_support_contact
from .translations import t

_SECTION_ICON = {
    "cloud_account": ("cloud_account", "👤"),
    "crypt": ("crypt", "🔐"),
    "info": ("info", "ℹ️"),
}


def welcome_text(lang: str) -> str:
    return t(lang, "welcome", icon=e("welcome", "👋"))


def section_text(lang: str, section: str) -> str | None:
    if section == "sos":
        return sos_text(lang)
    icon_info = _SECTION_ICON.get(section)
    if icon_info is None:
        return None
    key, fallback = icon_info
    return t(lang, f"section_{section}", icon=e(key, fallback))


def sos_text(lang: str) -> str:
    icon = e("sos", "🆘")
    contact = format_support_contact(config.support_contact)
    if contact:
        return t(lang, "section_sos_contact", icon=icon, contact=contact)
    return t(lang, "section_sos_empty", icon=icon)


def language_prompt_text(lang: str) -> str:
    return t(lang, "language_prompt", icon=e("language", "🌐"))


def language_saved_text(lang: str) -> str:
    return t(lang, "language_saved")
