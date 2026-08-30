from __future__ import annotations

import html

from .premium_emoji import e
from .translations import t

_WHOIS_ERR_KEYS = {
    "connect_failed": "whois_err_connect",
    "not_found": "whois_err_not_found",
    "bad_response": "whois_err_bad_response",
}

_BOT_NAME = "Arsi WhoIs Bot"

# A field row, or None for a blank separator line between groups of fields.
_TreeItem = tuple[str, str] | None


def prompt_text(lang: str) -> str:
    return t(lang, "whois_prompt", icon=e("whois", "🌐"))


def cancelled_text(lang: str) -> str:
    return t(lang, "whois_cancelled")


def invalid_input_text(lang: str) -> str:
    return t(lang, "whois_invalid")


def error_text(lang: str, reason: str) -> str:
    key = _WHOIS_ERR_KEYS.get(reason, "whois_err_bad_response")
    return t(lang, "whois_error", icon=e("error", "❌"), reason=t(lang, key))


def _yn(lang: str, value: bool) -> str:
    return t(lang, "whois_yes") if value else t(lang, "whois_no")


def _tree(lang: str, items: list[_TreeItem]) -> str:
    # Collapses consecutive/leading/trailing blanks, then renders the
    # box-drawing tree — the last real row closes it with "└" instead of "├".
    cleaned: list[_TreeItem] = []
    for item in items:
        if item is None:
            if cleaned and cleaned[-1] is not None:
                cleaned.append(None)
        else:
            cleaned.append(item)
    while cleaned and cleaned[-1] is None:
        cleaned.pop()

    last_idx = len(cleaned) - 1
    lines = [f"┌ {_BOT_NAME} 🌐"]
    for i, item in enumerate(cleaned):
        if item is None:
            lines.append("│")
        else:
            label_key, value = item
            prefix = "└" if i == last_idx else "├"
            lines.append(f"{prefix} {t(lang, label_key)}: {value}")
    return "<code>" + "\n".join(lines) + "</code>"


def _ip_fields(lang: str, info) -> list[_TreeItem]:
    country = f"{info.country_flag} {info.country}".strip() if info.country else "—"
    provider = f"{html.escape(info.isp or '—')} ({html.escape(info.asn or '—')})"
    return [
        ("whois_l_ip", html.escape(info.ip)),
        ("whois_l_country", html.escape(country)),
        ("whois_l_provider", provider),
        ("whois_l_cloudflare", _yn(lang, info.is_cloudflare)),
    ]


def ip_result_text(lang: str, info) -> str:
    city = ", ".join(filter(None, [info.city, info.region])) or "—"
    items: list[_TreeItem] = [
        ("whois_l_ip", html.escape(info.ip)),
        ("whois_l_host", html.escape(info.host or "—")),
        ("whois_l_country", html.escape(f"{info.country_flag} {info.country}".strip() if info.country else "—")),
        ("whois_l_city", html.escape(city)),
        ("whois_l_provider", f"{html.escape(info.isp or '—')} ({html.escape(info.asn or '—')})"),
        ("whois_l_timezone", html.escape(info.timezone or "—")),
        None,
        ("whois_l_proxy", _yn(lang, info.is_proxy)),
        ("whois_l_vpn", _yn(lang, info.is_vpn)),
        ("whois_l_tor", _yn(lang, info.is_tor)),
        ("whois_l_hosting", _yn(lang, info.is_hosting)),
        ("whois_l_cloudflare", _yn(lang, info.is_cloudflare)),
    ]
    return _tree(lang, items)


def domain_result_text(lang: str, info) -> str:
    nameservers = ", ".join(html.escape(ns) for ns in info.nameservers[:8]) if info.nameservers else "—"
    status = ", ".join(html.escape(s) for s in info.status[:6]) if info.status else "—"
    a_records = ", ".join(html.escape(a) for a in info.a_records[:6]) if info.a_records else "—"
    mx_records = ", ".join(html.escape(m) for m in info.mx_records[:6]) if info.mx_records else "—"
    txt_records = (
        ", ".join(html.escape(x[:60]) for x in info.txt_records[:3]) if info.txt_records else "—"
    )

    items: list[_TreeItem] = [
        ("whois_l_domain", html.escape(info.domain)),
        ("whois_l_registrar", html.escape(info.registrar or "—")),
        ("whois_l_created", html.escape(info.created or "—")),
        ("whois_l_expires", html.escape(info.expires or "—")),
        ("whois_l_updated", html.escape(info.updated or "—")),
        ("whois_l_status", status),
        ("whois_l_cloudflare_ns", _yn(lang, info.is_cloudflare_ns)),
        ("whois_l_nameservers", nameservers),
        None,
        ("whois_l_dns_a", a_records),
        ("whois_l_dns_mx", mx_records),
        ("whois_l_dns_txt", txt_records),
    ]
    if info.resolved_ip_info is not None:
        items.append(None)
        items.extend(_ip_fields(lang, info.resolved_ip_info))
    return _tree(lang, items)
