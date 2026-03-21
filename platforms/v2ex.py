"""V2EX platform via API v2.

Authentication: Personal Access Token (Bearer).
Note: V2EX API v2 topic creation may be restricted. If the API
does not support posting, returns a preview with instructions.
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class V2EXPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "v2ex"
    DISPLAY_NAME = "V2EX"
    REQUIRED_CONFIG_KEYS = ["v2ex_token"]

    API_BASE = "https://www.v2ex.com/api/v2"

    def __init__(self, config):
        self.token = getattr(config, "v2ex_token", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token or ''}",
            "Content-Type": "application/json",
        }

    def validate_config(self) -> bool:
        return bool(self.token)

    def adapt_content(self, content: PromotionContent) -> dict:
        node_name = content.metadata.get("v2ex_node", "share")
        body = content.body
        if content.url:
            body += f"\n\n项目地址: {content.url}"
        return {
            "title": content.title,
            "body": body,
            "node_name": node_name,
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            response = await self.client.post(
                f"{self.API_BASE}/topics",
                json={
                    "title": adapted["title"],
                    "body": adapted["body"],
                    "node_name": adapted["node_name"],
                },
            )

            if response.is_success:
                data = response.json()
                result_data = data.get("result", data)
                topic_id = result_data.get("id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://www.v2ex.com/t/{topic_id}" if topic_id else "",
                    post_id=str(topic_id),
                )

            if response.status_code in (401, 403):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="V2EX API may not support topic creation. Please post manually at https://www.v2ex.com/new",
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

    async def health_check(self) -> bool:
        try:
            resp = await self.client.get(f"{self.API_BASE}/token")
            return resp.is_success
        except Exception:
            return False
