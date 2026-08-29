from __future__ import annotations

import asyncio
import json
from pathlib import Path

from bot.config import config


class PanelStore:
    """Tiny JSON-backed store for each user's connected panel (type, URL,
    admin login/password). One connection per user; connecting a new panel
    replaces the previous one.

    The stored password lets the bot re-authenticate on demand (panel API
    tokens/sessions expire), matching the same "admin sees everything"
    trust model already used for Node install notifications.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._data: dict[str, dict] | None = None

    async def _load(self) -> dict[str, dict]:
        if self._data is None:
            async with self._lock:
                if self._data is None:
                    try:
                        self._data = json.loads(self._path.read_text(encoding="utf-8"))
                    except (FileNotFoundError, json.JSONDecodeError, OSError):
                        self._data = {}
        return self._data

    async def get(self, user_id: int) -> dict | None:
        data = await self._load()
        return data.get(str(user_id))

    async def set(self, user_id: int, panel_type: str, url: str, username: str, password: str) -> None:
        data = await self._load()
        async with self._lock:
            data[str(user_id)] = {
                "type": panel_type,
                "url": url,
                "username": username,
                "password": password,
            }
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def remove(self, user_id: int) -> None:
        data = await self._load()
        async with self._lock:
            if str(user_id) in data:
                del data[str(user_id)]
                self._path.parent.mkdir(parents=True, exist_ok=True)
                self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


panel_store = PanelStore(config.data_dir / "panel_connections.json")
