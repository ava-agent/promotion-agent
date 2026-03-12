"""promotion-agent MCP Server — 10 tools for social media publishing.

Tools:
  Publish (4): publish_zhihu, publish_x, publish_xiaohongshu, publish_wechat
  Auth (4):    auth_status, auth_set_cookie, auth_qr_login, auth_health_check
  Utility (2): list_platforms, preview_content

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
import platforms.zhihu  # noqa: F401
import platforms.x_twitter  # noqa: F401
import platforms.xiaohongshu  # noqa: F401
import platforms.wechat  # noqa: F401

from core.registry import get_platform, list_platforms as registry_list_platforms

# ---------------------------------------------------------------------------
# FastMCP app
# ---------------------------------------------------------------------------

app = FastMCP("promotion-agent")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Publish tools (4)
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
    topics = topics or []
    settings = _settings()
    platform_cls = get_platform("zhihu")
    platform = platform_cls(settings)

    content = PromotionContent(
        title=title,
        body=body,
        format=ContentFormat.MARKDOWN,
        metadata={"zhihu_column": column, "zhihu_topics": topics},
    )

    adapted = platform.adapt_content(content)

    if dry_run:
        return {"dry_run": True, "platform": "zhihu", "adapted": adapted}

    result = await platform.post(content)
    return asdict(result)


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
    thread = thread or []
    hashtags = hashtags or []
    settings = _settings()
    platform_cls = get_platform("x")
    platform = platform_cls(settings)

    metadata = {}
    if thread:
        metadata["thread"] = thread

    content = PromotionContent(
        title=text,
        body=text,
        format=ContentFormat.PLAIN,
        tags=hashtags,
        url=url or None,
        metadata=metadata,
    )

    adapted = platform.adapt_content(content)

    if dry_run:
        return {"dry_run": True, "platform": "x", "adapted": adapted}

    result = await platform.post(content)
    return asdict(result)


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
    images = images or []
    tags = tags or []
    settings = _settings()
    platform_cls = get_platform("xiaohongshu")
    platform = platform_cls(settings)

    content = PromotionContent(
        title=title,
        body=body,
        format=ContentFormat.MARKDOWN,
        tags=tags,
        metadata={"images": images},
    )

    adapted = platform.adapt_content(content)

    if dry_run:
        return {"dry_run": True, "platform": "xiaohongshu", "adapted": adapted}

    result = await platform.post(content)
    return asdict(result)


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
    settings = _settings()
    platform_cls = get_platform("wechat")
    platform = platform_cls(settings)

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

    adapted = platform.adapt_content(content)

    if dry_run:
        return {"dry_run": True, "platform": "wechat", "adapted": adapted}

    result = await platform.post(content)
    return asdict(result)


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
        platform: Platform name (e.g. 'zhihu').
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
        platform: Platform name to check (zhihu, x, xiaohongshu, wechat).
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
        result.append({
            "name": name,
            "display_name": cls.DISPLAY_NAME,
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
    platforms = platforms or ["zhihu", "x", "xiaohongshu", "wechat"]
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
