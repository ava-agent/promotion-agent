"""X (Twitter) platform via official v2 API (async v4 with thread support).

Authentication: OAuth 1.0a with consumer key/secret + access token/secret.
Can alternatively publish through Xquik when configured with a connected account.
Uses tweepy library (sync) wrapped with asyncio.to_thread().
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

import httpx
import tweepy

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


DEFAULT_XQUIK_BASE_URL = "https://xquik.com/api/v1"
DIRECT_PROVIDER = "direct"
XQUIK_PROVIDER = "xquik"


@register_platform
class XTwitterPlatform(BasePlatform):
    PLATFORM_NAME = "x"
    DISPLAY_NAME = "X (Twitter)"
    REQUIRED_CONFIG_KEYS = [
        "x_consumer_key",
        "x_consumer_secret",
        "x_access_token",
        "x_access_token_secret",
    ]

    def __init__(self, config):
        self.provider = (
            (
                getattr(config, "x_provider", None)
                or os.environ.get("PROMOTE_X_PROVIDER")
                or DIRECT_PROVIDER
            )
            .strip()
            .lower()
        )
        self.consumer_key = getattr(config, "x_consumer_key", None)
        self.consumer_secret = getattr(config, "x_consumer_secret", None)
        self.access_token = getattr(config, "x_access_token", None)
        self.access_token_secret = getattr(config, "x_access_token_secret", None)
        self.xquik_api_key = getattr(config, "xquik_api_key", None) or os.environ.get(
            "PROMOTE_XQUIK_API_KEY"
        )
        self.xquik_account = getattr(config, "xquik_account", None) or os.environ.get(
            "PROMOTE_XQUIK_ACCOUNT"
        )
        self.xquik_base_url = (
            getattr(config, "xquik_base_url", None)
            or os.environ.get("PROMOTE_XQUIK_BASE_URL")
            or DEFAULT_XQUIK_BASE_URL
        ).rstrip("/")
        self._client: Optional[tweepy.Client] = None

    @property
    def client(self) -> tweepy.Client:
        if self._client is None:
            self._client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
            )
        return self._client

    def _has_direct_config(self) -> bool:
        return bool(
            self.consumer_key
            and self.consumer_secret
            and self.access_token
            and self.access_token_secret
        )

    def _use_xquik(self) -> bool:
        return self.provider == XQUIK_PROVIDER

    def validate_config(self) -> bool:
        if self._use_xquik():
            return bool(self.xquik_api_key and self.xquik_account)
        return self._has_direct_config()

    def adapt_content(self, content: PromotionContent) -> dict:
        """Build tweet payload. Supports single tweet or thread mode.

        If content.metadata["thread"] exists, return thread mode.
        Otherwise build a single tweet (280 char limit, hashtags, URL).
        """
        # Thread mode
        thread = content.metadata.get("thread")
        if thread:
            return {"text": None, "thread": thread}

        # Single tweet mode
        parts = []

        title = content.title
        if len(title) > 200:
            title = title[:197] + "..."
        parts.append(title)

        if content.url:
            parts.append(content.url)

        if content.tags:
            hashtags = " ".join(f"#{t}" for t in content.tags[:3])
            parts.append(hashtags)

        text = "\n\n".join(parts)

        if len(text) > 280:
            text = text[:277] + "..."

        return {"text": text}

    def _create_tweet_sync(self, **kwargs):
        """Sync helper calling tweepy create_tweet."""
        return self.client.create_tweet(**kwargs)

    async def _post_single(self, text: str) -> PostResult:
        """Post a single tweet."""
        response = await asyncio.to_thread(self._create_tweet_sync, text=text)
        tweet_data = response.data
        if tweet_data and "id" in tweet_data:
            tweet_id = tweet_data["id"]
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=True,
                url=f"https://x.com/i/status/{tweet_id}",
                post_id=str(tweet_id),
            )
        return PostResult(
            platform=self.PLATFORM_NAME,
            success=False,
            error=f"Unexpected response: {response}",
            error_type="unexpected_response",
        )

    async def _post_thread(self, tweets: list[str]) -> PostResult:
        """Post a thread as a reply chain. Returns first tweet ID as post_id."""
        first_tweet_id = None
        previous_id = None

        for tweet_text in tweets:
            kwargs = {"text": tweet_text}
            if previous_id is not None:
                kwargs["in_reply_to_tweet_id"] = previous_id

            response = await asyncio.to_thread(self._create_tweet_sync, **kwargs)
            tweet_data = response.data
            if not tweet_data or "id" not in tweet_data:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Thread broken at tweet: {tweet_text[:50]}",
                    error_type="thread_broken",
                )

            tweet_id = tweet_data["id"]
            if first_tweet_id is None:
                first_tweet_id = tweet_id
            previous_id = tweet_id

        return PostResult(
            platform=self.PLATFORM_NAME,
            success=True,
            url=f"https://x.com/i/status/{first_tweet_id}",
            post_id=str(first_tweet_id),
        )

    async def _post_xquik_tweet(
        self,
        text: str,
        reply_to_tweet_id: Optional[str] = None,
    ) -> str:
        payload = {
            "account": self.xquik_account,
            "text": text,
        }
        if reply_to_tweet_id:
            payload["reply_to_tweet_id"] = reply_to_tweet_id

        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.post(
                f"{self.xquik_base_url}/x/tweets",
                headers={"x-api-key": self.xquik_api_key},
                json=payload,
            )
        response.raise_for_status()
        data = response.json()
        tweet_id = data.get("tweetId")
        if not tweet_id:
            raise ValueError(f"Unexpected response: {data}")
        return str(tweet_id)

    async def _post_xquik_single(self, text: str) -> PostResult:
        tweet_id = await self._post_xquik_tweet(text)
        return PostResult(
            platform=self.PLATFORM_NAME,
            success=True,
            url=f"https://x.com/i/status/{tweet_id}",
            post_id=tweet_id,
        )

    async def _post_xquik_thread(self, tweets: list[str]) -> PostResult:
        first_tweet_id = None
        previous_id = None

        for tweet_text in tweets:
            tweet_id = await self._post_xquik_tweet(
                tweet_text,
                reply_to_tweet_id=previous_id,
            )
            if first_tweet_id is None:
                first_tweet_id = tweet_id
            previous_id = tweet_id

        return PostResult(
            platform=self.PLATFORM_NAME,
            success=True,
            url=f"https://x.com/i/status/{first_tweet_id}",
            post_id=str(first_tweet_id),
        )

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            if self._use_xquik():
                if adapted.get("thread"):
                    return await self._post_xquik_thread(adapted["thread"])
                return await self._post_xquik_single(adapted["text"])

            # Route to thread or single mode
            if adapted.get("thread"):
                return await self._post_thread(adapted["thread"])
            else:
                return await self._post_single(adapted["text"])

        except tweepy.TweepyException as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="tweepy_error",
            )
        except httpx.HTTPError as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="xquik_error",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="unexpected_error",
            )

    async def health_check(self) -> bool:
        try:
            if self._use_xquik():
                async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
                    response = await client.get(
                        f"{self.xquik_base_url}/x/accounts",
                        headers={"x-api-key": self.xquik_api_key},
                    )
                return response.is_success

            me = await asyncio.to_thread(self.client.get_me)
            return me.data is not None
        except Exception:
            return False
