from __future__ import annotations

import asyncio
import hashlib
import hmac
import json as json_module
import time
from base64 import standard_b64encode
from dataclasses import dataclass
from urllib.parse import urlencode, urlparse

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=20)

EXOSCALE_API_BASE = "https://api-{zone}.exoscale.com/v2"

POLL_INTERVAL = 3
POLL_TIMEOUT = 240

# Exoscale has no "list zones" endpoint -- a zone is just which regional API
# host a request goes to (api-<zone>.exoscale.com). This is the full,
# generally-available zone list from Exoscale's own datacenter page.
ZONES = [
    ("ch-gva-2", "Geneva, Switzerland"),
    ("ch-dk-2", "Zurich, Switzerland"),
    ("de-fra-1", "Frankfurt, Germany"),
    ("de-muc-1", "Munich, Germany"),
    ("at-vie-1", "Vienna, Austria"),
    ("at-vie-2", "Vienna, Austria"),
    ("bg-sof-1", "Sofia, Bulgaria"),
    ("hr-zag-1", "Zagreb, Croatia"),
]
DEFAULT_ZONE = ZONES[0][0]


class ExoscaleAPIError(Exception):
    """str(exc) is one of a small set of reason codes ('wrong_credentials',
    'connect_failed', 'bad_response', 'not_found', 'timeout'), or
    'detail:<msg>' carrying Exoscale's own error message -- the texts layer
    translates these into a human message, so it's always safe to show
    directly."""


@dataclass
class ExoscaleCredentials:
    key: str
    secret: str


@dataclass
class AccountInfo:
    pass  # Exoscale has no dedicated "whoami" -- a successful signed call is the whole check.


@dataclass
class InstanceTypeInfo:
    id: str
    family: str
    size: str
    cpus: int
    memory: int


@dataclass
class TemplateInfo:
    id: str
    name: str
    default_user: str = "root"


@dataclass
class ServerInfo:
    id: str
    name: str
    state: str  # "running" | "stopped" | "starting" | "stopping" | ...
    zone: str
    instance_type_id: str = ""
    template_id: str = ""
    instance_type_label: str = ""
    template_label: str = ""
    public_ip: str | None = None
    password: str | None = None


def _connector() -> aiohttp.TCPConnector:
    return aiohttp.TCPConnector(ssl=True)


def _extract_detail(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    msg = payload.get("message")
    return msg if isinstance(msg, str) and msg else None


def _sign_request(creds: ExoscaleCredentials, method: str, path: str, params: dict | None, body: bytes) -> str:
    """Exoscale API v2 (EXO2-HMAC-SHA256) request signing. The signed
    message is 5 newline-joined segments: "METHOD path", the raw body,
    query param VALUES only (no names, sorted by param name), signed
    header values (none, always empty), and the expiry timestamp -- see
    bot.services.hetzner_api for the sibling Hetzner scheme this mirrors in
    spirit, though the two signing algorithms are unrelated. Ported from
    the official `requests-exoscale-auth` package's ExoscaleV2Auth."""
    expires = int(time.time() + 10 * 60)
    signed_params = sorted(params) if params else []
    params_values = "".join(str(params[p]) for p in signed_params) if params else ""
    msg = b"\n".join(
        [
            f"{method} {path}".encode("utf-8"),
            body,
            params_values.encode("utf-8"),
            b"",
            str(expires).encode("utf-8"),
        ]
    )
    signature = hmac.new(creds.secret.encode("utf-8"), msg=msg, digestmod=hashlib.sha256).digest()
    header = f"EXO2-HMAC-SHA256 credential={creds.key}"
    if signed_params:
        header += f",signed-query-args={';'.join(signed_params)}"
    header += f",expires={expires},signature={standard_b64encode(signature).decode('utf-8')}"
    return header


async def _request(
    creds: ExoscaleCredentials, zone: str, method: str, path: str, *, json_body: dict | None = None, params: dict | None = None,
) -> object:
    body = json_module.dumps(json_body).encode("utf-8") if json_body is not None else b""
    base = EXOSCALE_API_BASE.format(zone=zone)
    url = f"{base}{path}"
    if params:
        url += "?" + urlencode(params)
    # The signed path is the request URL's actual path -- which includes
    # the "/v2" base prefix -- not just the endpoint-relative `path` above;
    # signing the wrong one produces a signature the real API rejects with
    # a 401 even for correct credentials.
    signed_path = urlparse(url).path
    headers = {
        "Authorization": _sign_request(creds, method, signed_path, params, body),
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
            async with session.request(method, url, data=body or None, headers=headers) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError):
                    payload = None
                if resp.status == 401 or resp.status == 403:
                    raise ExoscaleAPIError("wrong_credentials")
                if resp.status == 404:
                    raise ExoscaleAPIError("not_found")
                if resp.status >= 400:
                    detail = _extract_detail(payload)
                    raise ExoscaleAPIError(f"detail:{detail}" if detail else "bad_response")
                return payload
    except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError) as exc:
        raise ExoscaleAPIError("connect_failed") from exc


async def _poll_operation(creds: ExoscaleCredentials, zone: str, operation_id: str) -> str | None:
    """Instance create/lifecycle calls return an async "operation" object,
    not the affected resource directly -- polls it until terminal and
    returns the affected resource's id (``reference.id``), or None if the
    operation carries no reference (e.g. a plain stop/delete)."""
    elapsed = 0
    while True:
        payload = await _request(creds, zone, "GET", f"/operation/{operation_id}")
        state = (payload or {}).get("state")
        if state == "success":
            reference = (payload or {}).get("reference") or {}
            return reference.get("id")
        if state in ("failure", "timeout"):
            reason = (payload or {}).get("reason") or (payload or {}).get("message") or "operation failed"
            raise ExoscaleAPIError(f"detail:{reason}")
        if elapsed >= POLL_TIMEOUT:
            raise ExoscaleAPIError("timeout")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL


# --- Account ---


async def exoscale_login(creds: ExoscaleCredentials) -> AccountInfo:
    """Validates the API key/secret. No dedicated "who am I" endpoint, so
    this just makes a cheap authenticated read against one zone."""
    await _request(creds, DEFAULT_ZONE, "GET", "/instance-type")
    return AccountInfo()


# --- Catalog ---


async def exoscale_list_instance_types(creds: ExoscaleCredentials, zone: str) -> list[InstanceTypeInfo]:
    """Only the "standard" (general-purpose) family -- GPU/storage/memory-
    optimized families are a much longer, more specialized catalog not
    worth showing in a chat picker. Sorted by (cpus, memory) rather than
    the "size" name, since Exoscale's size names don't sort alphabetically
    in capacity order."""
    payload = await _request(creds, zone, "GET", "/instance-type")
    items = (payload or {}).get("instance-types", [])
    result = [
        InstanceTypeInfo(
            id=item["id"], family=item.get("family", ""), size=item.get("size", ""),
            cpus=int(item.get("cpus", 0) or 0), memory=int(item.get("memory", 0) or 0),
        )
        for item in items
        if isinstance(item, dict) and item.get("id") and item.get("family") == "standard"
    ]
    result.sort(key=lambda t: (t.cpus, t.memory))
    return result


async def exoscale_get_instance_type(creds: ExoscaleCredentials, zone: str, type_id: str) -> InstanceTypeInfo | None:
    payload = await _request(creds, zone, "GET", f"/instance-type/{type_id}")
    if not isinstance(payload, dict) or not payload.get("id"):
        return None
    return InstanceTypeInfo(
        id=payload["id"], family=payload.get("family", ""), size=payload.get("size", ""),
        cpus=int(payload.get("cpus", 0) or 0), memory=int(payload.get("memory", 0) or 0),
    )


async def exoscale_list_templates(creds: ExoscaleCredentials, zone: str) -> list[TemplateInfo]:
    """Every public template, sorted by name -- no name/family filtering,
    since Exoscale's template catalog varies per zone and guessing at a
    curated subset risks hiding the only OS actually offered somewhere."""
    payload = await _request(creds, zone, "GET", "/template", params={"visibility": "public"})
    items = (payload or {}).get("templates", [])
    result = [
        TemplateInfo(id=item["id"], name=item.get("name", ""), default_user=item.get("default-user") or "root")
        for item in items
        if isinstance(item, dict) and item.get("id") and item.get("name")
    ]
    result.sort(key=lambda tpl: tpl.name)
    return result


async def exoscale_get_template(creds: ExoscaleCredentials, zone: str, template_id: str) -> TemplateInfo | None:
    payload = await _request(creds, zone, "GET", f"/template/{template_id}")
    if not isinstance(payload, dict) or not payload.get("id"):
        return None
    return TemplateInfo(id=payload["id"], name=payload.get("name", ""), default_user=payload.get("default-user") or "root")


# --- SSH keys ---


async def _ensure_ssh_key(creds: ExoscaleCredentials, zone: str, public_key: str) -> str:
    """SSH keys are referenced by name (not id) at instance-create time --
    idempotent: reuses an already-registered key with the same fingerprint-
    worthy content under a name derived from it instead of erroring on a
    duplicate import."""
    public_key = public_key.strip()
    name = f"arsicloudbot-{hashlib.sha256(public_key.encode('utf-8')).hexdigest()[:16]}"
    payload = await _request(creds, zone, "GET", "/ssh-key")
    for item in (payload or {}).get("ssh-keys", []):
        if isinstance(item, dict) and item.get("name") == name:
            return name
    operation = await _request(
        creds, zone, "POST", "/ssh-key", json_body={"name": name, "public-key": public_key}
    )
    op_id = (operation or {}).get("id")
    if op_id:
        await _poll_operation(creds, zone, op_id)
    return name


# --- Servers (compute instances) ---


def _ref_id(value: object) -> str:
    """Exoscale's own API reference is inconsistent about whether a
    reference field (instance-type, template) comes back as {"id": "..."}
    or a bare id string in list-instances responses -- handles either
    shape instead of assuming one and raising on the other."""
    if isinstance(value, dict):
        return value.get("id", "")
    if isinstance(value, str):
        return value
    return ""


def _server_from_payload(item: dict, zone: str) -> ServerInfo:
    return ServerInfo(
        id=item.get("id", ""),
        name=item.get("name", ""),
        state=item.get("state", "unknown"),
        zone=zone,
        instance_type_id=_ref_id(item.get("instance-type")),
        template_id=_ref_id(item.get("template")),
        public_ip=item.get("public-ip"),
    )


async def exoscale_list_servers(creds: ExoscaleCredentials, zone: str) -> list[ServerInfo]:
    payload = await _request(creds, zone, "GET", "/instance")
    return [_server_from_payload(item, zone) for item in (payload or {}).get("instances", []) if isinstance(item, dict)]


async def exoscale_get_server(creds: ExoscaleCredentials, zone: str, instance_id: str) -> ServerInfo:
    payload = await _request(creds, zone, "GET", f"/instance/{instance_id}")
    server = _server_from_payload(payload, zone)
    # Resolve type/template ids to human-readable labels -- worth the extra
    # two calls here since the detail screen is viewed far less often than
    # the server list (which skips this to avoid an N+1 per listed server).
    if server.instance_type_id:
        type_info = await exoscale_get_instance_type(creds, zone, server.instance_type_id)
        if type_info:
            server.instance_type_label = f"{type_info.family}.{type_info.size}"
    if server.template_id:
        template_info = await exoscale_get_template(creds, zone, server.template_id)
        if template_info:
            server.template_label = template_info.name
    return server


async def exoscale_reveal_password(creds: ExoscaleCredentials, zone: str, instance_id: str) -> str | None:
    try:
        payload = await _request(creds, zone, "GET", f"/instance/{instance_id}:password")
    except ExoscaleAPIError:
        return None
    password = (payload or {}).get("password")
    return password if isinstance(password, str) and password else None


async def exoscale_create_server(
    creds: ExoscaleCredentials,
    zone: str,
    *,
    name: str,
    instance_type_id: str,
    template_id: str,
    disk_size: int = 10,
    ssh_public_key: str | None = None,
    progress=None,
) -> ServerInfo:
    async def tick(step: str) -> None:
        if progress:
            await progress(step)

    body: dict = {
        "name": name,
        "disk-size": disk_size,
        "instance-type": {"id": instance_type_id},
        "template": {"id": template_id},
    }
    if ssh_public_key:
        await tick("ssh_key")
        key_name = await _ensure_ssh_key(creds, zone, ssh_public_key)
        body["ssh-key"] = {"name": key_name}

    await tick("server")
    operation = await _request(creds, zone, "POST", "/instance", json_body=body)
    op_id = (operation or {}).get("id")
    if not op_id:
        raise ExoscaleAPIError("bad_response")

    await tick("provisioning")
    instance_id = await _poll_operation(creds, zone, op_id)
    if not instance_id:
        raise ExoscaleAPIError("bad_response")

    server = await exoscale_get_server(creds, zone, instance_id)
    if not ssh_public_key:
        server.password = await exoscale_reveal_password(creds, zone, instance_id)
    return server


async def _do_lifecycle_action(creds: ExoscaleCredentials, zone: str, instance_id: str, action: str) -> None:
    payload = await _request(creds, zone, "PUT", f"/instance/{instance_id}:{action}")
    op_id = (payload or {}).get("id")
    if op_id:
        await _poll_operation(creds, zone, op_id)


async def exoscale_start_server(creds: ExoscaleCredentials, zone: str, instance_id: str) -> None:
    await _do_lifecycle_action(creds, zone, instance_id, "start")


async def exoscale_stop_server(creds: ExoscaleCredentials, zone: str, instance_id: str) -> None:
    await _do_lifecycle_action(creds, zone, instance_id, "stop")


async def exoscale_reboot_server(creds: ExoscaleCredentials, zone: str, instance_id: str) -> None:
    await _do_lifecycle_action(creds, zone, instance_id, "reboot")


async def exoscale_delete_server(creds: ExoscaleCredentials, zone: str, instance_id: str) -> None:
    payload = await _request(creds, zone, "DELETE", f"/instance/{instance_id}")
    op_id = (payload or {}).get("id")
    if op_id:
        await _poll_operation(creds, zone, op_id)
