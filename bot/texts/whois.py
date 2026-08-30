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


def _code(value: str | None) -> str:
    # Monospace for literal server/domain identifiers (IPs, hostnames,
    # nameservers, DNS records) — everything else stays plain text.
    return f"<code>{html.escape(value)}</code>" if value else "—"


def _tree(lang: str, items: list[_TreeItem]) -> str:
    # Collapses consecutive/leading/trailing blanks, then renders the
    # box-drawing tree — the last real row closes it with "└" instead of "├".
    # Plain proportional text with bold labels (matching the reference
    # bot's look), a blank line under the header, and <code> only around
    # literal server/domain values.
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
    lines = [f"┌ <b>{_BOT_NAME}</b> 🌐", "│"]
    for i, item in enumerate(cleaned):
        if item is None:
            lines.append("│")
        else:
            label_key, value = item
            prefix = "└" if i == last_idx else "├"
            lines.append(f"{prefix} <b>{t(lang, label_key)}</b>: {value}")
    return "\n".join(lines)


def _ip_fields(lang: str, info) -> list[_TreeItem]:
    # The full field set for an IP — used both for a standalone IP lookup
    # and for the resolved-IP block embedded in a domain result.
    city = ", ".join(filter(None, [info.city, info.region])) or "—"
    country = f"{info.country_flag} {info.country}".strip() if info.country else "—"
    fields: list[_TreeItem] = [
        ("whois_l_ip", _code(info.ip)),
        ("whois_l_host", _code(info.host)),
        ("whois_l_country", html.escape(country)),
        ("whois_l_city", html.escape(city)),
        ("whois_l_provider", f"{html.escape(info.isp or '—')} ({_code(info.asn)})"),
    ]
    if info.org:
        fields.append(("whois_l_org", html.escape(info.org)))
    fields.append(("whois_l_timezone", html.escape(info.timezone or "—")))
    fields.append(None)
    fields.extend(
        [
            ("whois_l_proxy", _yn(lang, info.is_proxy)),
            ("whois_l_vpn", _yn(lang, info.is_vpn)),
            ("whois_l_tor", _yn(lang, info.is_tor)),
            ("whois_l_hosting", _yn(lang, info.is_hosting)),
            ("whois_l_cloudflare", _yn(lang, info.is_cloudflare)),
        ]
    )
    return fields


def ip_result_text(lang: str, info) -> str:
    return _tree(lang, _ip_fields(lang, info))


def domain_result_text(lang: str, info) -> str:
    nameservers = ", ".join(_code(ns) for ns in info.nameservers[:8]) if info.nameservers else "—"
    status = ", ".join(html.escape(s) for s in info.status[:6]) if info.status else "—"
    a_records = ", ".join(_code(a) for a in info.a_records[:6]) if info.a_records else "—"
    mx_records = ", ".join(_code(m) for m in info.mx_records[:6]) if info.mx_records else "—"
    txt_records = ", ".join(_code(x[:60]) for x in info.txt_records[:3]) if info.txt_records else "—"

    items: list[_TreeItem] = [
        ("whois_l_domain", _code(info.domain)),
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
