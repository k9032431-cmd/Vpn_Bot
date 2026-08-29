import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    bot_token: str
    support_contact: str
    data_dir: Path


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Add it to your .env file (see .env.example)."
        )
    support_contact = os.getenv("SUPPORT_CONTACT", "").strip()
    data_dir = Path(os.getenv("DATA_DIR", "data"))
    return Config(bot_token=token, support_contact=support_contact, data_dir=data_dir)


config = load_config()
