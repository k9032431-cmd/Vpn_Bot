from __future__ import annotations

import json
from dataclasses import dataclass, field

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)

# UpCloud's REST API lives at one fixed address for every account — unlike
# Marzban/3X-UI there is no per-user "panel URL" to store. Kept as a
# parameter (not hardcoded into every call) purely so fake-server tests can
# point it elsewhere.
UPCLOUD_API_BASE = "https://api.upcloud.com/1.3"


class UpCloudAPIError(Exception):
    """Raised when an UpCloud API call fails.

    ``str(exc)`` is one of a small set of reason codes, or ``detail:<msg>``
    carrying UpCloud's own error message — the texts layer translates these
    into a human message, so it's always safe to show directly.
    """


@dataclass
class AccountInfo:
    username: str
    credits: float
    currency: str = "EUR"


@dataclass
class ZoneInfo:
    id: str
    description: str


@dataclass
class PlanInfo:
    name: str
    core_number: int
    memory_amount: int
    storage_size: int
    price_per_hour: float | None = None


@dataclass
class TemplateInfo:
    uuid: str
    title: str
    os: str = ""


@dataclass
class IPAddressInfo:
    address: str
    access: str  # "public" | "private" | "utility"
    family: str  # "IPv4" | "IPv6"


@dataclass
class ServerInfo:
    uuid: str
    title: str
    hostname: str
    state: str
    zone: str
    plan: str
    core_number: int = 0
    memory_amount: int = 0
    ip_addresses: list[IPAddressInfo] = field(default_factory=list)
    password: str | None = None  # only set right after creation


def _connector() -> aiohttp.TCPConnector:
    return aiohttp.TCPConnector(ssl=True)


async def _request(
    method: str,
    path: str,
    username: str,
    password: str,
    *,
    base_url: str | None = None,
    json_body: dict | None = None,
    params: dict | None = None,
) -> object:
    url = f"{(base_url or UPCLOUD_API_BASE).rstrip('/')}{path}"
    auth = aiohttp.BasicAuth(username, password)
    try:
        async with aiohttp.ClientSession(
            connector=_connector(), timeout=REQUEST_TIMEOUT, auth=auth
        ) as session:
            async with session.request(method, url, json=json_body, params=params) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    payload = None
                if resp.status == 401:
                    raise UpCloudAPIError("wrong_credentials")
                if resp.status >= 400:
                    detail = _extract_detail(payload)
                    if detail:
                        raise UpCloudAPIError(f"detail:{detail}")
                    raise UpCloudAPIError("bad_response")
                return payload
    except (aiohttp.ClientError, TimeoutError) as exc:
        raise UpCloudAPIError("connect_failed") from exc


def _extract_detail(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if isinstance(error, dict):
        msg = error.get("error_message")
        if isinstance(msg, str) and msg:
            return msg
    return None


# --- Account ---


async def upcloud_login(username: str, password: str, *, base_url: str | None = None) -> AccountInfo:
    """Validates credentials and returns the account snapshot, same as
    Marzban/3X-UI login — a wrong sub-account username/password raises
    UpCloudAPIError("wrong_credentials")."""
    return await upcloud_get_account(username, password, base_url=base_url)


async def upcloud_get_account(
    username: str, password: str, *, base_url: str | None = None
) -> AccountInfo:
    payload = await _request("GET", "/account", username, password, base_url=base_url)
    account = payload.get("account", {}) if isinstance(payload, dict) else {}
    return AccountInfo(
        username=account.get("username", username),
        credits=float(account.get("credits", 0) or 0),
    )


# --- Servers ---


def _parse_ip(raw: dict) -> IPAddressInfo:
    return IPAddressInfo(
        address=raw.get("address", ""),
        access=raw.get("access", ""),
        family=raw.get("family", ""),
    )


def _parse_server_summary(raw: dict) -> ServerInfo:
    return ServerInfo(
        uuid=raw.get("uuid", ""),
        title=raw.get("title", ""),
        hostname=raw.get("hostname", ""),
        state=raw.get("state", ""),
        zone=raw.get("zone", ""),
        plan=raw.get("plan", ""),
        core_number=int(raw.get("core_number", 0) or 0),
        memory_amount=int(raw.get("memory_amount", 0) or 0),
    )


def _parse_server_detail(raw: dict) -> ServerInfo:
    server = _parse_server_summary(raw)
    ip_addresses = raw.get("ip_addresses", {})
    entries = ip_addresses.get("ip_address", []) if isinstance(ip_addresses, dict) else []
    server.ip_addresses = [_parse_ip(item) for item in entries if isinstance(item, dict)]
    return server


async def upcloud_list_servers(
    username: str, password: str, *, base_url: str | None = None
) -> list[ServerInfo]:
    payload = await _request("GET", "/server", username, password, base_url=base_url)
    servers = payload.get("servers", {}) if isinstance(payload, dict) else {}
    entries = servers.get("server", []) if isinstance(servers, dict) else []
    return [_parse_server_summary(item) for item in entries if isinstance(item, dict)]


async def upcloud_get_server(
    username: str, password: str, server_uuid: str, *, base_url: str | None = None
) -> ServerInfo:
    payload = await _request(
        "GET", f"/server/{server_uuid}", username, password, base_url=base_url
    )
    server = payload.get("server", {}) if isinstance(payload, dict) else {}
    return _parse_server_detail(server)


async def upcloud_create_server(
    username: str,
    password: str,
    *,
    zone: str,
    hostname: str,
    title: str,
    plan: str,
    template_uuid: str,
    storage_size: int = 25,
    ssh_public_key: str | None = None,
    base_url: str | None = None,
) -> ServerInfo:
    """Creates a server, cloning the given storage template. Uses
    ``password_delivery: none`` + a generated root password returned in the
    response when no SSH key is given (fetched separately by the caller and
    shown once), matching UpCloud's own "create server" defaults."""
    login_user: dict = {"create_password": "yes" if not ssh_public_key else "no"}
    if ssh_public_key:
        login_user["ssh_keys"] = {"ssh_key": [ssh_public_key]}

    body = {
        "server": {
            "zone": zone,
            "title": title,
            "hostname": hostname,
            "plan": plan,
            "password_delivery": "none",
            "login_user": login_user,
            "storage_devices": {
                "storage_device": [
                    {
                        "action": "clone",
                        "storage": template_uuid,
                        "title": f"{title}-disk1",
                        "size": storage_size,
                        "tier": "maxiops",
                    }
                ]
            },
        }
    }
    payload = await _request("POST", "/server", username, password, base_url=base_url, json_body=body)
    server = payload.get("server", {}) if isinstance(payload, dict) else {}
    info = _parse_server_detail(server)
    password_field = server.get("password")
    if isinstance(password_field, str) and password_field:
        info.password = password_field
    return info


async def upcloud_modify_server(
    username: str,
    password: str,
    server_uuid: str,
    *,
    title: str | None = None,
    plan: str | None = None,
    base_url: str | None = None,
) -> ServerInfo:
    fields: dict = {}
    if title is not None:
        fields["title"] = title
    if plan is not None:
        fields["plan"] = plan
    payload = await _request(
        "PUT",
        f"/server/{server_uuid}",
        username,
        password,
        base_url=base_url,
        json_body={"server": fields},
    )
    server = payload.get("server", {}) if isinstance(payload, dict) else {}
    return _parse_server_detail(server)


async def upcloud_start_server(
    username: str, password: str, server_uuid: str, *, base_url: str | None = None
) -> ServerInfo:
    payload = await _request(
        "POST", f"/server/{server_uuid}/start", username, password, base_url=base_url
    )
    server = payload.get("server", {}) if isinstance(payload, dict) else {}
    return _parse_server_detail(server)


async def upcloud_stop_server(
    username: str, password: str, server_uuid: str, *, base_url: str | None = None
) -> ServerInfo:
    payload = await _request(
        "POST",
        f"/server/{server_uuid}/stop",
        username,
        password,
        base_url=base_url,
        json_body={"stop_server": {"stop_type": "hard"}},
    )
    server = payload.get("server", {}) if isinstance(payload, dict) else {}
    return _parse_server_detail(server)


async def upcloud_restart_server(
    username: str, password: str, server_uuid: str, *, base_url: str | None = None
) -> ServerInfo:
    payload = await _request(
        "POST",
        f"/server/{server_uuid}/restart",
        username,
        password,
        base_url=base_url,
        json_body={"restart_server": {"stop_type": "hard"}},
    )
    server = payload.get("server", {}) if isinstance(payload, dict) else {}
    return _parse_server_detail(server)


async def upcloud_delete_server(
    username: str,
    password: str,
    server_uuid: str,
    *,
    delete_storages: bool = True,
    base_url: str | None = None,
) -> None:
    params = {"storages": "1"} if delete_storages else None
    await _request(
        "DELETE", f"/server/{server_uuid}", username, password, base_url=base_url, params=params
    )


# --- Catalog: zones, plans, templates ---


async def upcloud_list_zones(
    username: str, password: str, *, base_url: str | None = None
) -> list[ZoneInfo]:
    payload = await _request("GET", "/zone", username, password, base_url=base_url)
    zones = payload.get("zones", {}) if isinstance(payload, dict) else {}
    entries = zones.get("zone", []) if isinstance(zones, dict) else []
    return [
        ZoneInfo(id=item.get("id", ""), description=item.get("description", ""))
        for item in entries
        if isinstance(item, dict)
    ]


async def upcloud_list_plans(
    username: str, password: str, *, base_url: str | None = None
) -> list[PlanInfo]:
    payload = await _request("GET", "/plan", username, password, base_url=base_url)
    plans = payload.get("plans", {}) if isinstance(payload, dict) else {}
    entries = plans.get("plan", []) if isinstance(plans, dict) else []
    return [
        PlanInfo(
            name=item.get("name", ""),
            core_number=int(item.get("core_number", 0) or 0),
            memory_amount=int(item.get("memory_amount", 0) or 0),
            storage_size=int(item.get("storage_size", 0) or 0),
        )
        for item in entries
        if isinstance(item, dict)
    ]


async def upcloud_list_templates(
    username: str, password: str, *, base_url: str | None = None
) -> list[TemplateInfo]:
    payload = await _request("GET", "/storage/template", username, password, base_url=base_url)
    storages = payload.get("storages", {}) if isinstance(payload, dict) else {}
    entries = storages.get("storage", []) if isinstance(storages, dict) else []
    return [
        TemplateInfo(uuid=item.get("uuid", ""), title=item.get("title", ""), os=item.get("os", ""))
        for item in entries
        if isinstance(item, dict)
    ]
