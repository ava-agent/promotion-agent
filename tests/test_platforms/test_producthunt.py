"""Tests for Product Hunt platform (async v4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from core.content import PromotionContent
from platforms.producthunt import ProductHuntPlatform


class MockConfig:
    producthunt_token = "test_ph_token"


def test_validate_config():
    platform = ProductHuntPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        producthunt_token = None

    platform = ProductHuntPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["name"] == sample_content.title
    assert payload["url"] == sample_content.url
    assert len(payload["tagline"]) <= 60


def test_adapt_content_tagline_truncation():
    content = PromotionContent(
        title="Test",
        body="Body",
        description="A" * 100,
    )
    platform = ProductHuntPlatform(MockConfig())
    payload = platform.adapt_content(content)
    assert len(payload["tagline"]) <= 60
    assert payload["tagline"].endswith("...")


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = True
    response.json.return_value = {
        "data": {
            "createPost": {
                "post": {
                    "id": "ph_123",
                    "slug": "test-project",
                    "url": "https://www.producthunt.com/posts/test-project",
                },
                "errors": None,
            }
        }
    }
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert "producthunt.com" in result.url
    assert result.post_id == "ph_123"


@pytest.mark.asyncio
async def test_post_graphql_errors(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = True
    response.json.return_value = {
        "data": {
            "createPost": {
                "post": None,
                "errors": [{"field": "url", "message": "has already been taken"}],
            }
        }
    }
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "already been taken" in result.error


@pytest.mark.asyncio
async def test_post_http_failure(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    mock_client = AsyncMock()

    response = MagicMock()
    response.is_success = False
    response.status_code = 401
    response.text = "Unauthorized"
    mock_client.post.return_value = response
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "401" in result.error
