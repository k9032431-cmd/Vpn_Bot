from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bot.config import config


class UserStatsStore:
    """Tracks the first time this bot ever saw each user, for the admin
    panel's "📊 Статистика" screen. Fed from LanguageMiddleware (see
    bot/middlewares/language.py), which already runs on every single
    update for every user -- recording a user there, rather than from
    individual handlers, means every interaction counts a user as seen,
    not just /start or a handful of specific actions."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._data: dict[str, str] | None = None  # user_id (str) -> ISO first-seen timestamp (UTC)

    async def _load(self) -> dict[str, str]:
        if self._data is None:
            async with self._lock:
                if self._data is None:
                    try:
                        self._data = json.loads(self._path.read_text(encoding="utf-8"))
                    except (FileNotFoundError, json.JSONDecodeError, OSError):
                        self._data = {}
        return self._data

    async def record_seen(self, user_id: int) -> None:
        data = await self._load()
        key = str(user_id)
        if key in data:
            return  # already known -- skip the disk write on every single update
        async with self._lock:
            if key in data:
                return
            data[key] = datetime.now(timezone.utc).isoformat()
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def total_count(self) -> int:
        data = await self._load()
        return len(data)

    async def count_new_within(self, hours: int) -> int:
        data = await self._load()
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        count = 0
        for iso in data.values():
            try:
                seen = datetime.fromisoformat(iso)
            except ValueError:
                continue
            if seen >= cutoff:
                count += 1
        return count


user_stats = UserStatsStore(config.data_dir / "user_stats.json")
