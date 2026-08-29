from __future__ import annotations

import asyncio
import json
from pathlib import Path

from bot.config import config


class UserPrefsStore:
    """Tiny JSON-backed store for per-user preferences (currently just the
    interface language). Kept on disk under Config.data_dir so a choice
    survives bot restarts and redeploys, as long as that directory is
    volume-mounted (see docker-compose.yml)."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._data: dict[str, str] | None = None

    async def _load(self) -> dict[str, str]:
        if self._data is None:
            async with self._lock:
                if self._data is None:
                    try:
                        self._data = json.loads(self._path.read_text(encoding="utf-8"))
                    except (FileNotFoundError, json.JSONDecodeError, OSError):
                        self._data = {}
        return self._data

    async def get_language(self, user_id: int) -> str | None:
        data = await self._load()
        return data.get(str(user_id))

    async def set_language(self, user_id: int, lang: str) -> None:
        data = await self._load()
        async with self._lock:
            data[str(user_id)] = lang
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )


user_prefs = UserPrefsStore(config.data_dir / "user_languages.json")
