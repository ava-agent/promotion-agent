"""Reddit platform via PRAW."""

import praw

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


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
        username = config.reddit_username
        user_agent = getattr(
            config,
            "reddit_user_agent",
            f"promotion-agent:v0.1 (by /u/{username})",
        )
        self.default_subreddit = getattr(config, "reddit_default_subreddit", "test")
        self.reddit = praw.Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            username=username,
            password=config.reddit_password,
            user_agent=user_agent,
        )

    def validate_config(self) -> bool:
        try:
            self.reddit.user.me()
            return True
        except Exception:
            return False

    def adapt_content(self, content: PromotionContent) -> dict:
        subreddit = content.metadata.get("reddit_subreddit", self.default_subreddit)
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

    def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
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
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            self.reddit.user.me()
            return True
        except Exception:
            return False
