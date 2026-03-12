"""Tests for Zhihu platform (async v4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from core.content import PromotionContent
from platforms.zhihu import ZhihuPlatform


class MockConfig:
    zhihu_cookie = "test_cookie"


class EmptyConfig:
    zhihu_cookie = None


@pytest.fixture
def platform():
    return ZhihuPlatform(MockConfig())


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="Test Project - AI Tool",
        body="This is a test project for AI automation.",
        tags=["ai", "python", "automation"],
        url="https://github.com/kevinten10/test-project",
        description="A test AI project",
    )


# --- validate_config ---


def test_validate_config_positive(platform):
    assert platform.validate_config() is True


def test_validate_config_negative():
    platform = ZhihuPlatform(EmptyConfig())
    assert platform.validate_config() is False


# --- adapt_content ---


def test_adapt_content_title_preserved(platform, sample_content):
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title


def test_adapt_content_url_appended(platform, sample_content):
    payload = platform.adapt_content(sample_content)
    assert sample_content.url in payload["content"]


# --- post (async) ---


@pytest.mark.asyncio
async def test_post_success(platform, sample_content):
    mock_client = AsyncMock()

    # Step 1: create draft returns id
    draft_response = MagicMock()
    draft_response.is_success = True
    draft_response.json.return_value = {"id": "draft_789"}
    mock_client.post.return_value = draft_response

    # Step 2: publish draft returns url
    publish_response = MagicMock()
    publish_response.is_success = True
    publish_response.json.return_value = {
        "url": "https://zhuanlan.zhihu.com/p/draft_789"
    }
    mock_client.put.return_value = publish_response

    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is True
    assert "draft_789" in result.url
    assert result.post_id == "draft_789"


@pytest.mark.asyncio
async def test_post_draft_fails(platform, sample_content):
    mock_client = AsyncMock()

    # Draft creation fails
    draft_response = MagicMock()
    draft_response.is_success = False
    draft_response.text = "Unauthorized"
    draft_response.status_code = 401
    mock_client.post.return_value = draft_response

    platform._client = mock_client

    result = await platform.post(sample_content)
    assert result.success is False
    assert "draft" in result.error.lower()
    assert result.error_type == "draft_creation_failed"


# --- health_check (async) ---


@pytest.mark.asyncio
async def test_health_check_success(platform):
    mock_client = AsyncMock()

    health_response = MagicMock()
    health_response.is_success = True
    mock_client.get.return_value = health_response

    platform._client = mock_client

    result = await platform.health_check()
    assert result is True
