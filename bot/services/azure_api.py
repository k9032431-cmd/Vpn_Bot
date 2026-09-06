from __future__ import annotations

import asyncio
import json
import secrets
import string
from dataclasses import dataclass, field
from typing import Awaitable, Callable

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30)

AZURE_LOGIN_BASE = "https://login.microsoftonline.com"
AZURE_MANAGEMENT_BASE = "https://management.azure.com"
AZURE_SCOPE = "https://management.azure.com/.default"

# Every VM this bot creates lives in one fixed resource group per Azure
# account, with one shared VNet/subnet per (account, location) — this keeps
# delete simple (VM + its own NIC/public IP/NSG go away; the RG/VNet are
# reused by the next VM) without needing a resource-group picker in the UI.
RESOURCE_GROUP_NAME = "arsicloudbot-rg"

API_VERSION_SUBS = "2022-12-01"
API_VERSION_RG = "2022-09-01"
API_VERSION_NETWORK = "2023-09-01"
API_VERSION_COMPUTE = "2023-09-01"
API_VERSION_SKUS = "2021-07-01"

POLL_INTERVAL = 3
POLL_TIMEOUT = 240

ADMIN_USERNAME = "azureuser"

ProgressCallback = Callable[[str], Awaitable[None]]


class AzureAPIError(Exception):
    """Raised when an Azure ARM API call fails.

    ``str(exc)`` is one of a small set of reason codes ('wrong_credentials',
    'connect_failed', 'bad_response', 'timeout', 'not_found'), or
    'detail:<msg>' carrying Azure's own error message — the texts layer
    translates these into a human message, so it's always safe to show
    directly.
    """


@dataclass
class AzureCredentials:
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str
    # Overridable only so fake-server tests can point both endpoints
    # elsewhere — real usage always talks to the real Azure endpoints.
    management_base: str = AZURE_MANAGEMENT_BASE
    login_base: str = AZURE_LOGIN_BASE


@dataclass
class AccountInfo:
    subscription_id: str
    display_name: str
    state: str = "Enabled"


@dataclass
class LocationInfo:
    name: str
    display_name: str


@dataclass
class VmSizeInfo:
    name: str
    cores: int
    memory_mb: int


@dataclass
class ImageInfo:
    key: str
    title: str
    publisher: str
    offer: str
    sku: str
    version: str = "latest"


@dataclass
class VMInfo:
    name: str
    location: str
    vm_size: str
    power_state: str  # "running" | "deallocated" | "stopped" | "starting" | "stopping" | "unknown"
    public_ip: str | None = None
    admin_username: str = ADMIN_USERNAME
    admin_password: str | None = None  # only set right after creation


# A short, static catalog rather than crawling the full Marketplace API
# (which needs several extra authenticated calls per publisher/offer/sku) —
# these are well-known, stable image references that work in every region.
CURATED_IMAGES: list[ImageInfo] = [
    ImageInfo("ubuntu2404", "Ubuntu Server 24.04 LTS", "Canonical", "ubuntu-24_04-lts", "server"),
    ImageInfo("ubuntu2204", "Ubuntu Server 22.04 LTS", "Canonical", "0001-com-ubuntu-server-jammy", "22_04-lts-gen2"),
    ImageInfo("debian12", "Debian 12", "Debian", "debian-12", "12-gen2"),
]

# A curated shortlist rather than every VM size Azure returns (200+,
# unusable in a paginated bot menu) — filtered against what's actually
# available in the chosen location before being shown.
CURATED_SIZES = [
    "Standard_B1s",
    "Standard_B1ms",
    "Standard_B2s",
    "Standard_B2ms",
    "Standard_D2s_v5",
    "Standard_D4s_v5",
]


def generate_azure_password(length: int = 16) -> str:
    """Generates a password meeting Azure's Linux VM complexity rule (12-72
    chars, at least 3 of lower/upper/digit/special)."""
    length = max(length, 12)
    specials = "!@#$%^&*()-_=+"
    required = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(specials),
    ]
    pool = string.ascii_lowercase + string.ascii_uppercase + string.digits + specials
    chars = required + [secrets.choice(pool) for _ in range(length - len(required))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _connector() -> aiohttp.TCPConnector:
    return aiohttp.TCPConnector(ssl=True)


async def _get_token(creds: AzureCredentials) -> str:
    url = f"{creds.login_base.rstrip('/')}/{creds.tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scope": AZURE_SCOPE,
    }
    try:
        async with aiohttp.ClientSession(connector=_connector(), timeout=REQUEST_TIMEOUT) as session:
            async with session.post(url, data=data) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    payload = None
                if resp.status in (400, 401):
                    raise AzureAPIError("wrong_credentials")
                if resp.status >= 400:
                    raise AzureAPIError("bad_response")
                token = (payload or {}).get("access_token")
                if not token:
                    raise AzureAPIError("bad_response")
                return token
    except (aiohttp.ClientError, TimeoutError) as exc:
        raise AzureAPIError("connect_failed") from exc


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
    method: str,
    path: str,
    creds: AzureCredentials,
    *,
    json_body: dict | None = None,
    params: dict | None = None,
) -> tuple[int, object]:
    token = await _get_token(creds)
    url = f"{creds.management_base.rstrip('/')}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with aiohttp.ClientSession(
            connector=_connector(), timeout=REQUEST_TIMEOUT, headers=headers
        ) as session:
            async with session.request(method, url, json=json_body, params=params) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    payload = None
                if resp.status == 401:
                    raise AzureAPIError("wrong_credentials")
                if resp.status == 404:
                    return resp.status, payload
                if resp.status >= 400:
                    detail = _extract_detail(payload)
                    if detail:
                        raise AzureAPIError(f"detail:{detail}")
                    raise AzureAPIError("bad_response")
                return resp.status, payload
    except (aiohttp.ClientError, TimeoutError) as exc:
        raise AzureAPIError("connect_failed") from exc


async def _poll_provisioning_state(
    path: str, creds: AzureCredentials, *, params: dict | None = None,
    timeout: int | None = None, interval: int | None = None,
) -> dict:
    """ARM resource PUTs are asynchronous — the initial response reflects
    the *desired* state, not the actual one yet. Polls the resource's own
    GET until ``properties.provisioningState`` reaches a terminal value.

    ``timeout``/``interval`` read the module-level POLL_TIMEOUT/POLL_INTERVAL
    at call time (not as bound defaults) so tests can speed them up by
    patching the module attributes after import."""
    timeout = POLL_TIMEOUT if timeout is None else timeout
    interval = POLL_INTERVAL if interval is None else interval
    elapsed = 0
    while True:
        _, payload = await _request("GET", path, creds, params=params)
        state = (payload or {}).get("properties", {}).get("provisioningState") if isinstance(payload, dict) else None
        if state == "Succeeded":
            return payload
        if state in ("Failed", "Canceled"):
            raise AzureAPIError("detail:provisioning failed")
        if elapsed >= timeout:
            raise AzureAPIError("timeout")
        await asyncio.sleep(interval)
        elapsed += interval


async def _poll_deleted(
    path: str, creds: AzureCredentials, *, params: dict | None = None,
    timeout: int | None = None, interval: int | None = None,
) -> None:
    timeout = POLL_TIMEOUT if timeout is None else timeout
    interval = POLL_INTERVAL if interval is None else interval
    elapsed = 0
    while True:
        status, _ = await _request("GET", path, creds, params=params)
        if status == 404:
            return
        if elapsed >= timeout:
            raise AzureAPIError("timeout")
        await asyncio.sleep(interval)
        elapsed += interval


# --- Account ---


def _rg_path(creds: AzureCredentials) -> str:
    return f"/subscriptions/{creds.subscription_id}/resourceGroups/{RESOURCE_GROUP_NAME}"


async def azure_login(creds: AzureCredentials) -> AccountInfo:
    """Validates credentials and returns the subscription snapshot — a
    wrong tenant/client/secret raises AzureAPIError("wrong_credentials")
    from the token call, and a subscription id the app has no access to
    raises the same from the subscription lookup."""
    return await azure_get_account(creds)


async def azure_get_account(creds: AzureCredentials) -> AccountInfo:
    path = f"/subscriptions/{creds.subscription_id}"
    status, payload = await _request("GET", path, creds, params={"api-version": API_VERSION_SUBS})
    if status == 404:
        raise AzureAPIError("wrong_credentials")
    payload = payload or {}
    return AccountInfo(
        subscription_id=payload.get("subscriptionId", creds.subscription_id),
        display_name=payload.get("displayName", ""),
        state=payload.get("state", "Enabled"),
    )


# --- Catalog: locations, sizes, images ---


async def azure_list_locations(creds: AzureCredentials) -> list[LocationInfo]:
    path = f"/subscriptions/{creds.subscription_id}/locations"
    _, payload = await _request("GET", path, creds, params={"api-version": API_VERSION_SUBS})
    entries = (payload or {}).get("value", [])
    return [
        LocationInfo(name=item.get("name", ""), display_name=item.get("displayName", item.get("name", "")))
        for item in entries
        if isinstance(item, dict) and item.get("metadata", {}).get("regionType", "Physical") == "Physical"
    ]


async def azure_list_available_sizes(creds: AzureCredentials, location: str) -> list[VmSizeInfo]:
    """Lists the curated sizes that are actually usable in ``location`` right
    now. Uses the Resource SKUs API (not the plain vmSizes list) because
    only this one reports per-location/per-subscription restrictions —
    including live capacity shortages ("Following SKUs have failed for
    Capacity Restrictions...") — that the plain vmSizes list stays silent
    about until you actually try to deploy and it fails."""
    path = f"/subscriptions/{creds.subscription_id}/providers/Microsoft.Compute/skus"
    _, payload = await _request(
        "GET", path, creds, params={"api-version": API_VERSION_SKUS, "$filter": f"location eq '{location}'"}
    )
    entries = (payload or {}).get("value", [])
    by_name: dict[str, dict] = {}
    for item in entries:
        if not isinstance(item, dict) or item.get("resourceType") != "virtualMachines":
            continue
        name = item.get("name")
        if name not in CURATED_SIZES:
            continue
        restrictions = item.get("restrictions") or []
        if any(r.get("type") == "Location" and location in (r.get("values") or []) for r in restrictions):
            continue  # unavailable for this subscription/location right now
        by_name[name] = item

    result = []
    for name in CURATED_SIZES:
        item = by_name.get(name)
        if not item:
            continue
        caps = {c.get("name"): c.get("value") for c in item.get("capabilities", []) if isinstance(c, dict)}
        cores = int(caps.get("vCPUs", 0) or 0)
        memory_gb = float(caps.get("MemoryGB", 0) or 0)
        result.append(VmSizeInfo(name=name, cores=cores, memory_mb=int(memory_gb * 1024)))
    return result


def azure_list_images() -> list[ImageInfo]:
    return list(CURATED_IMAGES)


# --- Networking building blocks (idempotent "ensure"/"create" helpers) ---


async def azure_ensure_resource_group(creds: AzureCredentials, location: str) -> None:
    await _request(
        "PUT", _rg_path(creds), creds,
        json_body={"location": location}, params={"api-version": API_VERSION_RG},
    )


def _vnet_name(location: str) -> str:
    return f"arsicloud-vnet-{location}"


def _vnet_path(creds: AzureCredentials, location: str) -> str:
    return f"{_rg_path(creds)}/providers/Microsoft.Network/virtualNetworks/{_vnet_name(location)}"


async def azure_ensure_network(creds: AzureCredentials, location: str) -> str:
    """Creates the shared VNet+subnet for this (account, location) if it
    doesn't already exist, returning the subnet's resource id."""
    path = _vnet_path(creds, location)
    status, payload = await _request("GET", path, creds, params={"api-version": API_VERSION_NETWORK})
    if status == 200:
        subnets = (payload or {}).get("properties", {}).get("subnets", [])
        if subnets:
            return subnets[0]["id"]

    body = {
        "location": location,
        "properties": {
            "addressSpace": {"addressPrefixes": ["10.10.0.0/16"]},
            "subnets": [{"name": "default", "properties": {"addressPrefix": "10.10.1.0/24"}}],
        },
    }
    await _request("PUT", path, creds, json_body=body, params={"api-version": API_VERSION_NETWORK})
    final = await _poll_provisioning_state(path, creds, params={"api-version": API_VERSION_NETWORK})
    return final["properties"]["subnets"][0]["id"]


def _pip_name(vm_name: str) -> str:
    return f"{vm_name}-pip"


def _pip_path(creds: AzureCredentials, vm_name: str) -> str:
    return f"{_rg_path(creds)}/providers/Microsoft.Network/publicIPAddresses/{_pip_name(vm_name)}"


async def azure_create_public_ip(creds: AzureCredentials, vm_name: str, location: str) -> tuple[str, str | None]:
    path = _pip_path(creds, vm_name)
    body = {
        "location": location,
        "sku": {"name": "Standard"},
        # Static (not Dynamic) so the address is known right after creation,
        # instead of only once a running VM's NIC picks it up.
        "properties": {"publicIPAllocationMethod": "Static"},
    }
    await _request("PUT", path, creds, json_body=body, params={"api-version": API_VERSION_NETWORK})
    final = await _poll_provisioning_state(path, creds, params={"api-version": API_VERSION_NETWORK})
    return final["id"], final.get("properties", {}).get("ipAddress")


def _nsg_name(vm_name: str) -> str:
    return f"{vm_name}-nsg"


def _nsg_path(creds: AzureCredentials, vm_name: str) -> str:
    return f"{_rg_path(creds)}/providers/Microsoft.Network/networkSecurityGroups/{_nsg_name(vm_name)}"


async def azure_create_nsg(creds: AzureCredentials, vm_name: str, location: str) -> str:
    path = _nsg_path(creds, vm_name)
    body = {
        "location": location,
        "properties": {
            "securityRules": [
                {
                    "name": "AllowSSH",
                    "properties": {
                        "priority": 1000, "direction": "Inbound", "access": "Allow", "protocol": "Tcp",
                        "sourcePortRange": "*", "destinationPortRange": "22",
                        "sourceAddressPrefix": "*", "destinationAddressPrefix": "*",
                    },
                },
                {
                    "name": "AllowHTTPS",
                    "properties": {
                        "priority": 1010, "direction": "Inbound", "access": "Allow", "protocol": "Tcp",
                        "sourcePortRange": "*", "destinationPortRange": "443",
                        "sourceAddressPrefix": "*", "destinationAddressPrefix": "*",
                    },
                },
            ]
        },
    }
    await _request("PUT", path, creds, json_body=body, params={"api-version": API_VERSION_NETWORK})
    final = await _poll_provisioning_state(path, creds, params={"api-version": API_VERSION_NETWORK})
    return final["id"]


def _nic_name(vm_name: str) -> str:
    return f"{vm_name}-nic"


def _nic_path(creds: AzureCredentials, vm_name: str) -> str:
    return f"{_rg_path(creds)}/providers/Microsoft.Network/networkInterfaces/{_nic_name(vm_name)}"


async def azure_create_nic(
    creds: AzureCredentials, vm_name: str, location: str, subnet_id: str, pip_id: str, nsg_id: str
) -> str:
    path = _nic_path(creds, vm_name)
    body = {
        "location": location,
        "properties": {
            "ipConfigurations": [
                {
                    "name": "ipconfig1",
                    "properties": {
                        "subnet": {"id": subnet_id},
                        "publicIPAddress": {"id": pip_id},
                        "privateIPAllocationMethod": "Dynamic",
                    },
                }
            ],
            "networkSecurityGroup": {"id": nsg_id},
        },
    }
    await _request("PUT", path, creds, json_body=body, params={"api-version": API_VERSION_NETWORK})
    final = await _poll_provisioning_state(path, creds, params={"api-version": API_VERSION_NETWORK})
    return final["id"]


# --- Virtual machines ---


def _vm_path(creds: AzureCredentials, vm_name: str) -> str:
    return f"{_rg_path(creds)}/providers/Microsoft.Compute/virtualMachines/{vm_name}"


async def azure_create_vm(
    creds: AzureCredentials,
    *,
    location: str,
    vm_size: str,
    image: ImageInfo,
    vm_name: str,
    admin_password: str | None = None,
    ssh_public_key: str | None = None,
    progress: ProgressCallback | None = None,
) -> VMInfo:
    async def tick(step: str) -> None:
        if progress:
            await progress(step)

    await tick("resource_group")
    await azure_ensure_resource_group(creds, location)

    await tick("network")
    subnet_id = await azure_ensure_network(creds, location)

    await tick("public_ip")
    pip_id, pip_address = await azure_create_public_ip(creds, vm_name, location)

    await tick("nsg")
    nsg_id = await azure_create_nsg(creds, vm_name, location)

    await tick("nic")
    nic_id = await azure_create_nic(creds, vm_name, location, subnet_id, pip_id, nsg_id)

    await tick("vm")
    os_profile: dict = {"computerName": vm_name, "adminUsername": ADMIN_USERNAME}
    if ssh_public_key:
        os_profile["linuxConfiguration"] = {
            "disablePasswordAuthentication": True,
            "ssh": {
                "publicKeys": [
                    {"path": f"/home/{ADMIN_USERNAME}/.ssh/authorized_keys", "keyData": ssh_public_key}
                ]
            },
        }
    else:
        os_profile["adminPassword"] = admin_password

    body = {
        "location": location,
        "properties": {
            "hardwareProfile": {"vmSize": vm_size},
            "storageProfile": {
                "imageReference": {
                    "publisher": image.publisher,
                    "offer": image.offer,
                    "sku": image.sku,
                    "version": image.version,
                },
                "osDisk": {"createOption": "FromImage", "managedDisk": {"storageAccountType": "Standard_LRS"}},
            },
            "osProfile": os_profile,
            "networkProfile": {"networkInterfaces": [{"id": nic_id}]},
        },
    }
    path = _vm_path(creds, vm_name)
    await _request("PUT", path, creds, json_body=body, params={"api-version": API_VERSION_COMPUTE})
    await _poll_provisioning_state(path, creds, params={"api-version": API_VERSION_COMPUTE})

    return VMInfo(
        name=vm_name,
        location=location,
        vm_size=vm_size,
        power_state="running",
        public_ip=pip_address,
        admin_username=ADMIN_USERNAME,
        admin_password=None if ssh_public_key else admin_password,
    )


def _power_state_from_instance_view(instance_view: dict) -> str:
    for status in instance_view.get("statuses", []):
        code = status.get("code", "")
        if code.startswith("PowerState/"):
            return code.split("/", 1)[1]
    return "unknown"


async def azure_list_vms(creds: AzureCredentials) -> list[VMInfo]:
    path = f"{_rg_path(creds)}/providers/Microsoft.Compute/virtualMachines"
    status, payload = await _request("GET", path, creds, params={"api-version": API_VERSION_COMPUTE})
    if status == 404:
        return []
    entries = (payload or {}).get("value", [])
    result = []
    for item in entries:
        name = item.get("name", "")
        try:
            result.append(await azure_get_vm(creds, name))
        except AzureAPIError:
            continue
    return result


async def azure_get_vm(creds: AzureCredentials, vm_name: str) -> VMInfo:
    path = _vm_path(creds, vm_name)
    status, payload = await _request(
        "GET", path, creds, params={"api-version": API_VERSION_COMPUTE, "$expand": "instanceView"}
    )
    if status == 404:
        raise AzureAPIError("not_found")
    payload = payload or {}
    props = payload.get("properties", {})
    power_state = _power_state_from_instance_view(props.get("instanceView", {}))

    public_ip = None
    pip_status, pip_payload = await _request(
        "GET", _pip_path(creds, vm_name), creds, params={"api-version": API_VERSION_NETWORK}
    )
    if pip_status == 200:
        public_ip = (pip_payload or {}).get("properties", {}).get("ipAddress")

    return VMInfo(
        name=vm_name,
        location=payload.get("location", ""),
        vm_size=props.get("hardwareProfile", {}).get("vmSize", ""),
        power_state=power_state,
        public_ip=public_ip,
        admin_username=props.get("osProfile", {}).get("adminUsername", ADMIN_USERNAME),
    )


async def _poll_power_state(creds: AzureCredentials, vm_name: str, target: str) -> None:
    elapsed = 0
    while True:
        info = await azure_get_vm(creds, vm_name)
        if info.power_state == target:
            return
        if elapsed >= POLL_TIMEOUT:
            raise AzureAPIError("timeout")
        await asyncio.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL


async def _do_power_action(creds: AzureCredentials, vm_name: str, action: str, target_state: str) -> None:
    path = f"{_vm_path(creds, vm_name)}/{action}"
    await _request("POST", path, creds, params={"api-version": API_VERSION_COMPUTE})
    await _poll_power_state(creds, vm_name, target_state)


async def azure_start_vm(creds: AzureCredentials, vm_name: str) -> None:
    await _do_power_action(creds, vm_name, "start", "running")


async def azure_stop_vm(creds: AzureCredentials, vm_name: str) -> None:
    # "deallocate" (not just "powerOff") releases the compute allocation so
    # the VM stops billing for compute — the same thing Azure's own portal
    # Stop button does, and the closest match to what "stop" means economically.
    await _do_power_action(creds, vm_name, "deallocate", "deallocated")


async def azure_restart_vm(creds: AzureCredentials, vm_name: str) -> None:
    await _do_power_action(creds, vm_name, "restart", "running")


async def azure_delete_vm(creds: AzureCredentials, vm_name: str) -> None:
    await _request("DELETE", _vm_path(creds, vm_name), creds, params={"api-version": API_VERSION_COMPUTE})
    await _poll_deleted(_vm_path(creds, vm_name), creds, params={"api-version": API_VERSION_COMPUTE})

    # Best-effort cleanup of the VM's own NIC/public IP/NSG — the shared
    # VNet/resource group stay, since other VMs may still use them.
    for path, api_version in (
        (_nic_path(creds, vm_name), API_VERSION_NETWORK),
        (_pip_path(creds, vm_name), API_VERSION_NETWORK),
        (_nsg_path(creds, vm_name), API_VERSION_NETWORK),
    ):
        try:
            await _request("DELETE", path, creds, params={"api-version": api_version})
            await _poll_deleted(path, creds, params={"api-version": api_version})
        except AzureAPIError:
            pass
