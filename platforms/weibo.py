"""微博 (Weibo) platform via statuses/share API.

Authentication: OAuth 2.0 access_token (requires approved open platform app).
API: POST https://api.weibo.com/2/statuses/share.json
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class WeiboPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "weibo"
    DISPLAY_NAME = "微博"
    REQUIRED_CONFIG_KEYS = ["weibo_access_token"]

    API_BASE = "https://api.weibo.com/2"

    def __init__(self, config):
        self.access_token = getattr(config, "weibo_access_token", None)
        self._client = None

    def validate_config(self) -> bool:
        return bool(self.access_token)

    def adapt_content(self, content: PromotionContent) -> dict:
        # Weibo share API requires a URL in the status text
        text = content.title
        if content.body:
            remaining = 2000 - len(text) - 5  # Reserve space for URL + separators
            if content.url:
                remaining -= len(content.url) + 2
            body_excerpt = content.body[:remaining] if len(content.body) > remaining else content.body
            text = f"{text}\n\n{body_excerpt}"
        if content.url:
            text = f"{text} {content.url}"
        return {"status": text[:2000]}

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            response = await self.client.post(
                f"{self.API_BASE}/statuses/share.json",
                data={
                    "access_token": self.access_token,
                    "status": adapted["status"],
                },
            )

            if response.is_success:
                data = response.json()
                mid = data.get("mid") or data.get("id") or data.get("idstr", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://weibo.com/{data.get('user', {}).get('id', '')}/{mid}" if mid else "",
                    post_id=str(mid),
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
            resp = await self.client.get(
                f"{self.API_BASE}/account/get_uid.json",
                params={"access_token": self.access_token},
            )
            return resp.is_success
        except Exception:
            return False
