"""Tests for MoltBook platform."""

from unittest.mock import MagicMock, PropertyMock, patch

import httpx

from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.moltbook import MoltBookPlatform


class MockConfig:
    moltbook_api_key = "test_key"
    moltbook_default_submolt = "general"


def test_validate_config():
    platform = MoltBookPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class EmptyConfig:
        moltbook_api_key = None
        moltbook_default_submolt = "general"

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


def test_post_success(sample_content):
    platform = MoltBookPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(
        200,
        json={"id": "123", "url": "https://moltbook.com/posts/123"},
    )
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert result.url == "https://moltbook.com/posts/123"
    assert result.post_id == "123"


def test_post_with_challenge(sample_content):
    platform = MoltBookPlatform(MockConfig())
    mock_client = MagicMock()

    # First call returns challenge, second call verifies
    mock_client.post.side_effect = [
        httpx.Response(
            202,
            json={"challenge": "initial velocity 10 cm/s, accelerate by 5 cm/s^2"},
        ),
        httpx.Response(
            200,
            json={"id": "456", "url": "https://moltbook.com/posts/456"},
        ),
    ]
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert result.post_id == "456"


def test_post_failure(sample_content):
    platform = MoltBookPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(403, text="Forbidden")
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "403" in result.error


def test_solve_challenge():
    platform = MoltBookPlatform(MockConfig())
    answer = platform._solve_challenge(
        "initial velocity 10 cm/s, accelerate by 5 cm/s^2"
    )
    assert answer == 15.0
