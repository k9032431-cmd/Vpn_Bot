from __future__ import annotations

import json
from pathlib import Path

from bot.config import config

_PATH: Path = config.data_dir / "premium_emoji_overrides.json"


def _load() -> dict[str, str]:
    try:
        return json.loads(_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


# Read synchronously, once, at import. e()/button_icon() in
# bot/texts/premium_emoji.py are called from plain (non-async) code spread
# across every texts/*.py and keyboards/*.py module, so this can't be the
# usual lazy-async-load store the other *_store.py files use -- it has to
# be a synchronously readable in-memory dict instead. A write (only from
# the admin emoji-settings screen, a rare, one-off action) updates this
# same dict and re-persists it right away, so a change takes effect
# immediately, without a bot restart.
_overrides: dict[str, str] = _load()


def get(key: str) -> str | None:
    return _overrides.get(key) or None


def all_overrides() -> dict[str, str]:
    return dict(_overrides)


def set_override(key: str, custom_emoji_id: str) -> None:
    _overrides[key] = custom_emoji_id
    _save()


def clear_override(key: str) -> None:
    _overrides.pop(key, None)
    _save()


def _save() -> None:
    _PATH.parent.mkdir(parents=True, exist_ok=True)
    _PATH.write_text(json.dumps(_overrides, ensure_ascii=False, indent=2), encoding="utf-8")
