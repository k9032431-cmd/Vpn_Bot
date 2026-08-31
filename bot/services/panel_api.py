from __future__ import annotations

import json
import secrets
import time
import uuid
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


@dataclass
class NodeInfo:
    id: int
    name: str
    address: str
    port: int
    api_port: int
    usage_coefficient: float
    xray_version: str | None
    status: str
    message: str | None


def _parse_node(data: dict) -> NodeInfo:
    return NodeInfo(
        id=int(data.get("id", 0) or 0),
        name=str(data.get("name", "?")),
        address=str(data.get("address", "?")),
        port=int(data.get("port", 0) or 0),
        api_port=int(data.get("api_port", 0) or 0),
        usage_coefficient=float(data.get("usage_coefficient", 1) or 1),
        xray_version=data.get("xray_version"),
        status=str(data.get("status", "?")),
        message=data.get("message"),
    )


async def marzban_get_nodes(url: str, token: str) -> list[NodeInfo]:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/nodes", headers=headers)
    if not isinstance(payload, list):
        raise PanelAPIError("bad_response")
    return [_parse_node(n) for n in payload if isinstance(n, dict)]


async def marzban_get_node(url: str, token: str, node_id: int) -> NodeInfo:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/node/{node_id}", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return _parse_node(payload)


async def marzban_add_node(
    url: str, token: str, name: str, address: str, port: int, api_port: int
) -> NodeInfo:
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "name": name,
        "address": address,
        "port": port,
        "api_port": api_port,
        "usage_coefficient": 1,
        "add_as_new_host": True,
    }
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "POST", f"{url}/api/node", headers=headers, json=body)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return _parse_node(payload)


async def marzban_delete_node(url: str, token: str, node_id: int) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "DELETE", f"{url}/api/node/{node_id}", headers=headers)


async def marzban_reconnect_node(url: str, token: str, node_id: int) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "POST", f"{url}/api/node/{node_id}/reconnect", headers=headers)


# --- Xray core config (Marzban / PasarGuard) ---


@dataclass
class CoreInfo:
    version: str
    started: bool


async def marzban_get_core_info(url: str, token: str) -> CoreInfo:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/core", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return CoreInfo(version=str(payload.get("version", "?")), started=bool(payload.get("started")))


async def marzban_get_core_config(url: str, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/core/config", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return payload


async def marzban_set_core_config(url: str, token: str, config: dict) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "PUT", f"{url}/api/core/config", headers=headers, json=config)


async def marzban_restart_core(url: str, token: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "POST", f"{url}/api/core/restart", headers=headers)


class CoreConfigError(Exception):
    """Raised by parse_core_config_input for a config that isn't usable —
    str(exc) is a short reason code the texts layer turns into a message."""


def parse_core_config_input(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise CoreConfigError("not_json") from exc
    if not isinstance(data, dict):
        raise CoreConfigError("not_object")
    if "inbounds" not in data:
        raise CoreConfigError("missing_inbounds")
    return data


# --- Sub-admin management (Marzban / PasarGuard) ---


@dataclass
class AdminInfo:
    username: str
    is_sudo: bool
    telegram_id: int | None


def _parse_admin(data: dict) -> AdminInfo:
    return AdminInfo(
        username=str(data.get("username", "?")),
        is_sudo=bool(data.get("is_sudo")),
        telegram_id=data.get("telegram_id"),
    )


async def marzban_get_admins(url: str, token: str) -> list[AdminInfo]:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/admins", headers=headers)
    if not isinstance(payload, list):
        raise PanelAPIError("bad_response")
    return [_parse_admin(a) for a in payload if isinstance(a, dict)]


async def marzban_create_admin(url: str, token: str, username: str, password: str, is_sudo: bool) -> AdminInfo:
    headers = {"Authorization": f"Bearer {token}"}
    body = {"username": username, "password": password, "is_sudo": is_sudo}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "POST", f"{url}/api/admin", headers=headers, json=body)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return _parse_admin(payload)


async def marzban_modify_admin(url: str, token: str, username: str, **fields) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "PUT", f"{url}/api/admin/{username}", headers=headers, json=fields)


async def marzban_delete_admin(url: str, token: str, username: str) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "DELETE", f"{url}/api/admin/{username}", headers=headers)


# --- Subscription host settings (Marzban / PasarGuard) ---
#
# Host entries are kept as raw dicts rather than a dataclass: Marzban's
# HostConfig has many optional advanced fields (fragment_setting,
# noise_setting, mux_enable, ...) that this bot doesn't expose editing
# for, and PUT /api/hosts replaces the *entire* structure — round-tripping
# through a lossy typed model would silently drop whatever the panel
# admin already configured for those fields.


async def marzban_get_hosts(url: str, token: str) -> dict[str, list[dict]]:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        payload = await _marzban_call(session, "GET", f"{url}/api/hosts", headers=headers)
    if not isinstance(payload, dict):
        raise PanelAPIError("bad_response")
    return {
        str(tag): [h for h in hosts if isinstance(h, dict)]
        for tag, hosts in payload.items()
        if isinstance(hosts, list)
    }


async def marzban_set_hosts(url: str, token: str, hosts: dict[str, list[dict]]) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
        await _marzban_call(session, "PUT", f"{url}/api/hosts", headers=headers, json=hosts)


def new_host_entry(remark: str, address: str, port: int | None) -> dict:
    return {
        "remark": remark,
        "address": address,
        "port": port,
        "sni": None,
        "host": None,
        "path": None,
        "security": "inbound_default",
        "alpn": None,
        "fingerprint": None,
        "allowinsecure": False,
        "is_disabled": False,
        "mux_enable": False,
        "fragment_setting": None,
        "noise_setting": None,
        "random_user_agent": False,
        "use_sni_as_host": False,
    }


class HostFieldsError(Exception):
    """str(exc) is a short reason code the texts layer turns into a message."""


def parse_host_fields_input(raw: str) -> dict:
    """Parses the compact "remark|address|port|sni|host|path" editor line.

    An empty segment leaves that field untouched; a lone "-" explicitly
    clears an optional field (port/sni/host/path) to null."""
    parts = raw.split("|")
    if len(parts) != 6:
        raise HostFieldsError("wrong_field_count")

    remark, address, port_raw, sni, host, path = (p.strip() for p in parts)
    updates: dict = {}
    if remark:
        updates["remark"] = remark
    if address:
        updates["address"] = address
    if port_raw:
        if port_raw == "-":
            updates["port"] = None
        else:
            try:
                port = int(port_raw)
            except ValueError as exc:
                raise HostFieldsError("bad_port") from exc
            if not (0 < port < 65536):
                raise HostFieldsError("bad_port")
            updates["port"] = port
    if sni:
        updates["sni"] = None if sni == "-" else sni
    if host:
        updates["host"] = None if host == "-" else host
    if path:
        updates["path"] = None if path == "-" else path
    return updates


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


def inbound_client_count(inbound: dict) -> int:
    return len(list_3xui_clients([inbound]))


async def threexui_update_inbound(url: str, cookies: dict[str, str], inbound: dict) -> None:
    # 3X-UI's update endpoint expects the whole inbound object back (like
    # Marzban's /api/hosts) — "clientStats" is a response-only computed
    # field the list endpoint adds, so it's dropped before resubmitting.
    body = {k: v for k, v in inbound.items() if k != "clientStats"}
    async with aiohttp.ClientSession(
        connector=_connector(), timeout=REQUEST_TIMEOUT, cookies=cookies
    ) as session:
        status, payload = await _request_json(
            session, "POST", f"{url}/panel/api/inbounds/update/{inbound['id']}", json=body
        )
    if status != 200 or not isinstance(payload, dict) or not payload.get("success"):
        raise PanelAPIError(f"http:{status}" if status != 200 else "bad_response")


async def threexui_delete_inbound(url: str, cookies: dict[str, str], inbound_id: int) -> None:
    async with aiohttp.ClientSession(
        connector=_connector(), timeout=REQUEST_TIMEOUT, cookies=cookies
    ) as session:
        status, payload = await _request_json(session, "POST", f"{url}/panel/api/inbounds/del/{inbound_id}")
    if status != 200 or not isinstance(payload, dict) or not payload.get("success"):
        raise PanelAPIError(f"http:{status}" if status != 200 else "bad_response")


class InboundFieldsError(Exception):
    """str(exc) is a short reason code the texts layer turns into a message."""


def parse_inbound_fields_input(raw: str) -> dict:
    """Parses the compact "remark|port" editor line — an empty segment
    leaves that field untouched. Protocol/TLS/Reality settings aren't
    editable this way; those are best configured in the panel itself."""
    parts = raw.split("|")
    if len(parts) != 2:
        raise InboundFieldsError("wrong_format")

    remark, port_raw = (p.strip() for p in parts)
    updates: dict = {}
    if remark:
        updates["remark"] = remark
    if port_raw:
        try:
            port = int(port_raw)
        except ValueError as exc:
            raise InboundFieldsError("bad_port") from exc
        if not (0 < port < 65536):
            raise InboundFieldsError("bad_port")
        updates["port"] = port
    return updates


# --- 3X-UI client management ---
#
# 3x-ui forks vary on their dedicated addClient/updateClient/delClient
# endpoints, so instead all client CRUD here goes through the same
# already-verified "resend the whole inbound" path as inbound editing:
# parse settings.clients out of the inbound's settings JSON, mutate the
# list locally, re-serialize, and call threexui_update_inbound. This is
# more portable than guessing a per-fork client-endpoint URL/payload shape.


def _inbound_settings(inbound: dict) -> dict:
    try:
        settings = json.loads(inbound.get("settings") or "{}")
    except (json.JSONDecodeError, TypeError):
        settings = {}
    return settings if isinstance(settings, dict) else {}


def get_inbound_clients(inbound: dict) -> list[dict]:
    clients = _inbound_settings(inbound).get("clients")
    return clients if isinstance(clients, list) else []


def client_label_id(client: dict) -> str:
    return str(client.get("id") or client.get("password") or client.get("email") or "?")


def client_stat_for(inbound: dict, client: dict) -> dict | None:
    stats = inbound.get("clientStats")
    if not isinstance(stats, list):
        return None
    email = client.get("email")
    return next((s for s in stats if isinstance(s, dict) and s.get("email") == email), None)


def with_inbound_clients(inbound: dict, clients: list[dict]) -> dict:
    """Returns a copy of `inbound` with its settings.clients replaced —
    the result is what should be passed to threexui_update_inbound."""
    settings = dict(_inbound_settings(inbound))
    settings["clients"] = clients
    new_inbound = dict(inbound)
    new_inbound["settings"] = json.dumps(settings)
    return new_inbound


def new_3xui_client(protocol: str, email: str, data_limit_gb: float | None, expire_days: int | None) -> dict:
    total_gb = int(data_limit_gb * 1024**3) if data_limit_gb else 0
    expiry_time = int((time.time() + expire_days * 86400) * 1000) if expire_days else 0
    client: dict = {
        "email": email,
        "limitIp": 0,
        "totalGB": total_gb,
        "expiryTime": expiry_time,
        "enable": True,
        "tgId": "",
        "subId": secrets.token_hex(8),
        "reset": 0,
    }
    if protocol in ("trojan", "shadowsocks"):
        client["password"] = secrets.token_urlsafe(12)
        if protocol == "shadowsocks":
            client["method"] = ""
    else:
        # vless, vmess, and any unrecognized protocol fall back to the
        # id-based client shape, which covers the two most common cases.
        client["id"] = str(uuid.uuid4())
        if protocol == "vless":
            client["flow"] = ""
    return client


class ClientFieldsError(Exception):
    """str(exc) is a short reason code the texts layer turns into a message."""


def parse_client_limits_input(raw: str) -> tuple[int, int]:
    """Parses the "GB|дней" line into (totalGB in bytes, expiryTime in ms).
    "0" for either segment means unlimited/never — same convention as the
    Marzban user create/edit flow."""
    parts = raw.split("|")
    if len(parts) != 2:
        raise ClientFieldsError("wrong_format")
    gb_raw, days_raw = (p.strip() for p in parts)
    try:
        gb = float(gb_raw.replace(",", "."))
        days = int(days_raw)
    except ValueError as exc:
        raise ClientFieldsError("not_numbers") from exc
    if gb < 0 or days < 0:
        raise ClientFieldsError("not_numbers")
    total_gb = int(gb * 1024**3) if gb else 0
    expiry_time = int((time.time() + days * 86400) * 1000) if days else 0
    return total_gb, expiry_time
