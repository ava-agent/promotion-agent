"""Hacker News platform via web form scraping.

No official posting API. Workflow:
POST /login (get session) -> GET /submit (extract fnid CSRF) -> POST /r (submit).
Authentication: Username + password (session cookies).
"""

from __future__ import annotations

import re
from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


@register_platform
class HackerNewsPlatform(BasePlatform):
    PLATFORM_NAME = "hackernews"
    DISPLAY_NAME = "Hacker News"
    REQUIRED_CONFIG_KEYS = ["hn_username", "hn_password"]

    BASE_URL = "https://news.ycombinator.com"

    def __init__(self, config):
        self.username = getattr(config, "hn_username", None)
        self.password = getattr(config, "hn_password", None)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                },
                follow_redirects=True,
                timeout=30.0,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.username and self.password)

    def _login(self) -> bool:
        """Authenticate and store session cookie."""
        resp = self.client.post(
            f"{self.BASE_URL}/login",
            data={"acct": self.username, "pw": self.password, "goto": "news"},
        )
        return "user" in resp.cookies or "user" in self.client.cookies

    def _extract_fnid(self) -> Optional[str]:
        """Fetch /submit page and extract the fnid CSRF token."""
        resp = self.client.get(f"{self.BASE_URL}/submit")
        if not resp.is_success:
            return None
        match = re.search(r'name="fnid"\s+value="([^"]+)"', resp.text)
        return match.group(1) if match else None

    def adapt_content(self, content: PromotionContent) -> dict:
        """Build form data for HN submission.

        HN supports two types:
        - Link post: title + url
        - Text post (Ask HN): title + text (no url)
        """
        payload: dict[str, str] = {"title": content.title[:80]}

        if content.url:
            payload["url"] = content.url
        else:
            payload["text"] = content.body

        return payload

    def post(self, content: PromotionContent) -> PostResult:
        try:
            if not self._login():
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Login failed. Check HN username/password.",
                )

            fnid = self._extract_fnid()
            if not fnid:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Could not extract fnid token from /submit page.",
                )

            adapted = self.adapt_content(content)
            form_data = {"fnid": fnid, "fnop": "submit-page", **adapted}
            resp = self.client.post(f"{self.BASE_URL}/r", data=form_data)

            if resp.status_code in (200, 302) and "newest" in str(resp.url):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"{self.BASE_URL}/newest",
                )

            if "please slow down" in resp.text.lower():
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Rate limited by Hacker News. Please wait before resubmitting.",
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"Submission may have failed. Response URL: {resp.url}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            resp = self.client.get(f"{self.BASE_URL}/news")
            return resp.is_success
        except Exception:
            return False
