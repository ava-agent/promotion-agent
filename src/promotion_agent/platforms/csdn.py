"""CSDN platform via unofficial saveArticle API.

Authentication: Cookie-based (from browser login session).
"""

from __future__ import annotations

from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


@register_platform
class CSDNPlatform(BasePlatform):
    PLATFORM_NAME = "csdn"
    DISPLAY_NAME = "CSDN"
    REQUIRED_CONFIG_KEYS = ["csdn_cookie"]

    API_URL = "https://blog-console-api.csdn.net/v3/mdeditor/saveArticle"

    def __init__(self, config):
        self.cookie = getattr(config, "csdn_cookie", None)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Content-Type": "application/json",
                    "Cookie": self.cookie or "",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36",
                    "Origin": "https://editor.csdn.net",
                    "Referer": "https://editor.csdn.net/md/",
                },
                timeout=30.0,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: [{content.url}]({content.url})"

        tags = ",".join(content.tags) if content.tags else ""

        return {
            "title": content.title,
            "markdowncontent": body,
            "content": body,  # CSDN also accepts plain content
            "tags": tags,
            "categories": content.metadata.get("csdn_categories", ""),
            "type": content.metadata.get("csdn_type", "original"),
            "status": 0,  # 0=publish, 2=draft
            "readType": "public",
            "Description": (content.description or content.title)[:200],
            "source": "pc_mdeditor",
            "not_auto_saved": "1",
            "authorized_status": False,
            "articleedittype": "1",
        }

    def post(self, content: PromotionContent) -> PostResult:
        try:
            payload = self.adapt_content(content)

            # Check if user wants draft
            if content.metadata.get("csdn_draft", False):
                payload["status"] = 2

            response = self.client.post(self.API_URL, json=payload)

            if response.is_success:
                data = response.json()
                article_id = data.get("data", {}).get("id") or data.get("id")
                if article_id:
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=True,
                        url=f"https://blog.csdn.net/article/details/{article_id}",
                        post_id=str(article_id),
                    )
                # Some responses have different structure
                if data.get("code") == 200 or data.get("msg") == "success":
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=True,
                        url=data.get("data", {}).get("url", ""),
                        post_id=str(data.get("data", {}).get("id", "")),
                    )
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Unexpected response: {data}",
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
                "https://blog-console-api.csdn.net/v1/user/info",
            )
            return resp.is_success
        except Exception:
            return False
