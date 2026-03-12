"""Tests for Xiaohongshu (小红书) proxy platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.content import PromotionContent
from core.proxy import MCPProxy
from platforms.xiaohongshu import XiaohongshuPlatform


class MockConfig:
    pass


@pytest.fixture
def mock_proxy():
    proxy = AsyncMock(spec=MCPProxy)
    proxy.is_running = AsyncMock(return_value=True)
    proxy.ensure_running = AsyncMock()
    proxy.call_tool = AsyncMock(
        return_value={"content": [{"type": "text", "text": "Published note_123"}]}
    )
    return proxy


@pytest.fixture
def platform(mock_proxy):
    return XiaohongshuPlatform(MockConfig(), proxy=mock_proxy)


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="Test Project - AI Tool",
        body="This is a test project for AI automation.",
        tags=["ai", "python", "automation"],
        url="https://github.com/kevinten10/test-project",
        description="A test AI project",
        metadata={"images": ["https://example.com/img1.png"]},
    )


# --- validate_config ---


def test_validate_config_always_true(platform):
    """Auth is managed by external MCP, so validate always returns True."""
    assert platform.validate_config() is True


# --- adapt_content ---


def test_adapt_content_title_truncated(platform):
    """Title must be <=20 chars for Xiaohongshu."""
    content = PromotionContent(
        title="This is a very long title that exceeds twenty characters",
        body="Body text",
    )
    adapted = platform.adapt_content(content)
    assert len(adapted["title"]) <= 20


def test_adapt_content_short_title(platform, sample_content):
    """Short titles are preserved as-is."""
    content = PromotionContent(title="Short Title", body="Body text")
    adapted = platform.adapt_content(content)
    assert adapted["title"] == "Short Title"


def test_adapt_content_body(platform, sample_content):
    adapted = platform.adapt_content(sample_content)
    assert adapted["body"] == sample_content.body


def test_adapt_content_images(platform, sample_content):
    adapted = platform.adapt_content(sample_content)
    assert adapted["images"] == ["https://example.com/img1.png"]


def test_adapt_content_images_default(platform):
    content = PromotionContent(title="No Images", body="Body")
    adapted = platform.adapt_content(content)
    assert adapted["images"] == []


def test_adapt_content_tags(platform, sample_content):
    adapted = platform.adapt_content(sample_content)
    assert adapted["tags"] == ["ai", "python", "automation"]


# --- post (async) ---


@pytest.mark.asyncio
async def test_post_success(platform, mock_proxy, sample_content):
    result = await platform.post(sample_content)

    assert result.success is True
    assert result.platform == "xiaohongshu"
    mock_proxy.ensure_running.assert_awaited_once_with("xiaohongshu")
    mock_proxy.call_tool.assert_awaited_once()
    call_args = mock_proxy.call_tool.call_args
    assert call_args[0][0] == "xiaohongshu"
    assert call_args[0][1] == "publish_note"


@pytest.mark.asyncio
async def test_post_proxy_not_running(sample_content):
    """When ensure_running raises, post returns error."""
    proxy = AsyncMock(spec=MCPProxy)
    proxy.ensure_running = AsyncMock(
        side_effect=TimeoutError("MCP did not start")
    )
    platform = XiaohongshuPlatform(MockConfig(), proxy=proxy)

    result = await platform.post(sample_content)

    assert result.success is False
    assert "MCP did not start" in result.error
    assert result.error_type == "proxy_error"


# --- health_check (async) ---


@pytest.mark.asyncio
async def test_health_check_delegates_to_proxy(platform, mock_proxy):
    result = await platform.health_check()
    assert result is True
    mock_proxy.is_running.assert_awaited_once_with("xiaohongshu")


@pytest.mark.asyncio
async def test_health_check_no_proxy():
    """Without a proxy, health_check returns False."""
    platform = XiaohongshuPlatform(MockConfig(), proxy=None)
    result = await platform.health_check()
    assert result is False
