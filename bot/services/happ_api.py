from __future__ import annotations

import asyncio
import json

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)

# Happ's own encryption service — module-level so it's easy to point at a
# fake server in tests without touching the request logic itself.
HAPP_ENCRYPT_URL = "https://crypto.happ.su/api-v2.php"


class HappAPIError(Exception):
    """str(exc) is one of a small set of reason codes — the texts layer
    translates these into a human message, so it's always safe to show."""


def _extract_link(payload: object) -> str | None:
    """Happ's own encryption API doesn't publish the exact shape of its
    response beyond "returns an encrypted link" — this checks every
    plausible key (and one level of nesting) so a server-side naming
    choice we didn't anticipate doesn't break the whole feature, and
    falls back to treating a plain-text body as the link itself."""
    if isinstance(payload, dict):
        for key in ("link", "url", "result", "data", "crypt_link", "encrypted", "crypt", "happ_link"):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        for value in payload.values():
            if isinstance(value, dict):
                nested = _extract_link(value)
                if nested:
                    return nested
        return None
    if isinstance(payload, str) and payload:
        return payload
    return None


def _looks_like_happ_link(link: str) -> bool:
    scheme = link.split("://", 1)[0].lower() if "://" in link else ""
    return scheme == "happ" or "crypt" in scheme


async def happ_encrypt_link(subscription_url: str) -> str:
    """Encrypts a subscription URL into Happ's own crypt5 link format via
    Happ's official encryption endpoint — not a local re-implementation.
    Happ's crypt5 format is RSA-4096 + ChaCha20-Poly1305 with per-release
    key material that only Happ's own service can produce a link the real
    app will actually accept, so this always goes through their API rather
    than trying to reproduce the crypto here."""
    try:
        async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT, trust_env=True) as session:
            async with session.post(HAPP_ENCRYPT_URL, json={"url": subscription_url}) as resp:
                raw = await resp.text()
                if resp.status >= 400:
                    raise HappAPIError("bad_response")
    except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError) as exc:
        raise HappAPIError("connect_failed") from exc

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = raw

    link = _extract_link(payload)
    if not link or not _looks_like_happ_link(link):
        raise HappAPIError("bad_response")
    return link
