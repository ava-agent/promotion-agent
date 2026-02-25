"""掘金 (Juejin) platform via unofficial API.

Workflow: create draft -> update draft content -> publish draft.
Authentication: Cookie-based (sessionid from browser).
"""

from __future__ import annotations

from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


@register_platform
class JuejinPlatform(BasePlatform):
    PLATFORM_NAME = "juejin"
    DISPLAY_NAME = "掘金"
    REQUIRED_CONFIG_KEYS = ["juejin_cookie"]

    BASE_URL = "https://api.juejin.cn/content_api/v1"

    def __init__(self, config):
        self.cookie = getattr(config, "juejin_cookie", None)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Content-Type": "application/json",
                    "Cookie": self.cookie or "",
                },
                timeout=30.0,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: {content.url}"

        return {
            "title": content.title,
            "mark_content": body,
            "brief_content": (content.description or content.title)[:100],
            "category_id": content.metadata.get("juejin_category_id", "6809637767543259144"),  # 默认: 前端
            "tag_ids": content.metadata.get("juejin_tag_ids", []),
            "cover_image": content.metadata.get("juejin_cover_image", ""),
            "edit_type": 10,
        }

    def _create_draft(self, adapted: dict) -> Optional[str]:
        """Step 1: Create an empty draft, returns draft_id."""
        resp = self.client.post(
            f"{self.BASE_URL}/article_draft/create",
            json={
                "title": adapted["title"],
                "mark_content": adapted["mark_content"],
                "brief_content": adapted["brief_content"],
                "category_id": adapted["category_id"],
                "tag_ids": adapted["tag_ids"],
                "cover_image": adapted["cover_image"],
                "edit_type": adapted["edit_type"],
            },
        )
        data = resp.json()
        if data.get("err_no") == 0:
            return data["data"]["id"]
        return None

    def _publish_draft(self, draft_id: str) -> dict:
        """Step 2: Publish the draft."""
        resp = self.client.post(
            f"{self.BASE_URL}/article/publish",
            json={
                "draft_id": draft_id,
                "sync_to_org": False,
                "column_ids": [],
                "theme_ids": [],
            },
        )
        return resp.json()

    def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            # Step 1: Create draft
            draft_id = self._create_draft(adapted)
            if not draft_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Failed to create draft",
                )

            # Step 2: Publish draft
            publish_data = self._publish_draft(draft_id)
            if publish_data.get("err_no") == 0:
                article_id = publish_data["data"].get("article_id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://juejin.cn/post/{article_id}",
                    post_id=str(article_id),
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=publish_data.get("err_msg", "Publish failed"),
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            resp = self.client.post(
                "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed",
                json={"sort_type": 200, "cursor": "0", "limit": 1},
            )
            return resp.is_success
        except Exception:
            return False
