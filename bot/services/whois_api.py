from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from dataclasses import dataclass, field

import aiohttp
import dns.asyncresolver

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=12)
DNS_TIMEOUT = 4
RAW_WHOIS_TIMEOUT = 8
RAW_WHOIS_PORT = 43

# Public data sources — module-level so they're easy to point at a
# self-hosted mirror (or a fake server in tests) without touching the
# lookup logic itself.
IPWHOIS_URL_TEMPLATE = "https://ipwho.is/{ip}"
RDAP_URL_TEMPLATE = "https://rdap.org/domain/{domain}"
RDAP_IP_URL_TEMPLATE = "https://rdap.org/ip/{ip}"
IANA_WHOIS_SERVER = "whois.iana.org"

# Cloudflare's own ASNs — used to flag an IP as Cloudflare even when the
# ISP/org name from the geo API doesn't spell it out.
_CLOUDFLARE_ASN = {"AS13335", "AS209242", "AS132892"}

_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$")


class WhoisAPIError(Exception):
    """str(exc) is one of a small set of reason codes — the texts layer
    translates these into a human message, so it's always safe to show."""


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


def is_domain(value: str) -> bool:
    if is_ip(value):
        return False
    return bool(_DOMAIN_RE.match(value))


@dataclass
class IPInfo:
    ip: str
    host: str | None
    country: str | None
    country_flag: str
    region: str | None
    city: str | None
    isp: str | None
    org: str | None
    network_name: str | None
    asn: str | None
    timezone: str | None
    is_proxy: bool
    is_vpn: bool
    is_tor: bool
    is_hosting: bool
    is_cloudflare: bool


@dataclass
class DomainInfo:
    domain: str
    registrar: str | None
    created: str | None
    expires: str | None
    updated: str | None
    nameservers: list[str]
    status: list[str]
    is_cloudflare_ns: bool
    a_records: list[str] = field(default_factory=list)
    mx_records: list[str] = field(default_factory=list)
    txt_records: list[str] = field(default_factory=list)
    resolved_ip_info: IPInfo | None = None


async def _reverse_dns(ip: str) -> str | None:
    loop = asyncio.get_running_loop()
    try:
        hostname, _, _ = await asyncio.wait_for(
            loop.run_in_executor(None, socket.gethostbyaddr, ip), timeout=3
        )
        return hostname
    except Exception:
        return None


async def _dns_records(domain: str, record_type: str) -> list[str]:
    resolver = dns.asyncresolver.Resolver()
    resolver.timeout = DNS_TIMEOUT
    resolver.lifetime = DNS_TIMEOUT
    try:
        answer = await resolver.resolve(domain, record_type)
    except Exception:
        return []

    values: list[str] = []
    for rdata in answer:
        if record_type == "TXT":
            text = b"".join(rdata.strings).decode("utf-8", errors="replace")
            values.append(text)
        elif record_type == "MX":
            # A null MX ("." exchange, RFC 7505) means "accepts no mail" —
            # not a real mail server, so it's not worth listing.
            exchange = str(rdata.exchange).rstrip(".")
            if exchange:
                values.append(f"{rdata.preference} {exchange}")
        else:
            values.append(str(rdata).rstrip("."))
    return values


async def _ip_rdap_lookup(ip: str) -> dict | None:
    # ipwho.is's isp/org fields come from a commercial geo-IP database and
    # can be generic or stale for smaller resellers. RDAP queries the
    # actual regional registry (RIPE/ARIN/APNIC/...) live, so its network
    # "name" is the authoritative, registry-assigned label for that block —
    # often closer to the real operator's brand than a geo-IP vendor guess.
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT, trust_env=True) as session:
        try:
            async with session.get(RDAP_IP_URL_TEMPLATE.format(ip=ip)) as resp:
                if resp.status >= 400:
                    return None
                try:
                    payload = await resp.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError):
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError):
            return None
    return payload if isinstance(payload, dict) else None


async def lookup_ip(ip: str) -> IPInfo:
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT, trust_env=True) as session:
        try:
            async with session.get(IPWHOIS_URL_TEMPLATE.format(ip=ip)) as resp:
                payload = await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError) as exc:
            raise WhoisAPIError("connect_failed") from exc

    if not isinstance(payload, dict) or payload.get("success") is False:
        raise WhoisAPIError("not_found")

    connection = payload.get("connection") or {}
    security = payload.get("security") or {}
    flag = payload.get("flag") or {}
    asn_raw = connection.get("asn")
    asn_label = f"AS{asn_raw}" if asn_raw else None
    isp = connection.get("isp")
    org = connection.get("org")
    provider = isp or org
    # ipwho.is separates the network operator (isp) from the registered
    # organization for that IP block (org) — they often differ (e.g. a
    # reseller's own name vs. the actual hosting company), so both are
    # worth showing whenever they're not the same thing.
    extra_org = org if org and org != provider else None
    is_cloudflare = (asn_label in _CLOUDFLARE_ASN) or bool(
        (provider and "cloudflare" in provider.lower()) or (org and "cloudflare" in org.lower())
    )

    host = await _reverse_dns(ip)

    network_name = None
    rdap_payload = await _ip_rdap_lookup(ip)
    if rdap_payload:
        name = rdap_payload.get("name")
        if isinstance(name, str) and name:
            network_name = name

    return IPInfo(
        ip=str(payload.get("ip", ip)),
        host=host,
        country=payload.get("country"),
        country_flag=str(flag.get("emoji") or ""),
        region=payload.get("region"),
        city=payload.get("city"),
        isp=provider,
        org=extra_org,
        network_name=network_name,
        asn=asn_label,
        timezone=(payload.get("timezone") or {}).get("id"),
        is_proxy=bool(security.get("proxy")),
        is_vpn=bool(security.get("vpn")),
        is_tor=bool(security.get("tor")),
        is_hosting=bool(security.get("hosting")),
        is_cloudflare=is_cloudflare,
    )


def _vcard_fn(vcard_array: object) -> str | None:
    try:
        for entry in vcard_array[1]:
            if isinstance(entry, list) and entry and entry[0] == "fn":
                return str(entry[3])
    except (IndexError, TypeError, KeyError):
        pass
    return None


def _rdap_event(events: list, action: str) -> str | None:
    for event in events:
        if isinstance(event, dict) and event.get("eventAction") == action:
            date = event.get("eventDate")
            if date:
                return str(date)[:10]
    return None


async def _rdap_lookup(domain: str) -> dict | None:
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT, trust_env=True) as session:
        try:
            async with session.get(RDAP_URL_TEMPLATE.format(domain=domain)) as resp:
                if resp.status >= 400:
                    return None
                try:
                    payload = await resp.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError):
                    return None
        except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError):
            return None
    return payload if isinstance(payload, dict) else None


# --- Classic WHOIS protocol (port 43) fallback — RDAP isn't run by every
# ccTLD registry (notably .ru and several others), so for those domains this
# is the only way to get registrar/date/nameserver data at all. ---

_WHOIS_PATTERNS = {
    "registrar": (r"(?im)^(?:Registrar|Sponsoring Registrar):\s*(.+)$",),
    "created": (r"(?im)^(?:Creation Date|created|Registered on|Domain Registration Date):\s*(.+)$",),
    "expires": (
        r"(?im)^(?:Registry Expiry Date|paid-till|Registrar Registration Expiration Date"
        r"|Expiry [Dd]ate|Expiration Date):\s*(.+)$",
    ),
    "updated": (r"(?im)^(?:Updated Date|Last updated|changed):\s*(.+)$",),
}


def _first_match(patterns: tuple[str, ...], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def _parse_raw_whois(text: str) -> dict:
    created = _first_match(_WHOIS_PATTERNS["created"], text)
    expires = _first_match(_WHOIS_PATTERNS["expires"], text)
    updated = _first_match(_WHOIS_PATTERNS["updated"], text)

    status: list[str] = []
    for line in re.findall(r"(?im)^(?:Domain Status|state):\s*(.+)$", text):
        for part in line.split(","):
            token = part.strip().split(" ")[0] if part.strip() else ""
            if token and token not in status:
                status.append(token)

    nameservers: list[str] = []
    for ns in re.findall(r"(?im)^(?:Name Server|nserver):\s*(\S+)", text):
        ns = ns.strip().rstrip(".")
        if ns and ns not in nameservers:
            nameservers.append(ns)

    return {
        "registrar": _first_match(_WHOIS_PATTERNS["registrar"], text),
        "created": created[:10] if created else None,
        "expires": expires[:10] if expires else None,
        "updated": updated[:10] if updated else None,
        "status": status,
        "nameservers": nameservers,
    }


async def _whois_query(server: str, query: str) -> str | None:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(server, RAW_WHOIS_PORT), timeout=RAW_WHOIS_TIMEOUT
        )
    except (OSError, asyncio.TimeoutError):
        return None
    try:
        writer.write((query + "\r\n").encode())
        await writer.drain()
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = await asyncio.wait_for(reader.read(4096), timeout=RAW_WHOIS_TIMEOUT)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > 200_000:
                break
        return b"".join(chunks).decode("utf-8", errors="replace")
    except (OSError, asyncio.TimeoutError):
        return None
    finally:
        writer.close()


async def _raw_whois_lookup(domain: str) -> dict | None:
    tld = domain.rsplit(".", 1)[-1].lower()
    iana_text = await _whois_query(IANA_WHOIS_SERVER, tld)
    if not iana_text:
        return None
    server_match = re.search(r"(?im)^whois:\s*(\S+)", iana_text)
    if not server_match:
        return None

    text = await _whois_query(server_match.group(1), domain)
    if not text:
        return None

    # A handful of registries (classic gTLDs via their registrar) point to
    # a more specific server that holds the actual record.
    referral = re.search(r"(?im)^(?:ReferralServer|Registrar Whois Server):\s*(?:whois://)?(\S+)", text)
    if referral:
        deeper = await _whois_query(referral.group(1).rstrip("/"), domain)
        if deeper:
            text = deeper

    parsed = _parse_raw_whois(text)
    return parsed if any(parsed.values()) else None


async def lookup_domain(domain: str) -> DomainInfo:
    payload = await _rdap_lookup(domain)

    registrar = created = expires = updated = None
    nameservers: list[str] = []
    status: list[str] = []
    domain_label = domain.lower()

    if payload is not None:
        events = payload.get("events") or []
        nameservers = [
            str(ns.get("ldhName"))
            for ns in (payload.get("nameservers") or [])
            if isinstance(ns, dict) and ns.get("ldhName")
        ]
        for entity in payload.get("entities") or []:
            if isinstance(entity, dict) and "registrar" in (entity.get("roles") or []):
                registrar = _vcard_fn(entity.get("vcardArray")) or entity.get("handle")
                break
        created = _rdap_event(events, "registration")
        expires = _rdap_event(events, "expiration")
        updated = _rdap_event(events, "last changed")
        status = [str(s) for s in (payload.get("status") or [])]
        domain_label = str(payload.get("ldhName", domain)).lower()

    # RDAP coverage is spotty for many ccTLD registries (.ru among them) —
    # when it left the key fields empty, fall back to the classic WHOIS
    # protocol (port 43) via an IANA referral to the right server.
    if not registrar and not created:
        raw = await _raw_whois_lookup(domain)
        if raw:
            registrar = registrar or raw["registrar"]
            created = created or raw["created"]
            expires = expires or raw["expires"]
            updated = updated or raw["updated"]
            status = status or raw["status"]
            nameservers = nameservers or raw["nameservers"]

    a_records = await _dns_records(domain, "A")
    mx_records = await _dns_records(domain, "MX")
    txt_records = await _dns_records(domain, "TXT")

    resolved_ip_info = None
    if a_records:
        try:
            resolved_ip_info = await lookup_ip(a_records[0])
        except WhoisAPIError:
            pass

    if not registrar and not nameservers and not a_records and not created:
        raise WhoisAPIError("not_found")

    return DomainInfo(
        domain=domain_label,
        registrar=registrar,
        created=created,
        expires=expires,
        updated=updated,
        nameservers=nameservers,
        status=status,
        is_cloudflare_ns=any("cloudflare" in ns.lower() for ns in nameservers),
        a_records=a_records,
        mx_records=mx_records,
        txt_records=txt_records,
        resolved_ip_info=resolved_ip_info,
    )
