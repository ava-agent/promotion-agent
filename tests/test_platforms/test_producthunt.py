"""Tests for Product Hunt platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx

from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.producthunt import ProductHuntPlatform


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


def test_post_success(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(
        200,
        json={
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
        },
    )
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert "producthunt.com" in result.url
    assert result.post_id == "ph_123"


def test_post_graphql_errors(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(
        200,
        json={
            "data": {
                "createPost": {
                    "post": None,
                    "errors": [{"field": "url", "message": "has already been taken"}],
                }
            }
        },
    )
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "already been taken" in result.error


def test_post_http_failure(sample_content):
    platform = ProductHuntPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(401, text="Unauthorized")
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "401" in result.error
