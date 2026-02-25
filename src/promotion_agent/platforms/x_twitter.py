"""X (Twitter) platform via official v2 API.

Authentication: OAuth 1.0a with consumer key/secret + access token/secret.
Uses tweepy library. Free tier: 500 posts/month.
"""

from __future__ import annotations

from typing import Optional

import tweepy

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


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
        self.consumer_key = getattr(config, "x_consumer_key", None)
        self.consumer_secret = getattr(config, "x_consumer_secret", None)
        self.access_token = getattr(config, "x_access_token", None)
        self.access_token_secret = getattr(config, "x_access_token_secret", None)
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

    def validate_config(self) -> bool:
        return bool(
            self.consumer_key
            and self.consumer_secret
            and self.access_token
            and self.access_token_secret
        )

    def adapt_content(self, content: PromotionContent) -> dict:
        """Build tweet text. Twitter limit is 280 characters."""
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

    def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            response = self.client.create_tweet(text=adapted["text"])

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
            )
        except tweepy.TweepyException as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            me = self.client.get_me()
            return me.data is not None
        except Exception:
            return False
