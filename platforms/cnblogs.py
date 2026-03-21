"""博客园 (CNBlogs) platform via MetaWeblog XML-RPC API.

Authentication: Username + API Token (generated in cnblogs settings).
API endpoint: https://rpc.cnblogs.com/metaweblog/{blogname}
"""

from __future__ import annotations

import asyncio
import xmlrpc.client
from typing import Optional

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class CNBlogsPlatform(BasePlatform):
    PLATFORM_NAME = "cnblogs"
    DISPLAY_NAME = "博客园"
    REQUIRED_CONFIG_KEYS = ["cnblogs_blog_url", "cnblogs_username", "cnblogs_token"]

    def __init__(self, config):
        self.blog_url = getattr(config, "cnblogs_blog_url", None)
        self.username = getattr(config, "cnblogs_username", None)
        self.token = getattr(config, "cnblogs_token", None)
        self._proxy: Optional[xmlrpc.client.ServerProxy] = None

    @property
    def proxy(self) -> xmlrpc.client.ServerProxy:
        if self._proxy is None:
            rpc_url = f"https://rpc.cnblogs.com/metaweblog/{self.username}"
            self._proxy = xmlrpc.client.ServerProxy(rpc_url)
        return self._proxy

    def validate_config(self) -> bool:
        return bool(self.blog_url and self.username and self.token)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: [{content.url}]({content.url})"

        categories = content.metadata.get("cnblogs_categories", [])
        mt_keywords = ",".join(content.tags) if content.tags else ""

        return {
            "title": content.title,
            "description": body,
            "categories": categories,
            "mt_keywords": mt_keywords,
        }

    def _new_post_sync(self, adapted: dict, publish: bool) -> PostResult:
        post_struct = {
            "title": adapted["title"],
            "description": adapted["description"],
            "categories": adapted["categories"],
            "mt_keywords": adapted["mt_keywords"],
        }
        post_id = self.proxy.metaWeblog.newPost(
            self.blog_url,
            self.username,
            self.token,
            post_struct,
            publish,
        )
        return PostResult(
            platform=self.PLATFORM_NAME,
            success=True,
            url=f"https://www.cnblogs.com/{self.username}/p/{post_id}.html",
            post_id=str(post_id),
        )

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)
            publish = not content.metadata.get("cnblogs_draft", False)
            return await asyncio.to_thread(self._new_post_sync, adapted, publish)
        except xmlrpc.client.Fault as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"XML-RPC fault: {e.faultString}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    async def health_check(self) -> bool:
        try:
            await asyncio.to_thread(
                lambda: self.proxy.metaWeblog.getRecentPosts(
                    self.blog_url, self.username, self.token, 1,
                )
            )
            return True
        except Exception:
            return False
