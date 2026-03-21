"""Tests for LinkedIn platform (async v4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from core.content import PromotionContent
from platforms.linkedin import LinkedInPlatform


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


@pytest.mark.asyncio
async def test_post_success(sample_content):
    platform = LinkedInPlatform(MockConfig())
    mock_client = AsyncMock()

    userinfo_resp = MagicMock()
    userinfo_resp.is_success = True
    userinfo_resp.json.return_value = {"sub": "person123"}

    ugc_resp = MagicMock()
    ugc_resp.is_success = True
    ugc_resp.json.return_value = {"id": "urn:li:share:987654"}

    mock_client.get.return_value = userinfo_resp
    mock_client.post.return_value = ugc_resp
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert "urn:li:share:987654" in result.url
    assert result.post_id == "urn:li:share:987654"


@pytest.mark.asyncio
async def test_post_person_id_failure(sample_content):
    platform = LinkedInPlatform(MockConfig())
    mock_client = AsyncMock()

    resp = MagicMock()
    resp.is_success = False
    resp.status_code = 401
    resp.text = "Unauthorized"
    mock_client.get.return_value = resp
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "person ID" in result.error


@pytest.mark.asyncio
async def test_post_ugc_failure(sample_content):
    platform = LinkedInPlatform(MockConfig())
    mock_client = AsyncMock()

    userinfo_resp = MagicMock()
    userinfo_resp.is_success = True
    userinfo_resp.json.return_value = {"sub": "person123"}
    mock_client.get.return_value = userinfo_resp

    ugc_resp = MagicMock()
    ugc_resp.is_success = False
    ugc_resp.status_code = 403
    ugc_resp.text = "Forbidden"
    mock_client.post.return_value = ugc_resp
    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "403" in result.error
