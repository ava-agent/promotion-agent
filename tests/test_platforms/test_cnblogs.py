"""Tests for CNBlogs platform (async v4 with to_thread)."""

from unittest.mock import MagicMock, patch

import pytest

from platforms.cnblogs import CNBlogsPlatform


class MockConfig:
    cnblogs_blog_url = "test_blog"
    cnblogs_username = "test_user"
    cnblogs_token = "test_token"


def test_validate_config():
    platform = CNBlogsPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        cnblogs_blog_url = None
        cnblogs_username = None
        cnblogs_token = None

    platform = CNBlogsPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = CNBlogsPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert sample_content.url in payload["description"]
    assert payload["mt_keywords"] == "ai,python,automation"


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = CNBlogsPlatform(MockConfig())
    mock_proxy = MagicMock()
    mock_proxy.metaWeblog.newPost.return_value = "12345678"
    platform._proxy = mock_proxy

    result = await platform.post(sample_content)
    assert result.success is True
    assert "12345678" in result.url
    assert result.post_id == "12345678"
    mock_proxy.metaWeblog.newPost.assert_called_once()


@pytest.mark.asyncio
async def test_post_failure(sample_content):
    import xmlrpc.client

    platform = CNBlogsPlatform(MockConfig())
    mock_proxy = MagicMock()
    mock_proxy.metaWeblog.newPost.side_effect = xmlrpc.client.Fault(
        403, "Token expired"
    )
    platform._proxy = mock_proxy

    result = await platform.post(sample_content)
    assert result.success is False
    assert "Token expired" in result.error
