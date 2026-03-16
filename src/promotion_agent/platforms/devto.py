"""Dev.to platform via Forem API."""

from __future__ import annotations

from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


@register_platform
class DevToPlatform(BasePlatform):
    PLATFORM_NAME = "devto"
    DISPLAY_NAME = "Dev.to"
    REQUIRED_CONFIG_KEYS = ["devto_api_key"]

    API_URL = "https://dev.to/api/articles"

    def __init__(self, config):
        self.api_key = getattr(config, "devto_api_key", None)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "api-key": self.api_key or "",
                    "Accept": "application/vnd.forem.api-v1+json",
                    "Content-Type": "application/json",
                },
                timeout=30.0,
                trust_env=False,  # 禁用系统代理避免SSL问题
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.api_key)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n---\n\nCheck it out: {content.url}"

        return {
            "article": {
                "title": content.title,
                "body_markdown": body,
                "published": content.metadata.get("devto_published", True),
                "tags": content.tags[:4],
                "description": content.description or content.title[:100],
                "canonical_url": content.url,
                "series": content.metadata.get("devto_series"),
            }
        }

    def post(self, content: PromotionContent) -> PostResult:
        try:
            payload = self.adapt_content(content)
            response = self.client.post(self.API_URL, json=payload)

            if response.is_success:
                data = response.json()
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=data.get("url"),
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

    def health_check(self) -> bool:
        try:
            resp = self.client.get(
                "https://dev.to/api/articles/me?per_page=1",
            )
            return resp.is_success
        except Exception:
            return False
