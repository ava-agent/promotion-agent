"""Tests for MoltBook platform (async v4)."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from platforms.moltbook import MoltBookPlatform


class MockConfig:
    moltbook_api_key = "test_key"


def test_validate_config():
    platform = MoltBookPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class EmptyConfig:
        moltbook_api_key = None

    platform = MoltBookPlatform(EmptyConfig())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = MoltBookPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert "content" in payload
    assert sample_content.url in payload["content"]
    assert payload["submolt"] == "general"


def test_adapt_content_custom_submolt(moltbook_content):
    platform = MoltBookPlatform(MockConfig())
    payload = platform.adapt_content(moltbook_content)
    assert payload["submolt"] == "ai-agents"


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = MoltBookPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = True
    response.status_code = 200
    response.json.return_value = {"id": "123", "url": "https://moltbook.com/posts/123"}
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert result.url == "https://moltbook.com/posts/123"
    assert result.post_id == "123"


@pytest.mark.asyncio
async def test_post_with_challenge(sample_content):
    platform = MoltBookPlatform(MockConfig())
    mock_client = AsyncMock()

    challenge_resp = MagicMock()
    challenge_resp.is_success = False
    challenge_resp.status_code = 202
    challenge_resp.json.return_value = {
        "challenge": "initial velocity 10 cm/s, accelerate by 5 cm/s^2"
    }

    verify_resp = MagicMock()
    verify_resp.is_success = True
    verify_resp.json.return_value = {"id": "456", "url": "https://moltbook.com/posts/456"}

    mock_client.post.side_effect = [challenge_resp, verify_resp]
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert result.post_id == "456"


@pytest.mark.asyncio
async def test_post_failure(sample_content):
    platform = MoltBookPlatform(MockConfig())
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


def test_solve_challenge():
    platform = MoltBookPlatform(MockConfig())
    answer = platform._solve_challenge(
        "initial velocity 10 cm/s, accelerate by 5 cm/s^2"
    )
    assert answer == 15.0
