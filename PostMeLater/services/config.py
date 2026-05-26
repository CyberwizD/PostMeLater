"""Configuration and environment loading helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"


@lru_cache(maxsize=1)
def load_env_file() -> dict[str, str]:
    """Load .env values without printing secrets."""
    values: dict[str, str] = {}
    if not ENV_PATH.exists():
        return values
    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
        values[key] = os.environ.get(key, value)
    return values


def get_setting(*names: str, default: str = "") -> str:
    """Return the first configured environment value for the given names."""
    load_env_file()
    for name in names:
        value = os.environ.get(name)
        if value:
            return value.strip()
    return default


def app_timezone() -> str:
    """Return the timezone used for scheduled posts."""
    return get_setting("APP_TIMEZONE", "TZ", default="Africa/Lagos")

