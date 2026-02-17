"""Configuration loader with multi-source support.

Priority (highest to lowest):
1. Environment variables (incl. OpenClaw-injected via skills.entries.*.env)
2. PROMOTE_ENV_FILE override
3. .env in current working directory
4. ~/.config/promotion-agent/.env
5. ~/.openclaw/skills/promotion-agent/.env
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from promotion_agent.config.settings import PromotionSettings


def _find_env_file() -> str | None:
    """Find .env file in priority order."""
    candidates = [
        Path.cwd() / ".env",
        Path.home() / ".config" / "promotion-agent" / ".env",
        Path.home() / ".openclaw" / "skills" / "promotion-agent" / ".env",
    ]
    for path in candidates:
        try:
            if path.is_file():
                return str(path)
        except (OSError, PermissionError):
            continue
    return None


@lru_cache
def load_settings() -> PromotionSettings:
    """Load settings from environment and .env files.

    OpenClaw injects env vars from openclaw.json skills.entries.promotion-agent.env
    directly into the process environment, so pydantic-settings reads them automatically
    via the PROMOTE_ prefix.
    """
    env_file = os.environ.get("PROMOTE_ENV_FILE") or _find_env_file()
    if env_file:
        return PromotionSettings(_env_file=env_file)
    return PromotionSettings()
