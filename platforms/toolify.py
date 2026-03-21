"""Toolify.ai — AI directory submission.

Submits AI tools to the Toolify directory. If the site uses
captcha protection, returns submission instructions instead.
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class ToolifyPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "toolify"
    DISPLAY_NAME = "Toolify.ai"
    REQUIRED_CONFIG_KEYS = []

    SUBMIT_URL = "https://www.toolify.ai/submit"

    def __init__(self, config):
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
        }

    def _client_kwargs(self) -> dict:
        return {"follow_redirects": True}

    def validate_config(self) -> bool:
        return True

    def adapt_content(self, content: PromotionContent) -> dict:
        return {
            "name": content.title,
            "url": content.url or "",
            "description": (content.description or content.body)[:500],
            "category": content.metadata.get("directory_category", ""),
            "pricing": content.metadata.get("directory_pricing", ""),
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            response = await self.client.post(
                self.SUBMIT_URL,
                data={
                    "name": adapted["name"],
                    "url": adapted["url"],
                    "description": adapted["description"],
                    "category": adapted["category"],
                    "pricing": adapted["pricing"],
                },
            )

            if response.is_success:
                if "captcha" in response.text.lower() or "recaptcha" in response.text.lower():
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=False,
                        error=f"CAPTCHA detected. Please submit manually at {self.SUBMIT_URL}",
                    )
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=self.SUBMIT_URL,
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"HTTP {response.status_code}. Submit manually at {self.SUBMIT_URL}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"{e}. Submit manually at {self.SUBMIT_URL}",
            )

    async def health_check(self) -> bool:
        try:
            resp = await self.client.get("https://www.toolify.ai/")
            return resp.is_success
        except Exception:
            return False
