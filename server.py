"""promotion-agent MCP Server — 12 tools for social media publishing.

Tools:
  Publish (6): publish_zhihu, publish_x, publish_xiaohongshu, publish_wechat,
               publish (generic), submit_directory
  Auth (4):    auth_status, auth_set_cookie, auth_qr_login, auth_health_check
  Utility (2): list_platforms, preview_content

Platforms (18): zhihu, x, xiaohongshu, wechat, juejin, csdn, devto, reddit,
  linkedin, producthunt, cnblogs, hackernews, moltbook, medium, hashnode,
  weibo, v2ex, segmentfault, oschina
AI Directories (3): taaft, futurepedia, toolify

Requires: pip install mcp  (Python 3.10+)
Run:      python server.py          (stdio transport)
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import asdict
from typing import Optional

from mcp.server.fastmcp import FastMCP

from auth.manager import AuthManager
from core.content import ContentFormat, PromotionContent
from core.settings import PromotionSettings

# Import platforms to trigger @register_platform decorators
import platforms.zhihu        # noqa: F401
import platforms.x_twitter    # noqa: F401
import platforms.xiaohongshu  # noqa: F401
import platforms.wechat       # noqa: F401
# Legacy migrated
import platforms.juejin       # noqa: F401
import platforms.csdn         # noqa: F401
import platforms.devto        # noqa: F401
import platforms.reddit       # noqa: F401
import platforms.linkedin     # noqa: F401
import platforms.producthunt  # noqa: F401
import platforms.cnblogs      # noqa: F401
import platforms.hackernews   # noqa: F401
import platforms.moltbook     # noqa: F401
# New platforms
import platforms.medium       # noqa: F401
import platforms.hashnode      # noqa: F401
import platforms.weibo        # noqa: F401
import platforms.v2ex         # noqa: F401
import platforms.segmentfault  # noqa: F401
import platforms.oschina      # noqa: F401
# AI directories
import platforms.taaft        # noqa: F401
import platforms.futurepedia  # noqa: F401
import platforms.toolify      # noqa: F401

from core.registry import get_platform, list_platforms as registry_list_platforms

# ---------------------------------------------------------------------------
# FastMCP app
# ---------------------------------------------------------------------------

app = FastMCP("promotion-agent")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_PLATFORMS = [
    "zhihu", "x", "xiaohongshu", "wechat",
    "juejin", "csdn", "devto", "reddit", "linkedin",
    "producthunt", "cnblogs", "hackernews", "moltbook",
    "medium", "hashnode", "weibo", "v2ex",
    "segmentfault", "oschina",
]

DIRECTORY_PLATFORMS = ["taaft", "futurepedia", "toolify"]


def _settings() -> PromotionSettings:
    """Load settings from environment / .env file."""
    return PromotionSettings(_env_file=None)


def _env_file_path() -> str:
    return os.environ.get(
        "PROMOTE_ENV_FILE",
        os.path.join(os.path.dirname(__file__), ".env"),
    )


def _auth_manager() -> AuthManager:
    return AuthManager(_settings(), env_file_path=_env_file_path())


async def _do_publish(
    platform_name: str,
    content: PromotionContent,
    dry_run: bool,
) -> dict:
    """Shared publish logic: instantiate platform, adapt, optionally post."""
    settings = _settings()
    try:
        platform_cls = get_platform(platform_name)
    except KeyError:
        return {"error": f"Unknown platform: {platform_name}. Use list_platforms to see available options."}

    instance = platform_cls(settings)
    adapted = instance.adapt_content(content)

    if dry_run:
        return {"dry_run": True, "platform": platform_name, "adapted": adapted}

    result = await instance.post(content)
    return asdict(result)


# ---------------------------------------------------------------------------
# Publish tools — original 4 (backward compatible)
# ---------------------------------------------------------------------------


@app.tool()
async def publish_zhihu(
    title: str,
    body: str,
    column: str = "",
    topics: Optional[list[str]] = None,
    dry_run: bool = False,
) -> dict:
    """Publish an article to Zhihu (知乎).

    Args:
        title: Article title.
        body: Article body in Markdown.
        column: Zhihu column slug (optional).
        topics: List of topic strings (optional).
        dry_run: If True, return adapted content without posting.
    """
    content = PromotionContent(
        title=title,
        body=body,
        format=ContentFormat.MARKDOWN,
        metadata={"zhihu_column": column, "zhihu_topics": topics or []},
    )
    return await _do_publish("zhihu", content, dry_run)


@app.tool()
async def publish_x(
    text: str = "",
    thread: Optional[list[str]] = None,
    url: str = "",
    hashtags: Optional[list[str]] = None,
    dry_run: bool = False,
) -> dict:
    """Publish a tweet or thread to X (Twitter).

    Args:
        text: Tweet text (single tweet mode).
        thread: List of tweet texts for thread mode.
        url: URL to include in the tweet.
        hashtags: List of hashtag strings (without #).
        dry_run: If True, return adapted content without posting.
    """
    metadata = {}
    if thread:
        metadata["thread"] = thread

    content = PromotionContent(
        title=text,
        body=text,
        format=ContentFormat.PLAIN,
        tags=hashtags or [],
        url=url or None,
        metadata=metadata,
    )
    return await _do_publish("x", content, dry_run)


@app.tool()
async def publish_xiaohongshu(
    title: str,
    body: str,
    images: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    dry_run: bool = False,
) -> dict:
    """Publish a note to Xiaohongshu (小红书).

    Args:
        title: Note title (max 20 chars).
        body: Note body text.
        images: List of image URLs or paths.
        tags: List of tag strings.
        dry_run: If True, return adapted content without posting.
    """
    content = PromotionContent(
        title=title,
        body=body,
        format=ContentFormat.MARKDOWN,
        tags=tags or [],
        metadata={"images": images or []},
    )
    return await _do_publish("xiaohongshu", content, dry_run)


@app.tool()
async def publish_wechat(
    title: str,
    body: str,
    cover_image: str = "",
    digest: str = "",
    dry_run: bool = False,
) -> dict:
    """Publish an article to WeChat Official Account (微信公众号).

    Args:
        title: Article title.
        body: Article body in Markdown.
        cover_image: Cover image URL (optional).
        digest: Article digest/summary (optional, defaults to body[:120]).
        dry_run: If True, return adapted content without posting.
    """
    metadata = {}
    if cover_image:
        metadata["cover_image"] = cover_image
    if digest:
        metadata["digest"] = digest

    content = PromotionContent(
        title=title,
        body=body,
        format=ContentFormat.MARKDOWN,
        metadata=metadata,
    )
    return await _do_publish("wechat", content, dry_run)


# ---------------------------------------------------------------------------
# Generic publish tool (covers all 18 platforms)
# ---------------------------------------------------------------------------


@app.tool()
async def publish(
    platform: str,
    title: str,
    body: str,
    tags: Optional[list[str]] = None,
    url: str = "",
    description: str = "",
    metadata: Optional[dict] = None,
    dry_run: bool = False,
) -> dict:
    """Publish content to any supported platform.

    Use this for platforms beyond the original four (zhihu, x, xiaohongshu, wechat).
    Supports: juejin, csdn, devto, reddit, linkedin, producthunt, cnblogs,
    hackernews, moltbook, medium, hashnode, weibo, v2ex, segmentfault, oschina.
    Also works with the original four platforms.

    Args:
        platform: Platform identifier (e.g. "devto", "medium", "juejin").
        title: Content title.
        body: Content body (usually Markdown).
        tags: List of tag strings.
        url: Project/canonical URL to include.
        description: Short description/summary.
        metadata: Platform-specific options. Examples:
            reddit: {"reddit_subreddit": "python", "reddit_link_post": true}
            juejin: {"juejin_category_id": "...", "juejin_tag_ids": [...]}
            v2ex: {"v2ex_node": "share"}
            medium: {"medium_status": "draft"}
            hashnode: (uses PROMOTE_HASHNODE_PUBLICATION_ID from env)
        dry_run: If True, return adapted content without posting.
    """
    content = PromotionContent(
        title=title,
        body=body,
        format=ContentFormat.MARKDOWN,
        tags=tags or [],
        url=url or None,
        description=description or None,
        metadata=metadata or {},
    )
    return await _do_publish(platform, content, dry_run)


# ---------------------------------------------------------------------------
# AI Directory submission tool
# ---------------------------------------------------------------------------


@app.tool()
async def submit_directory(
    directory: str,
    name: str,
    url: str,
    description: str,
    category: str = "",
    pricing: str = "",
    dry_run: bool = False,
) -> dict:
    """Submit an AI tool to a directory listing site.

    Supported directories: taaft (There's An AI For That), futurepedia, toolify.

    Args:
        directory: Directory identifier (taaft, futurepedia, toolify).
        name: Tool/product name.
        url: Tool URL.
        description: Tool description (max 500 chars).
        category: Tool category (optional).
        pricing: Pricing model (e.g. "free", "freemium", "paid").
        dry_run: If True, return adapted content without submitting.
    """
    content = PromotionContent(
        title=name,
        body=description,
        description=description,
        url=url or None,
        metadata={
            "directory_category": category,
            "directory_pricing": pricing,
        },
    )

    result = await _do_publish(directory, content, dry_run)
    # Rename "platform" key to "directory" for directory results
    if "platform" in result:
        result["directory"] = result.pop("platform")
    return result


# ---------------------------------------------------------------------------
# Auth tools (4)
# ---------------------------------------------------------------------------


@app.tool()
async def auth_status() -> dict:
    """Return authentication status for all supported platforms."""
    mgr = _auth_manager()
    statuses = mgr.status_all()
    return {name: asdict(status) for name, status in statuses.items()}


@app.tool()
async def auth_set_cookie(platform: str, cookie: str) -> dict:
    """Write a cookie value to the env file for a platform.

    Args:
        platform: Platform name (e.g. 'zhihu', 'juejin', 'csdn', 'segmentfault', 'oschina').
        cookie: The cookie string to store.
    """
    try:
        mgr = _auth_manager()
        mgr.set_cookie(platform, cookie)
        return {"success": True, "platform": platform, "message": "Cookie saved"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


@app.tool()
async def auth_qr_login() -> dict:
    """Trigger QR code login for Xiaohongshu.

    Returns instructions for completing QR-based authentication
    via the external MCP proxy.
    """
    return {
        "platform": "xiaohongshu",
        "method": "qr_login",
        "message": (
            "QR login for Xiaohongshu requires the external MCP proxy. "
            "Ensure the xiaohongshu-mcp server is running, then scan "
            "the QR code displayed in the proxy terminal."
        ),
    }


@app.tool()
async def auth_health_check(platform: str) -> dict:
    """Verify that credentials for a platform are still valid.

    Args:
        platform: Platform name to check (any of the 18 supported platforms).
    """
    settings = _settings()
    try:
        platform_cls = get_platform(platform)
        instance = platform_cls(settings)

        if not instance.validate_config():
            return {
                "platform": platform,
                "healthy": False,
                "message": "Credentials not configured",
            }

        healthy = await instance.health_check()
        return {
            "platform": platform,
            "healthy": healthy,
            "message": "OK" if healthy else "Health check failed",
        }
    except KeyError:
        return {
            "platform": platform,
            "healthy": False,
            "message": f"Unknown platform: {platform}",
        }
    except Exception as e:
        return {
            "platform": platform,
            "healthy": False,
            "message": str(e),
        }


# ---------------------------------------------------------------------------
# Utility tools (2)
# ---------------------------------------------------------------------------


@app.tool()
async def list_platforms() -> list[dict]:
    """Return a list of all supported platforms with their auth status."""
    mgr = _auth_manager()
    statuses = mgr.status_all()
    registry = registry_list_platforms()

    result = []
    for name, cls in registry.items():
        auth = statuses.get(name)
        is_directory = name in DIRECTORY_PLATFORMS
        result.append({
            "name": name,
            "display_name": cls.DISPLAY_NAME,
            "type": "directory" if is_directory else "platform",
            "auth": asdict(auth) if auth else {"configured": False, "valid": False},
        })
    return result


@app.tool()
async def preview_content(
    title: str,
    body: str,
    platforms: Optional[list[str]] = None,
) -> dict:
    """Preview how content will be adapted for each platform.

    Args:
        title: Content title.
        body: Content body.
        platforms: List of platform names to preview. If None, preview all.
    """
    platforms = platforms or ALL_PLATFORMS
    settings = _settings()
    result = {}

    for name in platforms:
        try:
            platform_cls = get_platform(name)
            instance = platform_cls(settings)
            content = PromotionContent(title=title, body=body)
            adapted = instance.adapt_content(content)
            result[name] = adapted
        except KeyError:
            result[name] = {"error": f"Unknown platform: {name}"}

    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(transport="stdio")
