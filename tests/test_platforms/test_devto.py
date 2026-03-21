"""Tests for Dev.to platform (async v4)."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from core.content import PromotionContent
from platforms.devto import DevToPlatform


class MockConfig:
    devto_api_key = "test_key"


def test_validate_config():
    platform = DevToPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class EmptyConfig:
        devto_api_key = None

    platform = DevToPlatform(EmptyConfig())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = DevToPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    article = payload["article"]
    assert article["title"] == sample_content.title
    assert article["published"] is True
    assert len(article["tags"]) <= 4
    assert sample_content.url in article["body_markdown"]


def test_adapt_content_tags_limit():
    content = PromotionContent(
        title="Test",
        body="Body",
        tags=["a", "b", "c", "d", "e"],  # 5 tags
    )
    platform = DevToPlatform(MockConfig())
    payload = platform.adapt_content(content)
    assert len(payload["article"]["tags"]) == 4


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = DevToPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = True
    response.json.return_value = {
        "id": 789,
        "url": "https://dev.to/kevinten10/test-project",
    }
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert result.url == "https://dev.to/kevinten10/test-project"


@pytest.mark.asyncio
async def test_post_failure(sample_content):
    platform = DevToPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = False
    response.status_code = 422
    response.text = "Validation failed"
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "422" in result.error
