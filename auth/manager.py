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
    expires_hint: str  # "long-lived" | "~1 month" | "~30 days" | "~60 days" | "session" | "none"
    message: str


# Platforms that support set_cookie and their env var names
_COOKIE_PLATFORMS = {
    "zhihu": "PROMOTE_ZHIHU_COOKIE",
    "juejin": "PROMOTE_JUEJIN_COOKIE",
    "csdn": "PROMOTE_CSDN_COOKIE",
    "segmentfault": "PROMOTE_SEGMENTFAULT_COOKIE",
    "oschina": "PROMOTE_OSCHINA_COOKIE",
}

# Auth definitions: (platform, settings_keys, expires_hint, configured_msg, missing_msg)
_AUTH_DEFINITIONS: list[tuple[str, list[str], str, str, str]] = [
    # Original 4
    ("zhihu", ["zhihu_cookie"], "~1 month", "Cookie configured", "No cookie set"),
    ("x", ["x_consumer_key", "x_consumer_secret", "x_access_token", "x_access_token_secret"],
     "long-lived", "OAuth 1.0a configured", "Missing OAuth credentials"),
    ("wechat", ["wechat_app_id", "wechat_app_secret"],
     "long-lived", "App credentials configured", "Missing app_id or app_secret"),
    # Legacy migrated
    ("juejin", ["juejin_cookie"], "~1 month", "Cookie configured", "No cookie set"),
    ("csdn", ["csdn_cookie"], "~1 month", "Cookie configured", "No cookie set"),
    ("devto", ["devto_api_key"], "long-lived", "API key configured", "No API key set"),
    ("reddit", ["reddit_client_id", "reddit_client_secret", "reddit_username", "reddit_password"],
     "long-lived", "OAuth configured", "Missing Reddit credentials"),
    ("linkedin", ["linkedin_access_token"], "~60 days", "Access token configured", "No access token set"),
    ("producthunt", ["producthunt_token"], "long-lived", "Token configured", "No token set"),
    ("cnblogs", ["cnblogs_blog_url", "cnblogs_username", "cnblogs_token"],
     "long-lived", "MetaWeblog credentials configured", "Missing CNBlogs credentials"),
    ("hackernews", ["hn_username", "hn_password"],
     "long-lived", "Credentials configured", "Missing HN username/password"),
    ("moltbook", ["moltbook_api_key"], "long-lived", "API key configured", "No API key set"),
    # New platforms
    ("medium", ["medium_integration_token"], "long-lived", "Integration token configured", "No integration token set"),
    ("hashnode", ["hashnode_token"], "long-lived", "Personal access token configured", "No token set"),
    ("weibo", ["weibo_access_token"], "~30 days", "Access token configured", "No access token set"),
    ("v2ex", ["v2ex_token"], "long-lived", "Personal access token configured", "No token set"),
    ("segmentfault", ["segmentfault_cookie"], "~1 month", "Cookie configured", "No cookie set"),
    ("oschina", ["oschina_cookie"], "~1 month", "Cookie configured", "No cookie set"),
]


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

    def _get_status(self, keys: list[str], expires_hint: str,
                    configured_msg: str, missing_msg: str) -> AuthStatus:
        """Build AuthStatus by checking whether all settings keys are set."""
        configured = all(getattr(self._settings, k, None) for k in keys)
        return AuthStatus(
            configured=configured,
            valid=configured,
            expires_hint=expires_hint,
            message=configured_msg if configured else missing_msg,
        )

    def status_all(self) -> dict[str, AuthStatus]:
        """Return auth status for all supported platforms."""
        result: dict[str, AuthStatus] = {}

        for platform, keys, hint, ok_msg, fail_msg in _AUTH_DEFINITIONS:
            result[platform] = self._get_status(keys, hint, ok_msg, fail_msg)

        # Special cases
        result["xiaohongshu"] = AuthStatus(
            configured=False, valid=False,
            expires_hint="session",
            message="Requires QR code login via auth_qr_login()",
        )

        # AI directories — no auth needed
        for name in ("taaft", "futurepedia", "toolify"):
            result[name] = AuthStatus(True, True, "none", "No auth required")

        return result

    # -- Cookie management --------------------------------------------------

    def set_cookie(self, platform: str, cookie: str) -> None:
        """Write a cookie value to the env file.

        Args:
            platform: Platform name (zhihu, juejin, csdn, segmentfault, oschina).
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
        """Write or update an env var in the env file."""
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
