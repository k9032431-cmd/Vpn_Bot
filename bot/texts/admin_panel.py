from __future__ import annotations

from .premium_emoji import e
from .translations import t


def admin_panel_text(lang: str) -> str:
    return t(lang, "admin_panel_header", icon=e("warning", "🛡"))


def admin_stats_text(lang: str, total: int, new_24h: int, new_7d: int) -> str:
    return t(lang, "admin_stats", icon=e("warning", "📊"), total=total, new_24h=new_24h, new_7d=new_7d)
