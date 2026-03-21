"""SegmentFault platform via unofficial API.

Authentication: Cookie-based (from browser login session).
API: POST https://segmentfault.com/api/articles
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class SegmentFaultPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "segmentfault"
    DISPLAY_NAME = "SegmentFault"
    REQUIRED_CONFIG_KEYS = ["segmentfault_cookie"]

    API_BASE = "https://segmentfault.com/api"

    def __init__(self, config):
        self.cookie = getattr(config, "segmentfault_cookie", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Cookie": self.cookie or "",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://segmentfault.com/write",
            "Origin": "https://segmentfault.com",
        }

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: [{content.url}]({content.url})"

        tags = ",".join(content.tags) if content.tags else ""

        return {
            "title": content.title,
            "text": body,
            "tags": tags,
            "type": content.metadata.get("segmentfault_type", "article"),
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            response = await self.client.post(
                f"{self.API_BASE}/articles",
                json={
                    "title": adapted["title"],
                    "text": adapted["text"],
                    "tags": adapted["tags"],
                    "type": adapted["type"],
                },
            )

            if response.is_success:
                data = response.json()
                article_id = data.get("data", {}).get("id") or data.get("id", "")
                url = data.get("data", {}).get("url", "")
                if not url and article_id:
                    url = f"https://segmentfault.com/a/{article_id}"
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=url,
                    post_id=str(article_id),
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    async def health_check(self) -> bool:
        try:
            resp = await self.client.get(f"{self.API_BASE}/user/current")
            return resp.is_success
        except Exception:
            return False
