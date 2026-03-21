"""OSCHINA (开源中国) platform via API.

Authentication: Cookie-based or OAuth.
API: https://www.oschina.net/action/apiv2/
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class OSCHINAPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "oschina"
    DISPLAY_NAME = "OSCHINA"
    REQUIRED_CONFIG_KEYS = ["oschina_cookie"]

    API_BASE = "https://www.oschina.net/action/apiv2"

    def __init__(self, config):
        self.cookie = getattr(config, "oschina_cookie", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Cookie": self.cookie or "",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.oschina.net/",
            "Origin": "https://www.oschina.net",
        }

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: [{content.url}]({content.url})"

        return {
            "title": content.title,
            "content": body,
            "content_type": "markdown",
            "category": content.metadata.get("oschina_category", "1"),
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            response = await self.client.post(
                f"{self.API_BASE}/blog",
                json={
                    "title": adapted["title"],
                    "content": adapted["content"],
                    "content_type": adapted["content_type"],
                    "category": adapted["category"],
                },
            )

            if response.is_success:
                data = response.json()
                blog_id = data.get("id", "")
                url = data.get("url", "")
                if not url and blog_id:
                    url = f"https://my.oschina.net/blog/{blog_id}"
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=url,
                    post_id=str(blog_id),
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
            resp = await self.client.get(f"{self.API_BASE}/user/me")
            return resp.is_success
        except Exception:
            return False
