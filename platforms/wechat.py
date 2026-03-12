"""微信公众号 (WeChat Official Account) platform via external MCP proxy.

Uses Arcs-MCP external server for WeChat article publishing.
The proxy handles lifecycle management (clone, start, health check).
"""

from __future__ import annotations

from typing import Optional

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.proxy import ExternalMCPConfig, MCPProxy
from core.registry import register_platform
from core.result import PostResult

WECHAT_MCP = ExternalMCPConfig(
    name="wechat",
    repo="https://github.com/anthropics/Arcs-MCP",
    local_path=".mcp-servers/arcs-mcp",
    start_cmd=["python", "-m", "arcs_mcp", "--port", "3002"],
    endpoint="http://localhost:3002/mcp",
)


@register_platform
class WechatPlatform(BasePlatform):
    PLATFORM_NAME = "wechat"
    DISPLAY_NAME = "微信公众号"

    def __init__(self, config, proxy: Optional[MCPProxy] = None) -> None:
        self.app_id = getattr(config, "wechat_app_id", None)
        self.app_secret = getattr(config, "wechat_app_secret", None)
        self._proxy = proxy

    def validate_config(self) -> bool:
        """Check that app_id and app_secret are configured."""
        return bool(self.app_id and self.app_secret)

    def adapt_content(self, content: PromotionContent) -> dict:
        """Transform content for WeChat article submission.

        Digest falls back to body[:120] when not provided in metadata.
        """
        return {
            "title": content.title,
            "body": content.body,
            "cover_image": content.metadata.get("cover_image", None),
            "digest": content.metadata.get("digest", content.body[:120]),
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            await self._proxy.ensure_running("wechat")
            adapted = self.adapt_content(content)
            result = await self._proxy.call_tool(
                "wechat", "submit_article_content_prompt", adapted
            )
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=True,
                post_id=str(result),
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="proxy_error",
            )

    async def health_check(self) -> bool:
        if self._proxy is None:
            return False
        return await self._proxy.is_running("wechat")
