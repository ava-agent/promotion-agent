"""Tests for X (Twitter) platform."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import tweepy

from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.x_twitter import XTwitterPlatform


class MockConfig:
    x_consumer_key = "test_ck"
    x_consumer_secret = "test_cs"
    x_access_token = "test_at"
    x_access_token_secret = "test_ats"


def test_validate_config():
    platform = XTwitterPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
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


def test_adapt_content(sample_content):
    platform = XTwitterPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert "text" in payload
    assert sample_content.title in payload["text"]
    assert sample_content.url in payload["text"]


def test_adapt_content_280_limit():
    content = PromotionContent(
        title="A" * 300,
        body="Body",
        url="https://github.com/test",
        tags=["ai", "python", "ml"],
    )
    platform = XTwitterPlatform(MockConfig())
    payload = platform.adapt_content(content)
    assert len(payload["text"]) <= 280


def test_adapt_content_hashtags(sample_content):
    platform = XTwitterPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert "#ai" in payload["text"]


def test_post_success(sample_content):
    platform = XTwitterPlatform(MockConfig())

    mock_response = MagicMock()
    mock_response.data = {"id": "1234567890"}

    mock_client = MagicMock()
    mock_client.create_tweet.return_value = mock_response
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert "1234567890" in result.url
    assert result.post_id == "1234567890"


def test_post_failure(sample_content):
    platform = XTwitterPlatform(MockConfig())

    mock_client = MagicMock()
    mock_client.create_tweet.side_effect = tweepy.TweepyException("Rate limit exceeded")
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "Rate limit" in result.error
