from __future__ import annotations

import asyncio
import secrets
from dataclasses import dataclass, field

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)

HETZNER_API_BASE = "https://api.hetzner.cloud/v1"

POLL_INTERVAL = 3
POLL_TIMEOUT = 240

# A small, curated shortlist rather than the full catalog (Hetzner has 20+
# server types and dozens of images) — same reasoning as Azure's curated
# size/image lists: showing everything would just be unusable in a chat UI.
CURATED_SERVER_TYPES = ["cx22", "cx32", "cx42", "cpx22", "cpx32", "cpx42"]
CURATED_IMAGES = ["ubuntu-24.04", "ubuntu-22.04", "debian-12"]


class HetznerAPIError(Exception):
    """str(exc) is one of a small set of reason codes ('wrong_credentials',
    'connect_failed', 'bad_response', 'not_found', 'timeout'), or
    'detail:<msg>' carrying Hetzner's own error message — the texts layer
    translates these into a human message, so it's always safe to show
    directly."""


@dataclass
class HetznerCredentials:
    token: str
    api_base: str = HETZNER_API_BASE


@dataclass
class AccountInfo:
    server_count: int


@dataclass
class LocationInfo:
    name: str
    description: str
    country: str  # ISO 3166-1 alpha-2, straight from the API — no guessing needed


@dataclass
class ServerTypeInfo:
    name: str
    cores: int
    memory_gb: float
    disk_gb: int
    price_hourly: float | None = None
    locations: list[str] = field(default_factory=list)  # where this type is actually sold, from its own prices[]


@dataclass
class ImageInfo:
    key: str  # the image's name -- see hetzner_list_available_images for why
    name: str
    description: str


@dataclass
class ServerInfo:
    id: int
    name: str
    status: str  # "running" | "off" | "starting" | "stopping" | "rebuilding" | ...
    server_type: str
    location: str
    ipv4: str | None = None
    ipv6: str | None = None
    root_password: str | None = None  # only set right after creation


@dataclass
class FloatingIPInfo:
    id: int
    ip: str
    ip_type: str  # "ipv4" | "ipv6"
    server_id: int | None = None
    location: str = ""


@dataclass
class PrimaryIPInfo:
    id: int
    ip: str
    ip_type: str  # "ipv4" | "ipv6"
    location: str
    server_id: int | None = None


def _connector() -> aiohttp.TCPConnector:
    return aiohttp.TCPConnector(ssl=True)


def _extract_detail(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    error = payload.get("error")
    if isinstance(error, dict):
        msg = error.get("message")
        if isinstance(msg, str) and msg:
            return msg
    return None


async def _request(
    creds: HetznerCredentials, method: str, path: str, *, json_body: dict | None = None, params: dict | None = None,
) -> tuple[int, object]:
    url = f"{creds.api_base.rstrip('/')}{path}"
    headers = {"Authorization": f"Bearer {creds.token}"}
    try:
        async with aiohttp.ClientSession(
            connector=_connector(), timeout=REQUEST_TIMEOUT, headers=headers
        ) as session:
            async with session.request(method, url, json=json_body, params=params) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError):
                    payload = None
                if resp.status == 401:
                    raise HetznerAPIError("wrong_credentials")
                if resp.status == 404:
                    return resp.status, payload
                if resp.status >= 400:
                    detail = _extract_detail(payload)
                    raise HetznerAPIError(f"detail:{detail}" if detail else "bad_response")
                return resp.status, payload
    except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError) as exc:
        raise HetznerAPIError("connect_failed") from exc


async def _poll_action(creds: HetznerCredentials, action_id: int) -> None:
    """Hetzner actions (create/power ops/rebuild/resize/floating-IP assign)
    are asynchronous — the POST response is just an "action" resource
    reflecting the *desired* outcome, not the actual one yet. Polls the
    action's own status until it's a terminal value."""
    elapsed = 0
    while True:
        _, payload = await _request(creds, "GET", f"/actions/{action_id}")
        action = (payload or {}).get("action") or {}
        status = action.get("status")
        if status == "success":
            return
        if status == "error":
            message = (action.get("error") or {}).get("message") or "action failed"
            raise HetznerAPIError(f"detail:{message}")
        if elapsed >= POLL_TIMEOUT:
            raise HetznerAPIError("timeout")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL


async def _poll_status(creds: HetznerCredentials, server_id: int, target: str) -> None:
    elapsed = 0
    while True:
        info = await hetzner_get_server(creds, server_id)
        if info.status == target:
            return
        if elapsed >= POLL_TIMEOUT:
            raise HetznerAPIError("timeout")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL


# --- Account ---


async def hetzner_login(creds: HetznerCredentials) -> AccountInfo:
    """Validates the API token. Hetzner Cloud tokens are project-scoped
    with no dedicated "who am I" endpoint, so this just makes a cheap
    authenticated read (also used to show a quick server count on connect)."""
    _, payload = await _request(creds, "GET", "/servers", params={"per_page": 1})
    total = (payload or {}).get("meta", {}).get("pagination", {}).get("total_entries", 0)
    return AccountInfo(server_count=int(total or 0))


# --- Catalog ---


async def hetzner_list_locations(creds: HetznerCredentials) -> list[LocationInfo]:
    _, payload = await _request(creds, "GET", "/locations")
    return [
        LocationInfo(name=item["name"], description=item.get("description", item["name"]), country=item.get("country", ""))
        for item in (payload or {}).get("locations", [])
        if isinstance(item, dict)
    ]


async def hetzner_list_available_server_types(creds: HetznerCredentials, location: str) -> list[ServerTypeInfo]:
    """Lists the curated server types actually offered in ``location`` —
    Hetzner reports per-location pricing/availability via each type's own
    "prices" array; a type simply has no entry for a location it isn't
    sold in there, which is what filters the curated list down."""
    _, payload = await _request(creds, "GET", "/server_types")
    by_name: dict[str, dict] = {}
    for item in (payload or {}).get("server_types", []):
        if not isinstance(item, dict) or item.get("name") not in CURATED_SERVER_TYPES or item.get("deprecated"):
            continue
        by_name[item["name"]] = item

    result = []
    for name in CURATED_SERVER_TYPES:
        item = by_name.get(name)
        if not item:
            continue
        price_entry = next((p for p in item.get("prices", []) if p.get("location") == location), None)
        if price_entry is None:
            continue
        price_hourly = None
        gross = (price_entry.get("price_hourly") or {}).get("gross")
        if gross is not None:
            try:
                price_hourly = float(gross)
            except (TypeError, ValueError):
                price_hourly = None
        result.append(
            ServerTypeInfo(
                name=name, cores=int(item.get("cores", 0) or 0), memory_gb=float(item.get("memory", 0) or 0),
                disk_gb=int(item.get("disk", 0) or 0), price_hourly=price_hourly,
            )
        )
    return result


async def hetzner_list_curated_server_types(creds: HetznerCredentials) -> list[ServerTypeInfo]:
    """Every curated server type that's sold *anywhere* at all, each
    annotated with exactly which locations it's sold in (from its own
    "prices" array). Used to drive the create wizard in Hetzner's own
    website order -- type first, then only that type's own available
    locations -- instead of the other way around. A type with prices in no
    location at all is skipped entirely, same principle as filtering by a
    single location in hetzner_list_available_server_types."""
    _, payload = await _request(creds, "GET", "/server_types")
    by_name: dict[str, dict] = {}
    for item in (payload or {}).get("server_types", []):
        if not isinstance(item, dict) or item.get("name") not in CURATED_SERVER_TYPES or item.get("deprecated"):
            continue
        by_name[item["name"]] = item

    result = []
    for name in CURATED_SERVER_TYPES:
        item = by_name.get(name)
        if not item:
            continue
        prices = item.get("prices") or []
        locations = [p.get("location") for p in prices if isinstance(p, dict) and p.get("location")]
        if not locations:
            continue
        gross_values: list[float] = []
        for p in prices:
            gross = (p.get("price_hourly") or {}).get("gross")
            if gross is not None:
                try:
                    gross_values.append(float(gross))
                except (TypeError, ValueError):
                    pass
        result.append(
            ServerTypeInfo(
                name=name, cores=int(item.get("cores", 0) or 0), memory_gb=float(item.get("memory", 0) or 0),
                disk_gb=int(item.get("disk", 0) or 0),
                price_hourly=min(gross_values) if gross_values else None,
                locations=locations,
            )
        )
    return result


async def hetzner_list_available_images(creds: HetznerCredentials) -> list[ImageInfo]:
    # Unlike Azure's fully-static image catalog, Hetzner's image catalog
    # differs per project, so the curated names still have to be resolved
    # against this project's own /images list.
    _, payload = await _request(creds, "GET", "/images", params={"type": "system", "per_page": 50})
    by_name = {
        item["name"]: item for item in (payload or {}).get("images", []) if isinstance(item, dict) and item.get("name")
    }
    result = []
    for name in CURATED_IMAGES:
        item = by_name.get(name)
        if not item:
            continue
        # ``key`` deliberately holds the image *name*, not its numeric id.
        # Hetzner now keys images by (name, architecture) -- e.g. two
        # separate "ubuntu-24.04" entries, one x86 and one arm -- and
        # /images can return either one for a given name arbitrarily here.
        # Passing that id straight to server creation risks an architecture
        # mismatch with whatever server type was picked ("image has wrong
        # architecture"); passing the name instead lets Hetzner's own API
        # resolve the correct architecture-matching image itself.
        result.append(ImageInfo(key=item["name"], name=item["name"], description=item.get("description") or item["name"]))
    return result


# --- SSH keys ---


async def _ensure_ssh_key(creds: HetznerCredentials, public_key: str) -> int:
    """Hetzner needs an SSH key registered as its own resource before it can
    be attached to a server (unlike UpCloud/Azure, which take the raw key
    inline at create time) — idempotent: reuses an already-uploaded key
    with the same content instead of erroring on a duplicate."""
    public_key = public_key.strip()
    _, payload = await _request(creds, "GET", "/ssh_keys", params={"per_page": 50})
    for item in (payload or {}).get("ssh_keys", []):
        if isinstance(item, dict) and item.get("public_key", "").strip() == public_key:
            return item["id"]

    name = f"arsicloudbot-{secrets.token_hex(4)}"
    _, payload = await _request(creds, "POST", "/ssh_keys", json_body={"name": name, "public_key": public_key})
    return payload["ssh_key"]["id"]


# --- Servers ---


def _server_from_payload(item: dict) -> ServerInfo:
    public_net = item.get("public_net") or {}
    ipv4 = (public_net.get("ipv4") or {}).get("ip")
    ipv6 = (public_net.get("ipv6") or {}).get("ip")
    return ServerInfo(
        id=item["id"],
        name=item.get("name", ""),
        status=item.get("status", "unknown"),
        server_type=(item.get("server_type") or {}).get("name", ""),
        location=(item.get("datacenter") or {}).get("location", {}).get("name", ""),
        ipv4=ipv4,
        ipv6=ipv6,
    )


async def hetzner_list_servers(creds: HetznerCredentials) -> list[ServerInfo]:
    _, payload = await _request(creds, "GET", "/servers", params={"per_page": 50})
    return [_server_from_payload(item) for item in (payload or {}).get("servers", []) if isinstance(item, dict)]


async def hetzner_get_server(creds: HetznerCredentials, server_id: int) -> ServerInfo:
    status, payload = await _request(creds, "GET", f"/servers/{server_id}")
    if status == 404:
        raise HetznerAPIError("not_found")
    return _server_from_payload(payload["server"])


async def hetzner_create_server(
    creds: HetznerCredentials,
    *,
    name: str,
    server_type: str,
    image_key: str,
    location: str,
    ssh_public_key: str | None = None,
    ipv6_enabled: bool = True,
    primary_ipv4_id: int | None = None,
    progress=None,
) -> ServerInfo:
    async def tick(step: str) -> None:
        if progress:
            await progress(step)

    ssh_key_ids: list[int] = []
    if ssh_public_key:
        await tick("ssh_key")
        ssh_key_ids = [await _ensure_ssh_key(creds, ssh_public_key)]

    await tick("server")
    body = {"name": name, "server_type": server_type, "image": image_key, "location": location}
    if ssh_key_ids:
        body["ssh_keys"] = ssh_key_ids
    # Only sent when the caller wants something other than Hetzner's own
    # default (a freshly auto-generated IPv4 + IPv6) -- an explicit
    # public_net omits ipv4/ipv6 entirely for "auto", or names an existing
    # unassigned Primary IP's id to attach that one instead.
    if not ipv6_enabled or primary_ipv4_id is not None:
        public_net: dict = {"enable_ipv4": True, "enable_ipv6": ipv6_enabled}
        if primary_ipv4_id is not None:
            public_net["ipv4"] = primary_ipv4_id
        body["public_net"] = public_net

    _, payload = await _request(creds, "POST", "/servers", json_body=body)
    server_data = payload["server"]
    action = payload.get("action")
    root_password = payload.get("root_password")

    if action and action.get("id"):
        await tick("provisioning")
        await _poll_action(creds, action["id"])

    detail = await hetzner_get_server(creds, server_data["id"])
    detail.root_password = root_password
    return detail


async def _do_power_action(creds: HetznerCredentials, server_id: int, action_name: str, target_status: str) -> None:
    _, payload = await _request(creds, "POST", f"/servers/{server_id}/actions/{action_name}")
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])
    await _poll_status(creds, server_id, target_status)


async def hetzner_start_server(creds: HetznerCredentials, server_id: int) -> None:
    await _do_power_action(creds, server_id, "poweron", "running")


async def hetzner_stop_server(creds: HetznerCredentials, server_id: int) -> None:
    await _do_power_action(creds, server_id, "poweroff", "off")


async def hetzner_reboot_server(creds: HetznerCredentials, server_id: int) -> None:
    await _do_power_action(creds, server_id, "reboot", "running")


async def hetzner_rebuild_server(creds: HetznerCredentials, server_id: int) -> None:
    """Reinstalls the OS from the same image the server currently has —
    same as the "Rebuild from image" action on the Hetzner Cloud Console.
    Wipes the disk, keeps the server's id/name/network/type/IPs."""
    status, payload = await _request(creds, "GET", f"/servers/{server_id}")
    if status == 404:
        raise HetznerAPIError("not_found")
    server_data = payload["server"]
    current_status = server_data.get("status", "unknown")
    image = server_data.get("image") or {}
    image_key = image.get("name") or image.get("id")
    if not image_key:
        raise HetznerAPIError("detail:server has no known image to rebuild from")

    _, payload = await _request(
        creds, "POST", f"/servers/{server_id}/actions/rebuild", json_body={"image": image_key}
    )
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])
    await _poll_status(creds, server_id, "running" if current_status != "off" else "off")


async def hetzner_resize_server(creds: HetznerCredentials, server_id: int, server_type: str) -> None:
    """Changes the server's plan (server_type) — Hetzner requires the
    server to be powered off first, same as UpCloud's plan-change gate."""
    _, payload = await _request(
        creds, "POST", f"/servers/{server_id}/actions/change_type",
        json_body={"server_type": server_type, "upgrade_disk": False},
    )
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])


async def hetzner_delete_server(creds: HetznerCredentials, server_id: int) -> None:
    status, payload = await _request(creds, "DELETE", f"/servers/{server_id}")
    if status == 404:
        return
    action = (payload or {}).get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])


# --- Floating IPs ---


def _floating_ip_from_payload(item: dict) -> FloatingIPInfo:
    return FloatingIPInfo(
        id=item["id"],
        ip=item.get("ip", ""),
        ip_type=item.get("type", "ipv4"),
        server_id=item.get("server"),
        location=(item.get("home_location") or {}).get("name", ""),
    )


async def hetzner_list_floating_ips(creds: HetznerCredentials, server_id: int) -> list[FloatingIPInfo]:
    _, payload = await _request(creds, "GET", "/floating_ips", params={"per_page": 50})
    return [
        _floating_ip_from_payload(item)
        for item in (payload or {}).get("floating_ips", [])
        if isinstance(item, dict) and item.get("server") == server_id
    ]


async def hetzner_list_all_floating_ips(creds: HetznerCredentials) -> list[FloatingIPInfo]:
    """Every Floating IP owned by the project, assigned or not -- used by the
    standalone IP-addresses section, unlike hetzner_list_floating_ips which
    is scoped to one server's detail screen."""
    _, payload = await _request(creds, "GET", "/floating_ips", params={"per_page": 50})
    return [
        _floating_ip_from_payload(item)
        for item in (payload or {}).get("floating_ips", [])
        if isinstance(item, dict)
    ]


async def hetzner_add_floating_ip(creds: HetznerCredentials, server_id: int, ip_type: str = "ipv4") -> FloatingIPInfo:
    _, payload = await _request(
        creds, "POST", "/floating_ips", json_body={"type": ip_type, "server": server_id}
    )
    action = payload.get("action")
    if action and action.get("id"):
        await _poll_action(creds, action["id"])
    return _floating_ip_from_payload(payload["floating_ip"])


async def hetzner_create_floating_ip(creds: HetznerCredentials, ip_type: str, location: str) -> FloatingIPInfo:
    """Buys a Floating IP that isn't attached to any server yet -- the
    project-level "buy an IP" flow, as opposed to hetzner_add_floating_ip
    which always attaches to a given server immediately."""
    _, payload = await _request(
        creds, "POST", "/floating_ips", json_body={"type": ip_type, "home_location": location}
    )
    action = payload.get("action")
    if action and action.get("id"):
        await _poll_action(creds, action["id"])
    return _floating_ip_from_payload(payload["floating_ip"])


async def hetzner_assign_floating_ip(creds: HetznerCredentials, floating_ip_id: int, server_id: int) -> None:
    _, payload = await _request(
        creds, "POST", f"/floating_ips/{floating_ip_id}/actions/assign", json_body={"server": server_id}
    )
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])


async def hetzner_unassign_floating_ip(creds: HetznerCredentials, floating_ip_id: int) -> None:
    _, payload = await _request(creds, "POST", f"/floating_ips/{floating_ip_id}/actions/unassign")
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])


async def hetzner_remove_floating_ip(creds: HetznerCredentials, floating_ip_id: int) -> None:
    status, _ = await _request(creds, "DELETE", f"/floating_ips/{floating_ip_id}")
    if status == 404:
        return


# --- Primary IPs ---


def _primary_ip_from_payload(item: dict) -> PrimaryIPInfo:
    datacenter = item.get("datacenter") or {}
    location = (datacenter.get("location") or {}).get("name", "")
    return PrimaryIPInfo(
        id=item["id"], ip=item.get("ip", ""), ip_type=item.get("type", "ipv4"),
        location=location, server_id=item.get("assignee_id"),
    )


async def hetzner_list_primary_ips(creds: HetznerCredentials) -> list[PrimaryIPInfo]:
    _, payload = await _request(creds, "GET", "/primary_ips", params={"per_page": 50})
    return [
        _primary_ip_from_payload(item) for item in (payload or {}).get("primary_ips", []) if isinstance(item, dict)
    ]


async def hetzner_create_primary_ip(creds: HetznerCredentials, ip_type: str, location: str) -> PrimaryIPInfo:
    """Buys a Primary IP not assigned to any server -- Hetzner's newer
    replacement for a server's automatic public IP, which (unlike a
    Floating IP) can also be handed to a server right at creation time."""
    name = f"arsicloudbot-{secrets.token_hex(4)}"
    _, payload = await _request(
        creds, "POST", "/primary_ips", json_body={"type": ip_type, "location": location, "name": name}
    )
    action = payload.get("action")
    if action and action.get("id"):
        await _poll_action(creds, action["id"])
    return _primary_ip_from_payload(payload["primary_ip"])


async def hetzner_assign_primary_ip(creds: HetznerCredentials, primary_ip_id: int, server_id: int) -> None:
    _, payload = await _request(
        creds, "POST", f"/primary_ips/{primary_ip_id}/actions/assign",
        json_body={"assignee_id": server_id, "assignee_type": "server"},
    )
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])


async def hetzner_unassign_primary_ip(creds: HetznerCredentials, primary_ip_id: int) -> None:
    _, payload = await _request(creds, "POST", f"/primary_ips/{primary_ip_id}/actions/unassign")
    action = payload.get("action") or {}
    if action.get("id"):
        await _poll_action(creds, action["id"])


async def hetzner_delete_primary_ip(creds: HetznerCredentials, primary_ip_id: int) -> None:
    status, _ = await _request(creds, "DELETE", f"/primary_ips/{primary_ip_id}")
    if status == 404:
        return


def hetzner_is_type_unavailable_error(error_detail: str) -> bool:
    """Best-effort detection of Hetzner's own deploy-time rejection when a
    server type turns out not to actually be orderable in the chosen
    location (e.g. "unsupported location for server type") -- a live user
    hit this. hetzner_list_available_server_types can't predict it ahead of
    time: its only signal is whether the location appears in the type's own
    "prices" array, and that can still be true for a type that Hetzner
    doesn't actually let you order there right now (limited/sold-out
    hardware generations). The create flow catches this and drops just the
    failed type from the picker instead of dying with a raw error."""
    lowered = error_detail.lower()
    return "location" in lowered and ("server type" in lowered or "server_type" in lowered)
