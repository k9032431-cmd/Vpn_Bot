from __future__ import annotations

import asyncio
import json
import secrets
from pathlib import Path

from bot.config import config


class PanelStore:
    """Tiny JSON-backed store for the panels each user has connected
    (type, URL, admin login/password). A user can connect several panels
    — including several of the same type (e.g. two Marzban instances) —
    each identified by a short random id used in callback_data.

    The stored password lets the bot re-authenticate on demand (panel API
    tokens/sessions expire), matching the same "admin sees everything"
    trust model already used for Node install notifications.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = asyncio.Lock()
        self._data: dict[str, list[dict]] | None = None

    async def _load(self) -> dict[str, list[dict]]:
        if self._data is None:
            async with self._lock:
                if self._data is None:
                    try:
                        raw = json.loads(self._path.read_text(encoding="utf-8"))
                    except (FileNotFoundError, json.JSONDecodeError, OSError):
                        raw = {}
                    self._data = {
                        user_id: self._migrate_entry(entry) for user_id, entry in raw.items()
                    }
        return self._data

    @staticmethod
    def _migrate_entry(entry: dict | list) -> list[dict]:
        # Older versions stored a single connection per user as a plain
        # dict instead of a list — wrap it so existing connections aren't
        # lost when upgrading to multi-panel support.
        if isinstance(entry, dict):
            entry = {**entry, "id": entry.get("id") or secrets.token_hex(4)}
            return [entry]
        return entry

    async def _write(self, data: dict[str, list[dict]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def list(self, user_id: int) -> list[dict]:
        data = await self._load()
        return data.get(str(user_id), [])

    async def get(self, user_id: int, panel_id: str) -> dict | None:
        for panel in await self.list(user_id):
            if panel["id"] == panel_id:
                return panel
        return None

    async def add(self, user_id: int, panel_type: str, url: str, username: str, password: str) -> str:
        data = await self._load()
        async with self._lock:
            panels = data.setdefault(str(user_id), [])
            existing_ids = {p["id"] for p in panels}
            panel_id = secrets.token_hex(4)
            while panel_id in existing_ids:
                panel_id = secrets.token_hex(4)
            panels.append(
                {
                    "id": panel_id,
                    "type": panel_type,
                    "url": url,
                    "username": username,
                    "password": password,
                }
            )
            await self._write(data)
        return panel_id

    async def remove(self, user_id: int, panel_id: str) -> None:
        data = await self._load()
        async with self._lock:
            panels = data.get(str(user_id), [])
            data[str(user_id)] = [p for p in panels if p["id"] != panel_id]
            await self._write(data)


panel_store = PanelStore(config.data_dir / "panel_connections.json")
