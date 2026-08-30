from __future__ import annotations

import json
from dataclasses import dataclass
from urllib.parse import urlparse, urlsplit, urlunsplit

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=15)


class PanelAPIError(Exception):
    """Raised when a panel login or API call fails.

    ``str(exc)`` is one of a small set of reason codes, or ``detail:<msg>``
    carrying the panel's own error message — the texts layer translates
    these into a human message, so it's always safe to show directly.
    """


def normalize_panel_url(raw: str) -> str:
    url = raw.strip()
    if not url.lower().startswith(("http://", "https://")):
        url = f"https://{url}"
    # Users commonly paste the browser URL of Marzban/PasarGuard's web
    # dashboard (e.g. https://host/dashboard/#/ or .../dashboard/#/login)
    # rather than the bare panel URL the API actually lives at — strip
    # that part off, keeping any reverse-proxy subpath before it.
    split = urlsplit(url)
    path = split.path
    idx = path.lower().find("/dashboard")
    if idx != -1:
        path = path[:idx]
    path = path.rstrip("/")
    return urlunsplit((split.scheme, split.netloc, path, "", ""))


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


def _extract_detail(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    detail = payload.get("detail")
    if isinstance(detail, str) and detail:
        return detail
    if isinstance(detail, list) and detail:
        parts = [item.get("msg") for item in detail if isinstance(item, dict) and item.get("msg")]
        if parts:
            return "; ".join(str(p) for p in parts)
    return None


async def _marzban_call(
    session: aiohttp.ClientSession, method: str, url: str, **kwargs
) -> object:
    status, payload = await _request_json(session, method, url, **kwargs)
    if status == 401:
        raise PanelAPIError("wrong_credentials")
    if status >= 400:
        detail = _extract_detail(payload)
        if detail:
            raise PanelAPIError(f"detail:{detail}")
        raise PanelAPIError(f"http:{status}")
    return payload


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
        payload = await _marzban_call(
            session,
            "POST",
            f"{url}/api/admin/token",
            data={"username": username, "password": password, "grant_type": "password"},
        )
    token = payload.get("access_token") if isinstance(payload, dict) else None
    if not token:
        raise PanelAPIError("bad_response")
    return token


async def marzban_get_system_stats(url: str, token: str) -> MarzbanFamilyStats:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/system", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
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


@dataclass
class UsersPage:
    users: list[dict]
    total: int


async def marzban_get_users(url: str, token: str, offset: int = 0, limit: int = 10) -> UsersPage:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(
            session, "GET", f"{url}/api/users", headers=headers, params={"offset": offset, "limit": limit}
        )
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    users = payload.get("users", [])
    users = users if isinstance(users, list) else []
    total = payload.get("total", offset + len(users))
    try:
        total = int(total)
    except (TypeError, ValueError):
        total = offset + len(users)
    return UsersPage(users=users, total=total)


async def marzban_get_user(url: str, token: str, username: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/user/{username}", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return payload


async def marzban_get_inbounds(url: str, token: str) -> dict[str, list[str]]:
    """Returns {protocol: [inbound_tag, ...]} for every protocol configured
    on the panel — used to give a newly created user access to everything
    the panel actually has, without the caller needing to know the tags."""
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/inbounds", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    result: dict[str, list[str]] = {}
    for protocol, inbounds in payload.items():
        if not isinstance(inbounds, list):
            continue
        tags = [ib.get("tag") for ib in inbounds if isinstance(ib, dict) and ib.get("tag")]
        if tags:
            result[protocol] = tags
    return result


async def marzban_create_user(
    url: str,
    token: str,
    username: str,
    proxies: dict[str, dict],
    inbounds: dict[str, list[str]],
    data_limit: int | None,
    expire: int | None,
) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "username": username,
        "proxies": proxies,
        "inbounds": inbounds,
        "data_limit": data_limit,
        "expire": expire,
    }
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "POST", f"{url}/api/user", headers=headers, json=body)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return payload


async def marzban_modify_user(url: str, token: str, username: str, **fields) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(
            session, "PUT", f"{url}/api/user/{username}", headers=headers, json=fields
        )
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return payload


async def marzban_delete_user(url: str, token: str, username: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "DELETE", f"{url}/api/user/{username}", headers=headers)


async def marzban_reset_user_usage(url: str, token: str, username: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(
            session, "POST", f"{url}/api/user/{username}/reset", headers=headers
        )
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return payload


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


def list_3xui_clients(inbounds: list[dict]) -> list[str]:
    """Flattens every inbound's `settings.clients` (raw Xray config JSON,
    stable across 3x-ui forks) into a list of display labels."""
    labels: list[str] = []
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
            for client in clients:
                labels.append(str(client.get("email") or client.get("id") or "?"))
    return labels


def count_3xui_clients(inbounds: list[dict]) -> int:
    return len(list_3xui_clients(inbounds))
