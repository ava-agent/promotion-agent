"""Reddit platform via PRAW (sync library wrapped with asyncio.to_thread)."""

from __future__ import annotations

import asyncio
from typing import Optional

import praw

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class RedditPlatform(BasePlatform):
    PLATFORM_NAME = "reddit"
    DISPLAY_NAME = "Reddit"
    REQUIRED_CONFIG_KEYS = [
        "reddit_client_id",
        "reddit_client_secret",
        "reddit_username",
        "reddit_password",
    ]

    def __init__(self, config):
        self._client_id = getattr(config, "reddit_client_id", None)
        self._client_secret = getattr(config, "reddit_client_secret", None)
        self._username = getattr(config, "reddit_username", None)
        self._password = getattr(config, "reddit_password", None)
        self._user_agent = f"promotion-agent:v4 (by /u/{self._username})"
        self._reddit: Optional[praw.Reddit] = None

    @property
    def reddit(self) -> praw.Reddit:
        if self._reddit is None:
            self._reddit = praw.Reddit(
                client_id=self._client_id,
                client_secret=self._client_secret,
                username=self._username,
                password=self._password,
                user_agent=self._user_agent,
            )
        return self._reddit

    def validate_config(self) -> bool:
        return bool(
            self._client_id
            and self._client_secret
            and self._username
            and self._password
        )

    def adapt_content(self, content: PromotionContent) -> dict:
        subreddit = content.metadata.get("reddit_subreddit", "test")
        is_link = content.metadata.get("reddit_link_post", False)

        payload = {"subreddit": subreddit, "title": content.title[:300]}

        if is_link and content.url:
            payload["url"] = content.url
        else:
            body = content.body
            if content.url:
                body += f"\n\nProject: {content.url}"
            payload["selftext"] = body

        return payload

    def _submit_sync(self, adapted: dict) -> PostResult:
        subreddit = self.reddit.subreddit(adapted["subreddit"])
        if "url" in adapted:
            submission = subreddit.submit(
                title=adapted["title"], url=adapted["url"]
            )
        else:
            submission = subreddit.submit(
                title=adapted["title"], selftext=adapted["selftext"]
            )
        return PostResult(
            platform=self.PLATFORM_NAME,
            success=True,
            url=f"https://reddit.com{submission.permalink}",
            post_id=submission.id,
        )

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            return await asyncio.to_thread(self._submit_sync, adapted)
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    async def health_check(self) -> bool:
        try:
            await asyncio.to_thread(lambda: self.reddit.user.me())
            return True
        except Exception:
            return False
