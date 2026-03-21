"""Medium platform via REST API v1.

Authentication: Integration Token (Bearer).
Flow: GET /me → userId → POST /users/{userId}/posts
"""

from __future__ import annotations

from typing import Optional

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class MediumPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "medium"
    DISPLAY_NAME = "Medium"
    REQUIRED_CONFIG_KEYS = ["medium_integration_token"]

    API_BASE = "https://api.medium.com/v1"

    def __init__(self, config):
        self.token = getattr(config, "medium_integration_token", None)
        self._client = None
        self._user_id: Optional[str] = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token or ''}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def validate_config(self) -> bool:
        return bool(self.token)

    async def _get_user_id(self) -> Optional[str]:
        if self._user_id:
            return self._user_id
        resp = await self.client.get(f"{self.API_BASE}/me")
        if resp.is_success:
            uid = resp.json().get("data", {}).get("id")
            if uid:
                self._user_id = uid
                return uid
        return None

    def adapt_content(self, content: PromotionContent) -> dict:
        return {
            "title": content.title,
            "contentFormat": "markdown",
            "content": content.body,
            "tags": content.tags[:5],
            "canonicalUrl": content.url or "",
            "publishStatus": content.metadata.get("medium_status", "public"),
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            user_id = await self._get_user_id()
            if not user_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Could not retrieve Medium user ID. Token may be invalid.",
                )

            payload = self.adapt_content(content)
            response = await self.client.post(
                f"{self.API_BASE}/users/{user_id}/posts",
                json=payload,
            )

            if response.is_success:
                data = response.json().get("data", {})
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=data.get("url", ""),
                    post_id=str(data.get("id", "")),
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"HTTP {response.status_code}: {response.text}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    async def health_check(self) -> bool:
        try:
            resp = await self.client.get(f"{self.API_BASE}/me")
            return resp.is_success
        except Exception:
            return False
