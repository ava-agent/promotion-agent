"""Tests for X (Twitter) platform (async v4 with thread support)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import tweepy

from core.content import PromotionContent
from platforms.x_twitter import XTwitterPlatform


class MockConfig:
    x_consumer_key = "test_ck"
    x_consumer_secret = "test_cs"
    x_access_token = "test_at"
    x_access_token_secret = "test_ats"


@pytest.fixture
def platform():
    return XTwitterPlatform(MockConfig())


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
    class Empty:
        x_consumer_key = None
        x_consumer_secret = None
        x_access_token = None
        x_access_token_secret = None

    platform = XTwitterPlatform(Empty())
    assert platform.validate_config() is False


def test_validate_config_partial():
    class Partial:
        x_consumer_key = "ck"
        x_consumer_secret = None
        x_access_token = "at"
        x_access_token_secret = None

    platform = XTwitterPlatform(Partial())
    assert platform.validate_config() is False


# --- adapt_content ---


def test_adapt_single_tweet(platform, sample_content):
    """Single tweet: URL included, within 280 chars."""
    payload = platform.adapt_content(sample_content)
    assert "text" in payload
    assert "thread" not in payload or payload["thread"] is None
    assert sample_content.url in payload["text"]
    assert sample_content.title in payload["text"]
    assert len(payload["text"]) <= 280


def test_adapt_thread(platform):
    """When metadata['thread'] is present, return thread mode."""
    thread_tweets = [
        "First tweet in thread",
        "Second tweet continues",
        "Third and final tweet",
    ]
    content = PromotionContent(
        title="Thread Post",
        body="Thread body",
        tags=["ai"],
        metadata={"thread": thread_tweets},
    )
    payload = platform.adapt_content(content)
    assert payload["text"] is None
    assert payload["thread"] == thread_tweets


def test_adapt_280_limit(platform):
    """Very long title gets truncated to stay within 280 chars."""
    content = PromotionContent(
        title="A" * 300,
        body="Body",
        url="https://github.com/test",
        tags=["ai", "python", "ml"],
    )
    payload = platform.adapt_content(content)
    assert len(payload["text"]) <= 280


# --- post (async) ---


@pytest.mark.asyncio
async def test_post_single_tweet(platform, sample_content):
    """Post a single tweet successfully."""
    mock_response = MagicMock()
    mock_response.data = {"id": "1234567890"}

    mock_client = MagicMock()
    mock_client.create_tweet.return_value = mock_response
    platform._client = mock_client

    async def fake_to_thread(fn, **kwargs):
        return mock_response

    with patch("platforms.x_twitter.asyncio.to_thread", side_effect=fake_to_thread):
        result = await platform.post(sample_content)

    assert result.success is True
    assert "1234567890" in result.url
    assert result.post_id == "1234567890"


@pytest.mark.asyncio
async def test_post_thread(platform):
    """Post a 3-tweet thread, verify in_reply_to_tweet_id chain."""
    thread_tweets = [
        "First tweet in thread",
        "Second tweet continues",
        "Third and final tweet",
    ]
    content = PromotionContent(
        title="Thread",
        body="Body",
        metadata={"thread": thread_tweets},
    )

    # Mock responses for each tweet in the chain
    responses = []
    for i, tweet_id in enumerate(["100", "200", "300"]):
        resp = MagicMock()
        resp.data = {"id": tweet_id}
        responses.append(resp)

    call_count = 0

    async def fake_to_thread(fn, **kwargs):
        nonlocal call_count
        result = responses[call_count]
        call_count += 1
        return result

    mock_client = MagicMock()
    platform._client = mock_client

    with patch("platforms.x_twitter.asyncio.to_thread", side_effect=fake_to_thread):
        result = await platform.post(content)

    assert result.success is True
    # post_id should be the first tweet's ID
    assert result.post_id == "100"
    assert "100" in result.url
    # Verify 3 tweets were created
    assert call_count == 3


@pytest.mark.asyncio
async def test_post_failure(platform, sample_content):
    """TweepyException results in error PostResult with error_type."""
    mock_client = MagicMock()
    platform._client = mock_client

    async def fake_to_thread(fn, **kwargs):
        raise tweepy.TweepyException("Rate limit exceeded")

    with patch("platforms.x_twitter.asyncio.to_thread", side_effect=fake_to_thread):
        result = await platform.post(sample_content)

    assert result.success is False
    assert "Rate limit" in result.error
    assert result.error_type == "tweepy_error"
