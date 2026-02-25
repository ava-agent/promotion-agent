"""Tests for LinkedIn platform."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx

from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.linkedin import LinkedInPlatform


class MockConfig:
    linkedin_access_token = "test_li_token"


def test_validate_config():
    platform = LinkedInPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        linkedin_access_token = None

    platform = LinkedInPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content(sample_content):
    platform = LinkedInPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert sample_content.title in payload["text"]
    assert sample_content.url in payload["text"]
    assert payload["url"] == sample_content.url


def test_adapt_content_hashtags():
    content = PromotionContent(
        title="Test",
        body="Body",
        tags=["ai", "python"],
    )
    platform = LinkedInPlatform(MockConfig())
    payload = platform.adapt_content(content)
    assert "#ai" in payload["text"]
    assert "#python" in payload["text"]


def test_post_success(sample_content):
    platform = LinkedInPlatform(MockConfig())
    mock_client = MagicMock()

    userinfo_resp = httpx.Response(200, json={"sub": "person123"})
    ugc_resp = httpx.Response(200, json={"id": "urn:li:share:987654"})

    mock_client.get.return_value = userinfo_resp
    mock_client.post.return_value = ugc_resp
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert "urn:li:share:987654" in result.url
    assert result.post_id == "urn:li:share:987654"


def test_post_person_id_failure(sample_content):
    platform = LinkedInPlatform(MockConfig())
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(401, text="Unauthorized")
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "person ID" in result.error


def test_post_ugc_failure(sample_content):
    platform = LinkedInPlatform(MockConfig())
    mock_client = MagicMock()

    mock_client.get.return_value = httpx.Response(200, json={"sub": "person123"})
    mock_client.post.return_value = httpx.Response(403, text="Forbidden")
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "403" in result.error
