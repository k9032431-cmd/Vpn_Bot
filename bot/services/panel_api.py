from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlparse

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)


class PanelAPIError(Exception):
    """Raised when a panel login or API call fails.

    ``str(exc)`` is one of a small set of reason codes (see below) that the
    texts layer translates into a human message — never a raw technical
    string, so it's safe to show directly to the user.
    """


def normalize_panel_url(raw: str) -> str:
    url = raw.strip().rstrip("/")
    if not url.lower().startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


def is_valid_panel_url(value: str) -> bool:
    if not value or " " in value or "\t" in value:
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return bool(parsed.netloc)


def _connector() -> aiohttp.TCPConnector:
    # Self-hosted panels very commonly run on self-signed certificates.
    return aiohttp.TCPConnector(ssl=False)


async def _request_json(
    session: aiohttp.ClientSession, method: str, url: str, **kwargs
) -> tuple[int, object]:
    try:
        async with session.request(method, url, **kwargs) as resp:
            try:
                payload = await resp.json(content_type=None)
            except (json.JSONDecodeError, aiohttp.ContentTypeError):
                payload = None
            return resp.status, payload
    except (aiohttp.ClientError, TimeoutError) as exc:
        raise PanelAPIError("connect_failed") from exc


# --- Marzban / PasarGuard (API-compatible: PasarGuard is a Marzban fork) ---


@dataclass
class MarzbanFamilyStats:
    version: str
    total_users: int
    active: int
    disabled: int
    expired: int
    limited: int
    on_hold: int
    online_users: int
    incoming_bandwidth: int
    outgoing_bandwidth: int


async def marzban_login(url: str, username: str, password: str) -> str:
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        status, payload = await _request_json(
            session,
            "POST",
            f"{url}/api/admin/token",
            data={"username": username, "password": password, "grant_type": "password"},
        )
    if status == 401:
        raise PanelAPIError("wrong_credentials")
    if status != 200:
        raise PanelAPIError(f"http:{status}")
    token = (payload or {}).get("access_token") if isinstance(payload, dict) else None
    if not token:
        raise PanelAPIError("bad_response")
    return token


async def marzban_get_system_stats(url: str, token: str) -> MarzbanFamilyStats:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        status, payload = await _request_json(session, "GET", f"{url}/api/system", headers=headers)
    if status != 200 or not isinstance(payload, dict):
        raise PanelAPIError(f"http:{status}" if status != 200 else "bad_response")
    return MarzbanFamilyStats(
        version=str(payload.get("version", "?")),
        total_users=int(payload.get("total_user", 0) or 0),
        active=int(payload.get("users_active", 0) or 0),
        disabled=int(payload.get("users_disabled", 0) or 0),
        expired=int(payload.get("users_expired", 0) or 0),
        limited=int(payload.get("users_limited", 0) or 0),
        on_hold=int(payload.get("users_on_hold", 0) or 0),
        online_users=int(payload.get("online_users", 0) or 0),
        incoming_bandwidth=int(payload.get("incoming_bandwidth", 0) or 0),
        outgoing_bandwidth=int(payload.get("outgoing_bandwidth", 0) or 0),
    )


async def marzban_get_users(url: str, token: str, limit: int = 10) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        status, payload = await _request_json(
            session, "GET", f"{url}/api/users", headers=headers, params={"limit": limit}
        )
    if status != 200 or not isinstance(payload, dict):
        raise PanelAPIError(f"http:{status}" if status != 200 else "bad_response")
    users = payload.get("users", [])
    return users if isinstance(users, list) else []


# --- 3X-UI (cookie-based session, optional CSRF token on newer builds) ---


async def threexui_login(url: str, username: str, password: str) -> dict[str, str]:
    jar = aiohttp.CookieJar(unsafe=True)
    async with aiohttp.ClientSession(
        connector=_connector(), timeout=REQUEST_TIMEOUT, cookie_jar=jar
    ) as session:
        headers = {}
        # Newer 3X-UI builds require a CSRF token for POST /login; older
        # ones don't have this route at all — a failure here is fine,
        # we just proceed without the header.
        try:
            _, csrf_payload = await _request_json(session, "GET", f"{url}/csrf-token")
            if isinstance(csrf_payload, dict) and csrf_payload.get("obj"):
                headers["X-CSRF-Token"] = str(csrf_payload["obj"])
        except PanelAPIError:
            pass

        status, payload = await _request_json(
            session,
            "POST",
            f"{url}/login",
            data={"username": username, "password": password},
            headers=headers,
        )
        if status != 200 or not isinstance(payload, dict):
            raise PanelAPIError(f"http:{status}" if status != 200 else "bad_response")
        if not payload.get("success"):
            raise PanelAPIError("wrong_credentials")

        cookies = {c.key: c.value for c in jar}
    if not cookies:
        raise PanelAPIError("bad_response")
    return cookies


async def threexui_get_inbounds(url: str, cookies: dict[str, str]) -> list[dict]:
    async with aiohttp.ClientSession(
        connector=_connector(), timeout=REQUEST_TIMEOUT, cookies=cookies
    ) as session:
        status, payload = await _request_json(session, "GET", f"{url}/panel/api/inbounds/list")
    if status != 200 or not isinstance(payload, dict) or not payload.get("success"):
        raise PanelAPIError(f"http:{status}" if status != 200 else "bad_response")
    obj = payload.get("obj", [])
    return obj if isinstance(obj, list) else []


def count_3xui_clients(inbounds: list[dict]) -> int:
    total = 0
    for inbound in inbounds:
        settings_raw = inbound.get("settings")
        if not settings_raw:
            continue
        try:
            settings = json.loads(settings_raw)
        except (json.JSONDecodeError, TypeError):
            continue
        clients = settings.get("clients") if isinstance(settings, dict) else None
        if isinstance(clients, list):
            total += len(clients)
    return total
