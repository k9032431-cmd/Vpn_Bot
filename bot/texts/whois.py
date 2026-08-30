from __future__ import annotations

import html

from .premium_emoji import e
from .translations import t

_WHOIS_ERR_KEYS = {
    "connect_failed": "whois_err_connect",
    "not_found": "whois_err_not_found",
    "bad_response": "whois_err_bad_response",
}


def prompt_text(lang: str) -> str:
    return t(lang, "whois_prompt", icon=e("whois", "🌐"))


def cancelled_text(lang: str) -> str:
    return t(lang, "whois_cancelled")


def invalid_input_text(lang: str) -> str:
    return t(lang, "whois_invalid")


def looking_up_text(lang: str) -> str:
    return t(lang, "whois_looking_up")


def error_text(lang: str, reason: str) -> str:
    key = _WHOIS_ERR_KEYS.get(reason, "whois_err_bad_response")
    return t(lang, "whois_error", icon=e("error", "❌"), reason=t(lang, key))


def _yn(lang: str, value: bool) -> str:
    return t(lang, "whois_yes") if value else t(lang, "whois_no")


def ip_result_text(lang: str, query: str, info) -> str:
    city = ", ".join(filter(None, [info.city, info.region])) or "—"
    country = f"{info.country_flag} {info.country}".strip() if info.country else "—"
    return t(
        lang,
        "whois_ip_result",
        query=html.escape(query),
        ip=html.escape(info.ip),
        host=html.escape(info.host or "—"),
        country=html.escape(country),
        city=html.escape(city),
        isp=html.escape(info.isp or "—"),
        asn=html.escape(info.asn or "—"),
        timezone=html.escape(info.timezone or "—"),
        proxy=_yn(lang, info.is_proxy),
        vpn=_yn(lang, info.is_vpn),
        tor=_yn(lang, info.is_tor),
        hosting=_yn(lang, info.is_hosting),
        cloudflare=_yn(lang, info.is_cloudflare),
        source=html.escape(info.source),
    )


def domain_result_text(lang: str, query: str, info) -> str:
    if info.nameservers:
        ns = "\n".join(f"├ <code>{html.escape(name)}</code>" for name in info.nameservers[:6])
    else:
        ns = "├ —"
    status = ", ".join(info.status) if info.status else "—"
    ip_extra = ", ".join(filter(None, [info.resolved_ip_country, info.resolved_ip_isp]))
    return t(
        lang,
        "whois_domain_result",
        query=html.escape(query),
        domain=html.escape(info.domain),
        registrar=html.escape(info.registrar or "—"),
        created=html.escape(info.created or "—"),
        expires=html.escape(info.expires or "—"),
        updated=html.escape(info.updated or "—"),
        status=html.escape(status),
        nameservers=ns,
        cloudflare=_yn(lang, info.is_cloudflare_ns),
        resolved_ip=html.escape(info.resolved_ip or "—"),
        ip_extra=html.escape(f" ({ip_extra})" if ip_extra else ""),
        source=html.escape(info.source),
    )
