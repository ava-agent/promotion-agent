"""Tests for Zhihu platform."""

from unittest.mock import MagicMock

import httpx

from promotion_agent.platforms.zhihu import ZhihuPlatform


class MockConfig:
    zhihu_cookie = "test_cookie"


def test_validate_config():
    platform = ZhihuPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        zhihu_cookie = None

    platform = ZhihuPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = ZhihuPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert sample_content.url in payload["content"]


def test_post_success(sample_content):
    platform = ZhihuPlatform(MockConfig())
    mock_client = MagicMock()

    # Step 1: create draft
    # Step 2: publish draft
    mock_client.post.return_value = httpx.Response(200, json={"id": "draft_789"})
    mock_client.put.return_value = httpx.Response(
        200, json={"url": "https://zhuanlan.zhihu.com/p/draft_789"}
    )
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert "draft_789" in result.url


def test_post_draft_fails(sample_content):
    platform = ZhihuPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(401, text="Unauthorized")
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "draft" in result.error.lower()
