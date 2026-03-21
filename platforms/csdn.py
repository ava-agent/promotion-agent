"""CSDN platform via unofficial saveArticle API.

Authentication: Cookie-based (from browser login session).
Note: Playwright fallback removed in v4. If WAF blocks the API,
returns an error suggesting manual publishing.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult

logger = logging.getLogger(__name__)


@register_platform
class CSDNPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "csdn"
    DISPLAY_NAME = "CSDN"
    REQUIRED_CONFIG_KEYS = ["csdn_cookie"]

    API_URL = "https://blog-console-api.csdn.net/v3/mdeditor/saveArticle"

    def __init__(self, config):
        self.cookie = getattr(config, "csdn_cookie", None)
        self._client = None

    def _extract_csrf_token(self) -> Optional[str]:
        if not self.cookie:
            return None
        for part in self.cookie.split(";"):
            part = part.strip()
            if part.lower().startswith("csrf_token=") or part.lower().startswith("x-csrf-token="):
                return part.split("=", 1)[1]
        return None

    def _extract_username(self) -> Optional[str]:
        if not self.cookie:
            return None
        for part in self.cookie.split(";"):
            part = part.strip()
            if part.startswith("UserName="):
                return part.split("=", 1)[1]
        return None

    def _default_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.cookie or "",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://editor.csdn.net",
            "Referer": "https://editor.csdn.net/md/",
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
        }
        csrf = self._extract_csrf_token()
        if csrf:
            headers["x-csrf-token"] = csrf
        return headers

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
            "content": body,
            "tags": tags,
            "categories": content.metadata.get("csdn_categories", ""),
            "type": content.metadata.get("csdn_type", "original"),
            "status": 0,
            "readType": "public",
            "Description": (content.description or content.title)[:200],
            "source": "pc_mdeditor",
            "not_auto_saved": "1",
            "authorized_status": False,
            "articleedittype": "1",
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            payload = self.adapt_content(content)
            if content.metadata.get("csdn_draft", False):
                payload["status"] = 2

            response = await self.client.post(self.API_URL, json=payload)

            if response.status_code in (401, 403):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"CSDN WAF blocked (HTTP {response.status_code}). Please publish manually at https://editor.csdn.net/md/",
                )

            if response.is_success:
                data = response.json()
                article_id = data.get("data", {}).get("id") or data.get("id")
                if article_id:
                    username = self._extract_username() or ""
                    url = data.get("data", {}).get("url", "")
                    if not url and username:
                        url = f"https://blog.csdn.net/{username}/article/details/{article_id}"
                    elif not url:
                        url = f"https://blog.csdn.net/article/details/{article_id}"
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=True,
                        url=url,
                        post_id=str(article_id),
                    )
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
                error=f"HTTP {response.status_code}: {response.text[:200]}",
            )
        except httpx.NetworkError as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"网络错误: {e}",
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
                "https://blog-console-api.csdn.net/v1/user/info",
            )
            return resp.is_success
        except Exception:
            return False
