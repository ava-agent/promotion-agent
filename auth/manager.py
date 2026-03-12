"""AuthManager — credential status tracking and cookie storage.

Handles per-platform auth status checks and writing cookie values
to the .env file. QR-based login and health_check are handled
in server.py tool handlers since they require platform-specific proxy access.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Optional

from core.settings import PromotionSettings


@dataclass
class AuthStatus:
    """Status of authentication for a single platform."""

    configured: bool
    valid: bool
    expires_hint: str  # "long-lived" | "~1 month" | "session"
    message: str


# Platforms that support set_cookie and their env var names
_COOKIE_PLATFORMS = {
    "zhihu": "PROMOTE_ZHIHU_COOKIE",
}


class AuthManager:
    """Manages credential status and env-file based storage.

    Args:
        settings: Current PromotionSettings instance.
        env_file_path: Path to the .env file for writing cookies.
            If None, set_cookie() will raise ValueError.
    """

    def __init__(
        self,
        settings: PromotionSettings,
        env_file_path: Optional[str] = None,
    ) -> None:
        self._settings = settings
        self._env_file_path = env_file_path

    def status_all(self) -> dict[str, AuthStatus]:
        """Return auth status for all four supported platforms."""
        return {
            "zhihu": self._zhihu_status(),
            "x": self._x_status(),
            "xiaohongshu": self._xiaohongshu_status(),
            "wechat": self._wechat_status(),
        }

    def _zhihu_status(self) -> AuthStatus:
        configured = bool(self._settings.zhihu_cookie)
        return AuthStatus(
            configured=configured,
            valid=configured,  # Can't verify without network call
            expires_hint="~1 month",
            message="Cookie configured" if configured else "No cookie set",
        )

    def _x_status(self) -> AuthStatus:
        configured = bool(
            self._settings.x_consumer_key
            and self._settings.x_consumer_secret
            and self._settings.x_access_token
            and self._settings.x_access_token_secret
        )
        return AuthStatus(
            configured=configured,
            valid=configured,
            expires_hint="long-lived",
            message="OAuth 1.0a configured" if configured else "Missing OAuth credentials",
        )

    def _xiaohongshu_status(self) -> AuthStatus:
        return AuthStatus(
            configured=False,
            valid=False,
            expires_hint="session",
            message="Requires QR code login via auth_qr_login()",
        )

    def _wechat_status(self) -> AuthStatus:
        configured = bool(
            self._settings.wechat_app_id and self._settings.wechat_app_secret
        )
        return AuthStatus(
            configured=configured,
            valid=configured,
            expires_hint="long-lived",
            message="App credentials configured" if configured else "Missing app_id or app_secret",
        )

    def set_cookie(self, platform: str, cookie: str) -> None:
        """Write a cookie value to the env file.

        Args:
            platform: Platform name (currently only 'zhihu' supported).
            cookie: The cookie string to store.

        Raises:
            ValueError: If platform is not supported or no env_file_path.
        """
        if self._env_file_path is None:
            raise ValueError(
                "Cannot set cookie: no env_file_path configured"
            )

        if platform not in _COOKIE_PLATFORMS:
            raise ValueError(
                f"Platform '{platform}' is not supported for cookie auth. "
                f"Supported: {', '.join(_COOKIE_PLATFORMS.keys())}"
            )

        env_key = _COOKIE_PLATFORMS[platform]
        self._write_env_var(env_key, cookie)

    def _write_env_var(self, key: str, value: str) -> None:
        """Write or update an env var in the env file.

        If the key already exists, replaces its value.
        If not, appends a new line.
        Creates the file if it doesn't exist.
        """
        path = self._env_file_path
        lines: list[str] = []
        found = False

        if os.path.isfile(path):
            with open(path, "r") as f:
                lines = f.readlines()

        new_lines: list[str] = []
        pattern = re.compile(rf"^{re.escape(key)}=.*$")
        for line in lines:
            if pattern.match(line.rstrip("\n")):
                new_lines.append(f"{key}={value}\n")
                found = True
            else:
                new_lines.append(line)

        if not found:
            new_lines.append(f"{key}={value}\n")

        with open(path, "w") as f:
            f.writelines(new_lines)
