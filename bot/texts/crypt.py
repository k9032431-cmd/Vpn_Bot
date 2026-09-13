from __future__ import annotations

import html

from .premium_emoji import e
from .translations import t

_CRYPT_ERR_KEYS = {
    "connect_failed": "crypt_err_connect",
    "bad_response": "crypt_err_bad_response",
}


def choose_action_text(lang: str) -> str:
    return t(lang, "crypt_choose_action", icon=e("crypt", "🔐"))


def decrypt_soon_text(lang: str) -> str:
    return t(lang, "crypt_decrypt_soon")


def choose_vpn_text(lang: str) -> str:
    return t(lang, "crypt_choose_vpn")


def cancelled_text(lang: str) -> str:
    return t(lang, "crypt_cancelled")


def waiting_url_text(lang: str) -> str:
    return t(lang, "crypt_waiting_url")


def invalid_url_text(lang: str) -> str:
    return t(lang, "crypt_invalid_url")


def result_text(lang: str, link: str) -> str:
    return t(lang, "crypt_result", icon=e("success", "✅"), link=html.escape(link))


def error_text(lang: str, reason: str) -> str:
    key = _CRYPT_ERR_KEYS.get(reason, "crypt_err_bad_response")
    return t(lang, "crypt_error", icon=e("error", "❌"), reason=t(lang, key))
