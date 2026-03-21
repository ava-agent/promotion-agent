"""Tests for Juejin platform (async v4)."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from platforms.juejin import JuejinPlatform


class MockConfig:
    juejin_cookie = "test_cookie"


def test_validate_config():
    platform = JuejinPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        juejin_cookie = None

    platform = JuejinPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = JuejinPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert sample_content.url in payload["mark_content"]
    assert payload["edit_type"] == 10


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = JuejinPlatform(MockConfig())
    mock_client = AsyncMock()

    # Step 1: create draft returns draft_id
    draft_resp = MagicMock()
    draft_resp.json.return_value = {"err_no": 0, "data": {"id": "draft_123"}}

    # Step 2: publish returns article_id
    publish_resp = MagicMock()
    publish_resp.json.return_value = {
        "err_no": 0,
        "data": {"article_id": "article_456"},
    }

    mock_client.post.side_effect = [draft_resp, publish_resp]
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert "article_456" in result.url
    assert mock_client.post.call_count == 2


@pytest.mark.asyncio
async def test_post_draft_creation_fails(sample_content):
    platform = JuejinPlatform(MockConfig())
    mock_client = AsyncMock()

    resp = MagicMock()
    resp.json.return_value = {"err_no": 1, "err_msg": "Auth failed"}
    mock_client.post.return_value = resp
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "draft" in result.error.lower()
