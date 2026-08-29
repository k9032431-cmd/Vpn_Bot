import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _parse_ids(raw: str) -> frozenset[int]:
    ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part:
            try:
                ids.add(int(part))
            except ValueError:
                pass
    return frozenset(ids)


@dataclass(frozen=True)
class Config:
    bot_token: str
    support_contact: str
    data_dir: Path
    admin_ids: frozenset[int] = field(default_factory=frozenset)


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Add it to your .env file (see .env.example)."
        )
    support_contact = os.getenv("SUPPORT_CONTACT", "").strip()
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    admin_ids = _parse_ids(os.getenv("ADMIN_IDS", ""))
    return Config(
        bot_token=token,
        support_contact=support_contact,
        data_dir=data_dir,
        admin_ids=admin_ids,
    )


config = load_config()
