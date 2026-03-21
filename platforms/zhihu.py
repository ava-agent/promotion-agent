"""知乎 (Zhihu) platform via unofficial zhuanlan API (async v4).

Workflow: create draft -> publish draft as column article.
Authentication: Cookie-based (from browser login session).
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class ZhihuPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "zhihu"
    DISPLAY_NAME = "知乎"
    REQUIRED_CONFIG_KEYS = ["zhihu_cookie"]

    BASE_URL = "https://zhuanlan.zhihu.com/api"

    def __init__(self, config):
        self.cookie = getattr(config, "zhihu_cookie", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Cookie": self.cookie or "",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://zhuanlan.zhihu.com",
            "Referer": "https://zhuanlan.zhihu.com/write",
            "X-Requested-With": "XMLHttpRequest",
        }

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n项目地址: {content.url}"

        topics = content.metadata.get("zhihu_topics", [])
        column = content.metadata.get("zhihu_column", "")

        return {
            "title": content.title,
            "content": body,
            "topics": topics,
            "column": column,
        }

    async def _create_draft(self, adapted: dict) -> str | None:
        """Step 1: Create a draft article."""
        resp = await self.client.post(
            f"{self.BASE_URL}/articles/drafts",
            json={
                "title": adapted["title"],
                "content": adapted["content"],
                "delta_time": 0,
            },
        )
        if resp.is_success:
            data = resp.json()
            return str(data.get("id", ""))
        return None

    async def _publish_draft(self, draft_id: str, adapted: dict) -> dict:
        """Step 2: Publish the draft."""
        payload = {"title": adapted["title"], "content": adapted["content"]}

        # Add column if specified
        if adapted.get("column"):
            payload["column"] = {"slug": adapted["column"]}

        # Add topics if specified
        if adapted.get("topics"):
            payload["topics"] = adapted["topics"]

        resp = await self.client.put(
            f"{self.BASE_URL}/articles/{draft_id}/publish",
            json=payload,
        )
        if resp.is_success:
            return resp.json()
        return {"error": resp.text, "status_code": resp.status_code}

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            # Step 1: Create draft
            draft_id = await self._create_draft(adapted)
            if not draft_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Failed to create draft on Zhihu",
                    error_type="draft_creation_failed",
                )

            # Step 2: Publish draft
            pub_data = await self._publish_draft(draft_id, adapted)
            if "error" not in pub_data:
                article_url = pub_data.get(
                    "url", f"https://zhuanlan.zhihu.com/p/{draft_id}"
                )
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=article_url,
                    post_id=draft_id,
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(pub_data.get("error", "Publish failed")),
                error_type="publish_failed",
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
            resp = await self.client.get("https://www.zhihu.com/api/v4/me")
            return resp.is_success
        except Exception:
            return False
