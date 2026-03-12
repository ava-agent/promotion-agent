"""Environment file discovery for promotion-agent settings.

Search order:
1. PROMOTE_ENV_FILE environment variable (explicit path)
2. .env in the current working directory
3. ~/.config/promotion-agent/.env
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def discover_env_file() -> Optional[str]:
    """Find the best .env file path, or None if none exists.

    Priority:
      1. $PROMOTE_ENV_FILE — if set and the file exists
      2. ./.env — current working directory
      3. ~/.config/promotion-agent/.env — XDG-style config dir
    """
    # 1. Explicit env var
    explicit = os.environ.get("PROMOTE_ENV_FILE")
    if explicit:
        if Path(explicit).is_file():
            return explicit
        return None

    # 2. Current working directory
    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        return str(cwd_env)

    # 3. Config directory under HOME
    home = os.environ.get("HOME", str(Path.home()))
    config_env = Path(home) / ".config" / "promotion-agent" / ".env"
    if config_env.is_file():
        return str(config_env)

    return None
