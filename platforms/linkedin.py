"""LinkedIn platform via ugcPosts REST API.

Authentication: OAuth 2.0 access token (obtain manually, expires in 60 days).
Scopes required: w_member_social, openid, profile.
"""

from __future__ import annotations

from typing import Optional

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class LinkedInPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "linkedin"
    DISPLAY_NAME = "LinkedIn"
    REQUIRED_CONFIG_KEYS = ["linkedin_access_token"]

    API_BASE = "https://api.linkedin.com/v2"

    def __init__(self, config):
        self.access_token = getattr(config, "linkedin_access_token", None)
        self._client = None
        self._person_id: Optional[str] = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token or ''}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def validate_config(self) -> bool:
        return bool(self.access_token)

    async def _get_person_id(self) -> Optional[str]:
        if self._person_id:
            return self._person_id
        resp = await self.client.get(f"{self.API_BASE}/userinfo")
        if resp.is_success:
            sub = resp.json().get("sub")
            if sub:
                self._person_id = sub
                return sub
        return None

    def adapt_content(self, content: PromotionContent) -> dict:
        text_parts = [content.title]
        if content.body:
            text_parts.append(content.body)
        if content.url:
            text_parts.append(content.url)
        if content.tags:
            hashtags = " ".join(f"#{t}" for t in content.tags[:5])
            text_parts.append(hashtags)
        return {
            "text": "\n\n".join(text_parts),
            "url": content.url,
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            person_id = await self._get_person_id()
            if not person_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Could not retrieve LinkedIn person ID. Token may be expired.",
                )

            adapted = self.adapt_content(content)

            payload: dict = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": adapted["text"]},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

            if adapted.get("url"):
                share = payload["specificContent"]["com.linkedin.ugc.ShareContent"]
                share["shareMediaCategory"] = "ARTICLE"
                share["media"] = [{"status": "READY", "originalUrl": adapted["url"]}]

            response = await self.client.post(f"{self.API_BASE}/ugcPosts", json=payload)

            if response.is_success:
                post_id = response.json().get("id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://www.linkedin.com/feed/update/{post_id}",
                    post_id=str(post_id),
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
            resp = await self.client.get(f"{self.API_BASE}/userinfo")
            return resp.is_success
        except Exception:
            return False
