"""小红书 (Xiaohongshu) platform via external MCP proxy.

Uses xiaohongshu-mcp external server for authentication and publishing.
The proxy handles lifecycle management (clone, start, health check).
"""

from __future__ import annotations

from typing import Optional

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.proxy import ExternalMCPConfig, MCPProxy
from core.registry import register_platform
from core.result import PostResult

XIAOHONGSHU_MCP = ExternalMCPConfig(
    name="xiaohongshu",
    repo="https://github.com/anthropics/xiaohongshu-mcp",
    local_path=".mcp-servers/xiaohongshu-mcp",
    start_cmd=["python", "-m", "xiaohongshu_mcp", "--port", "3001"],
    endpoint="http://localhost:3001/mcp",
)


@register_platform
class XiaohongshuPlatform(BasePlatform):
    PLATFORM_NAME = "xiaohongshu"
    DISPLAY_NAME = "小红书"

    def __init__(self, config, proxy: Optional[MCPProxy] = None) -> None:
        self._proxy = proxy

    def validate_config(self) -> bool:
        """Always True — auth is managed by the external MCP server."""
        return True

    def adapt_content(self, content: PromotionContent) -> dict:
        """Transform content for Xiaohongshu note publishing.

        Title is truncated to <=20 chars (Xiaohongshu limit).
        Images come from content.metadata['images'].
        """
        title = content.title
        if len(title) > 20:
            title = title[:17] + "..."

        return {
            "title": title,
            "body": content.body,
            "images": content.metadata.get("images", []),
            "tags": content.tags,
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            await self._proxy.ensure_running("xiaohongshu")
            adapted = self.adapt_content(content)
            result = await self._proxy.call_tool(
                "xiaohongshu", "publish_note", adapted
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
        return await self._proxy.is_running("xiaohongshu")
