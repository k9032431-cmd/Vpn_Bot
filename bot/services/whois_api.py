from __future__ import annotations

import asyncio
import ipaddress
import re
import socket
from dataclasses import dataclass

import aiohttp

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=12)

# Public data sources — module-level so they're easy to point at a
# self-hosted mirror (or a fake server in tests) without touching the
# lookup logic itself.
IPWHOIS_URL_TEMPLATE = "https://ipwho.is/{ip}"
RDAP_URL_TEMPLATE = "https://rdap.org/domain/{domain}"

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
    asn: str | None
    timezone: str | None
    is_proxy: bool
    is_vpn: bool
    is_tor: bool
    is_hosting: bool
    is_cloudflare: bool
    source: str


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
    resolved_ip: str | None
    resolved_ip_country: str | None
    resolved_ip_isp: str | None
    source: str


async def _reverse_dns(ip: str) -> str | None:
    loop = asyncio.get_running_loop()
    try:
        hostname, _, _ = await asyncio.wait_for(
            loop.run_in_executor(None, socket.gethostbyaddr, ip), timeout=3
        )
        return hostname
    except Exception:
        return None


async def _resolve_ip(domain: str) -> str | None:
    loop = asyncio.get_running_loop()
    try:
        infos = await asyncio.wait_for(
            loop.getaddrinfo(domain, None, family=socket.AF_INET), timeout=5
        )
        return infos[0][4][0] if infos else None
    except Exception:
        return None


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
    isp = connection.get("isp") or connection.get("org")
    is_cloudflare = (asn_label in _CLOUDFLARE_ASN) or bool(isp and "cloudflare" in isp.lower())

    host = await _reverse_dns(ip)

    return IPInfo(
        ip=str(payload.get("ip", ip)),
        host=host,
        country=payload.get("country"),
        country_flag=str(flag.get("emoji") or ""),
        region=payload.get("region"),
        city=payload.get("city"),
        isp=isp,
        asn=asn_label,
        timezone=(payload.get("timezone") or {}).get("id"),
        is_proxy=bool(security.get("proxy")),
        is_vpn=bool(security.get("vpn")),
        is_tor=bool(security.get("tor")),
        is_hosting=bool(security.get("hosting")),
        is_cloudflare=is_cloudflare,
        source="ipwho.is",
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


async def lookup_domain(domain: str) -> DomainInfo:
    async with aiohttp.ClientSession(timeout=REQUEST_TIMEOUT, trust_env=True) as session:
        try:
            async with session.get(RDAP_URL_TEMPLATE.format(domain=domain)) as resp:
                status = resp.status
                try:
                    payload = await resp.json(content_type=None)
                except (aiohttp.ContentTypeError, ValueError):
                    payload = None
        except (aiohttp.ClientError, asyncio.TimeoutError, TimeoutError) as exc:
            raise WhoisAPIError("connect_failed") from exc

    if status == 404:
        raise WhoisAPIError("not_found")
    if status >= 400 or not isinstance(payload, dict):
        raise WhoisAPIError("bad_response")

    events = payload.get("events") or []
    nameservers = [
        str(ns.get("ldhName"))
        for ns in (payload.get("nameservers") or [])
        if isinstance(ns, dict) and ns.get("ldhName")
    ]
    registrar = None
    for entity in payload.get("entities") or []:
        if isinstance(entity, dict) and "registrar" in (entity.get("roles") or []):
            registrar = _vcard_fn(entity.get("vcardArray")) or entity.get("handle")
            break

    resolved_ip = await _resolve_ip(domain)
    resolved_ip_country = None
    resolved_ip_isp = None
    if resolved_ip:
        try:
            ip_info = await lookup_ip(resolved_ip)
            resolved_ip_country = ip_info.country
            resolved_ip_isp = ip_info.isp
        except WhoisAPIError:
            pass

    return DomainInfo(
        domain=str(payload.get("ldhName", domain)).lower(),
        registrar=registrar,
        created=_rdap_event(events, "registration"),
        expires=_rdap_event(events, "expiration"),
        updated=_rdap_event(events, "last changed"),
        nameservers=nameservers,
        status=[str(s) for s in (payload.get("status") or [])],
        is_cloudflare_ns=any("cloudflare" in ns.lower() for ns in nameservers),
        resolved_ip=resolved_ip,
        resolved_ip_country=resolved_ip_country,
        resolved_ip_isp=resolved_ip_isp,
        source="RDAP",
    )
