from __future__ import annotations

import asyncio
import secrets
from dataclasses import dataclass

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)

DIGITALOCEAN_API_BASE = "https://api.digitalocean.com/v2"

POLL_INTERVAL = 3
POLL_TIMEOUT = 240

# A small, curated shortlist rather than DigitalOcean's full size catalog
# (dozens of CPU-optimized/memory-optimized/storage-optimized variants) --
# same reasoning as the other providers' curated lists: showing everything
# would just be unusable in a chat UI. These are DigitalOcean's standard
# "Basic" droplet sizes, cheapest first.
CURATED_SIZES = ["s-1vcpu-1gb", "s-1vcpu-2gb", "s-2vcpu-2gb", "s-2vcpu-4gb", "s-4vcpu-8gb"]
CURATED_IMAGES = ["ubuntu-24-04-x64", "ubuntu-22-04-x64", "debian-12-x64"]


class DigitalOceanAPIError(Exception):
    """str(exc) is one of a small set of reason codes ('wrong_credentials',
    'connect_failed', 'bad_response', 'not_found', 'timeout'), or
    'detail:<msg>' carrying DigitalOcean's own error message -- the texts
    layer translates these into a human message, so it's always safe to
    show directly."""


@dataclass
class DigitalOceanCredentials:
    token: str


@dataclass
class AccountInfo:
    email: str
    droplet_limit: int


@dataclass
class RegionInfo:
    slug: str
    name: str


@dataclass
class SizeInfo:
    slug: str
    vcpus: int
    memory_mb: int
    disk_gb: int
    price_monthly: float | None = None
    regions: list[str] | None = None


@dataclass
class ImageInfo:
    slug: str
    name: str
    distribution: str = ""


@dataclass
class ServerInfo:
    id: int
    name: str
    status: str  # "new" | "active" | "off" | "archive"
    region: str
    region_name: str = ""
    size_slug: str = ""
    vcpus: int = 0
    memory_mb: int = 0
    disk_gb: int = 0
    ipv4: str | None = None
    ipv6: str | None = None


def _connector() -> aiohttp.TCPConnector:
    return aiohttp.TCPConnector(ssl=True)


def _extract_detail(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    msg = payload.get("message")
    return msg if isinstance(msg, str) and msg else None


async def _request(
    creds: DigitalOceanCredentials, method: str, path: str, *, json_body: dict | None = None, params: dict | None = None,
) -> tuple[int, object]:
    url = f"{DIGITALOCEAN_API_BASE}{path}"
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
                    raise DigitalOceanAPIError("wrong_credentials")
                if resp.status == 404:
                    return resp.status, payload
                if resp.status >= 400:
                    detail = _extract_detail(payload)
                    raise DigitalOceanAPIError(f"detail:{detail}" if detail else "bad_response")
                return resp.status, payload
    except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError) as exc:
        raise DigitalOceanAPIError("connect_failed") from exc


async def _poll_action(creds: DigitalOceanCredentials, droplet_id: int, action_id: int) -> None:
    """Droplet create/lifecycle/resize calls return an async "action"
    resource reflecting the *desired* outcome, not the actual one yet --
    polls that action's own status until it's terminal."""
    elapsed = 0
    while True:
        _, payload = await _request(creds, "GET", f"/droplets/{droplet_id}/actions/{action_id}")
        action = (payload or {}).get("action") or {}
        status = action.get("status")
        if status == "completed":
            return
        if status == "errored":
            raise DigitalOceanAPIError("detail:action failed")
        if elapsed >= POLL_TIMEOUT:
            raise DigitalOceanAPIError("timeout")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL


async def _poll_status(creds: DigitalOceanCredentials, droplet_id: int, target: str) -> None:
    elapsed = 0
    while True:
        info = await digitalocean_get_server(creds, droplet_id)
        if info.status == target:
            return
        if elapsed >= POLL_TIMEOUT:
            raise DigitalOceanAPIError("timeout")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL


# --- Account ---


async def digitalocean_login(creds: DigitalOceanCredentials) -> AccountInfo:
    """Validates the Personal Access Token against the one dedicated
    "who am I" endpoint DigitalOcean does have."""
    _, payload = await _request(creds, "GET", "/account")
    account = (payload or {}).get("account") or {}
    return AccountInfo(email=account.get("email", ""), droplet_limit=int(account.get("droplet_limit", 0) or 0))


# --- Catalog ---


async def digitalocean_list_regions(creds: DigitalOceanCredentials) -> list[RegionInfo]:
    _, payload = await _request(creds, "GET", "/regions")
    return [
        RegionInfo(slug=item["slug"], name=item.get("name", item["slug"]))
        for item in (payload or {}).get("regions", [])
        if isinstance(item, dict) and item.get("available")
    ]


async def digitalocean_list_available_sizes(creds: DigitalOceanCredentials, region: str) -> list[SizeInfo]:
    """Lists the curated sizes actually offered in ``region`` -- each size
    carries its own "regions" array of where it's sold, which is what
    filters the curated list down (mirrors Hetzner's per-location price
    filtering)."""
    _, payload = await _request(creds, "GET", "/sizes", params={"per_page": 200})
    by_slug: dict[str, dict] = {
        item["slug"]: item
        for item in (payload or {}).get("sizes", [])
        if isinstance(item, dict) and item.get("slug") in CURATED_SIZES and item.get("available")
    }
    result = []
    for slug in CURATED_SIZES:
        item = by_slug.get(slug)
        if not item or region not in (item.get("regions") or []):
            continue
        result.append(
            SizeInfo(
                slug=slug, vcpus=int(item.get("vcpus", 0) or 0), memory_mb=int(item.get("memory", 0) or 0),
                disk_gb=int(item.get("disk", 0) or 0), price_monthly=item.get("price_monthly"),
            )
        )
    return result


async def digitalocean_list_available_images(creds: DigitalOceanCredentials) -> list[ImageInfo]:
    _, payload = await _request(creds, "GET", "/images", params={"type": "distribution", "per_page": 200})
    by_slug = {
        item["slug"]: item for item in (payload or {}).get("images", []) if isinstance(item, dict) and item.get("slug")
    }
    result = []
    for slug in CURATED_IMAGES:
        item = by_slug.get(slug)
        if not item:
            continue
        result.append(ImageInfo(slug=slug, name=item.get("name") or slug, distribution=item.get("distribution", "")))
    return result


# --- SSH keys ---


async def _ensure_ssh_key(creds: DigitalOceanCredentials, public_key: str) -> int:
    """DigitalOcean needs an SSH key registered as its own account resource
    before it can be attached to a droplet -- idempotent: reuses an
    already-uploaded key with the same content instead of erroring on a
    duplicate import."""
    public_key = public_key.strip()
    _, payload = await _request(creds, "GET", "/account/keys", params={"per_page": 200})
    for item in (payload or {}).get("ssh_keys", []):
        if isinstance(item, dict) and item.get("public_key", "").strip() == public_key:
            return item["id"]

    name = f"arsicloudbot-{secrets.token_hex(4)}"
    _, payload = await _request(creds, "POST", "/account/keys", json_body={"name": name, "public_key": public_key})
    return payload["ssh_key"]["id"]


# --- Servers (Droplets) ---


def _public_ip(networks: dict, family: str) -> str | None:
    for net in networks.get(family, []) or []:
        if isinstance(net, dict) and net.get("type") == "public":
            return net.get("ip_address")
    return None


def _server_from_payload(item: dict) -> ServerInfo:
    networks = item.get("networks") or {}
    region = item.get("region") or {}
    return ServerInfo(
        id=item["id"],
        name=item.get("name", ""),
        status=item.get("status", "unknown"),
        region=region.get("slug", ""),
        region_name=region.get("name", ""),
        size_slug=item.get("size_slug", ""),
        vcpus=int(item.get("vcpus", 0) or 0),
        memory_mb=int(item.get("memory", 0) or 0),
        disk_gb=int(item.get("disk", 0) or 0),
        ipv4=_public_ip(networks, "v4"),
        ipv6=_public_ip(networks, "v6"),
    )


async def digitalocean_list_servers(creds: DigitalOceanCredentials) -> list[ServerInfo]:
    _, payload = await _request(creds, "GET", "/droplets", params={"per_page": 200})
    return [_server_from_payload(item) for item in (payload or {}).get("droplets", []) if isinstance(item, dict)]


async def digitalocean_get_server(creds: DigitalOceanCredentials, droplet_id: int) -> ServerInfo:
    status, payload = await _request(creds, "GET", f"/droplets/{droplet_id}")
    if status == 404:
        raise DigitalOceanAPIError("not_found")
    return _server_from_payload(payload["droplet"])


async def digitalocean_create_server(
    creds: DigitalOceanCredentials,
    *,
    name: str,
    region: str,
    size: str,
    image: str,
    ssh_public_key: str | None = None,
    progress=None,
) -> ServerInfo:
    async def tick(step: str) -> None:
        if progress:
            await progress(step)

    body: dict = {"name": name, "region": region, "size": size, "image": image, "ipv6": True}
    if ssh_public_key:
        await tick("ssh_key")
        body["ssh_keys"] = [await _ensure_ssh_key(creds, ssh_public_key)]

    await tick("server")
    _, payload = await _request(creds, "POST", "/droplets", json_body=body)
    droplet_data = payload["droplet"]
    actions = (payload.get("links") or {}).get("actions") or []
    action_id = next((a.get("id") for a in actions if isinstance(a, dict)), None)

    if action_id:
        await tick("provisioning")
        await _poll_action(creds, droplet_data["id"], action_id)

    return await digitalocean_get_server(creds, droplet_data["id"])


async def _do_action(creds: DigitalOceanCredentials, droplet_id: int, body: dict) -> None:
    _, payload = await _request(creds, "POST", f"/droplets/{droplet_id}/actions", json_body=body)
    action = (payload or {}).get("action") or {}
    if action.get("id"):
        await _poll_action(creds, droplet_id, action["id"])


async def digitalocean_start_server(creds: DigitalOceanCredentials, droplet_id: int) -> None:
    await _do_action(creds, droplet_id, {"type": "power_on"})
    await _poll_status(creds, droplet_id, "active")


async def digitalocean_stop_server(creds: DigitalOceanCredentials, droplet_id: int) -> None:
    await _do_action(creds, droplet_id, {"type": "power_off"})
    await _poll_status(creds, droplet_id, "off")


async def digitalocean_reboot_server(creds: DigitalOceanCredentials, droplet_id: int) -> None:
    await _do_action(creds, droplet_id, {"type": "reboot"})
    await _poll_status(creds, droplet_id, "active")


async def digitalocean_resize_server(creds: DigitalOceanCredentials, droplet_id: int, size: str) -> None:
    """Changes the droplet's plan (size) -- DigitalOcean requires the
    droplet to be powered off first, same gate as Hetzner/UpCloud's own
    plan-change. ``disk=False`` keeps the current disk size, since a disk
    upgrade can never be undone -- same choice Hetzner's resize makes."""
    await _do_action(creds, droplet_id, {"type": "resize", "size": size, "disk": False})


async def digitalocean_delete_server(creds: DigitalOceanCredentials, droplet_id: int) -> None:
    status, _ = await _request(creds, "DELETE", f"/droplets/{droplet_id}")
    if status == 404:
        return
