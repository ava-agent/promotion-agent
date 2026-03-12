"""Tests for WeChat Official Account (微信公众号) proxy platform."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.content import PromotionContent
from core.proxy import MCPProxy
from platforms.wechat import WechatPlatform


class MockConfig:
    wechat_app_id = "wx_test_app_id"
    wechat_app_secret = "wx_test_app_secret"


class EmptyConfig:
    wechat_app_id = None
    wechat_app_secret = None


@pytest.fixture
def mock_proxy():
    proxy = AsyncMock(spec=MCPProxy)
    proxy.is_running = AsyncMock(return_value=True)
    proxy.ensure_running = AsyncMock()
    proxy.call_tool = AsyncMock(
        return_value={"content": [{"type": "text", "text": "Article submitted"}]}
    )
    return proxy


@pytest.fixture
def platform(mock_proxy):
    return WechatPlatform(MockConfig(), proxy=mock_proxy)


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="Test AI Article",
        body="This is the full article body for WeChat publication.",
        tags=["ai", "python"],
        url="https://github.com/kevinten10/test-project",
        description="A test AI project",
        metadata={
            "cover_image": "https://example.com/cover.png",
            "digest": "Custom digest text",
        },
    )


# --- validate_config ---


def test_validate_config_positive(platform):
    assert platform.validate_config() is True


def test_validate_config_missing_app_id():
    class Partial:
        wechat_app_id = None
        wechat_app_secret = "secret"

    platform = WechatPlatform(Partial())
    assert platform.validate_config() is False


def test_validate_config_missing_app_secret():
    class Partial:
        wechat_app_id = "app_id"
        wechat_app_secret = None

    platform = WechatPlatform(Partial())
    assert platform.validate_config() is False


def test_validate_config_both_missing():
    platform = WechatPlatform(EmptyConfig())
    assert platform.validate_config() is False


# --- adapt_content ---


def test_adapt_content_title(platform, sample_content):
    adapted = platform.adapt_content(sample_content)
    assert adapted["title"] == "Test AI Article"


def test_adapt_content_body(platform, sample_content):
    adapted = platform.adapt_content(sample_content)
    assert adapted["body"] == sample_content.body


def test_adapt_content_cover_image(platform, sample_content):
    adapted = platform.adapt_content(sample_content)
    assert adapted["cover_image"] == "https://example.com/cover.png"


def test_adapt_content_cover_image_default(platform):
    content = PromotionContent(title="No Cover", body="Body text")
    adapted = platform.adapt_content(content)
    assert adapted["cover_image"] is None


def test_adapt_content_digest_from_metadata(platform, sample_content):
    """When metadata has digest, use it."""
    adapted = platform.adapt_content(sample_content)
    assert adapted["digest"] == "Custom digest text"


def test_adapt_content_digest_fallback(platform):
    """When no digest in metadata, fallback to body[:120]."""
    body = "A" * 200
    content = PromotionContent(title="Fallback Digest", body=body)
    adapted = platform.adapt_content(content)
    assert adapted["digest"] == body[:120]


def test_adapt_content_digest_short_body(platform):
    """Short body used fully as digest fallback."""
    content = PromotionContent(title="Short", body="Short body")
    adapted = platform.adapt_content(content)
    assert adapted["digest"] == "Short body"


# --- post (async) ---


@pytest.mark.asyncio
async def test_post_success(platform, mock_proxy, sample_content):
    result = await platform.post(sample_content)

    assert result.success is True
    assert result.platform == "wechat"
    mock_proxy.ensure_running.assert_awaited_once_with("wechat")
    mock_proxy.call_tool.assert_awaited_once()
    call_args = mock_proxy.call_tool.call_args
    assert call_args[0][0] == "wechat"
    assert call_args[0][1] == "submit_article_content_prompt"


@pytest.mark.asyncio
async def test_post_proxy_not_running(sample_content):
    """When ensure_running fails, post returns error."""
    proxy = AsyncMock(spec=MCPProxy)
    proxy.ensure_running = AsyncMock(
        side_effect=TimeoutError("MCP did not start")
    )
    platform = WechatPlatform(MockConfig(), proxy=proxy)

    result = await platform.post(sample_content)

    assert result.success is False
    assert "MCP did not start" in result.error
    assert result.error_type == "proxy_error"


# --- health_check (async) ---


@pytest.mark.asyncio
async def test_health_check_delegates_to_proxy(platform, mock_proxy):
    result = await platform.health_check()
    assert result is True
    mock_proxy.is_running.assert_awaited_once_with("wechat")


@pytest.mark.asyncio
async def test_health_check_no_proxy():
    """Without a proxy, health_check returns False."""
    platform = WechatPlatform(MockConfig(), proxy=None)
    result = await platform.health_check()
    assert result is False
