"""Tests for CSDN platform (async v4)."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from platforms.csdn import CSDNPlatform


class MockConfig:
    csdn_cookie = "test_cookie"


def test_validate_config():
    platform = CSDNPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        csdn_cookie = None

    platform = CSDNPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = CSDNPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert sample_content.url in payload["markdowncontent"]
    assert payload["status"] == 0  # publish
    assert payload["type"] == "original"
    assert "ai,python,automation" == payload["tags"]


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = CSDNPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = True
    response.status_code = 200
    response.json.return_value = {
        "code": 200,
        "msg": "success",
        "data": {"id": "12345", "url": "https://blog.csdn.net/xxx/12345"},
    }
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert result.post_id == "12345"


@pytest.mark.asyncio
async def test_post_failure(sample_content):
    platform = CSDNPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = False
    response.status_code = 403
    response.text = "Forbidden"
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "403" in result.error
