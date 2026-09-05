from __future__ import annotations

import asyncio
import json
import secrets
from pathlib import Path

from bot.config import config


class CloudStore:
    """Tiny JSON-backed store for the cloud-provider accounts each user has
    connected (provider, login, password). A user can connect several
    accounts — including several with the same provider — each identified
    by a short random id used in callback_data.

    Mirrors bot.services.panel_store.PanelStore: the stored password lets
    the bot re-authenticate on demand, since the provider APIs used here
    (UpCloud's HTTP Basic Auth) don't hand out a long-lived token to cache.
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
                    self._data = raw
        return self._data

    async def _write(self, data: dict[str, list[dict]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def list(self, user_id: int, provider: str | None = None) -> list[dict]:
        data = await self._load()
        accounts = data.get(str(user_id), [])
        if provider is None:
            return accounts
        return [a for a in accounts if a["provider"] == provider]

    async def get(self, user_id: int, account_id: str) -> dict | None:
        for account in await self.list(user_id):
            if account["id"] == account_id:
                return account
        return None

    async def add(self, user_id: int, provider: str, username: str, password: str) -> str:
        data = await self._load()
        async with self._lock:
            accounts = data.setdefault(str(user_id), [])
            existing_ids = {a["id"] for a in accounts}
            account_id = secrets.token_hex(4)
            while account_id in existing_ids:
                account_id = secrets.token_hex(4)
            accounts.append(
                {
                    "id": account_id,
                    "provider": provider,
                    "username": username,
                    "password": password,
                }
            )
            await self._write(data)
        return account_id

    async def remove(self, user_id: int, account_id: str) -> None:
        data = await self._load()
        async with self._lock:
            accounts = data.get(str(user_id), [])
            data[str(user_id)] = [a for a in accounts if a["id"] != account_id]
            await self._write(data)


cloud_store = CloudStore(config.data_dir / "cloud_accounts.json")
