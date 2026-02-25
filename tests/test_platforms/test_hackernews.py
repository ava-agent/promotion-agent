"""Tests for Hacker News platform."""

from __future__ import annotations

from unittest.mock import MagicMock

from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.hackernews import HackerNewsPlatform


class MockConfig:
    hn_username = "test_user"
    hn_password = "test_pass"


def test_validate_config():
    platform = HackerNewsPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        hn_username = None
        hn_password = None

    platform = HackerNewsPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content_link_post(sample_content):
    platform = HackerNewsPlatform(MockConfig())
    payload = platform.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert payload["url"] == sample_content.url
    assert "text" not in payload


def test_adapt_content_text_post():
    content = PromotionContent(
        title="Ask HN: Best AI tools?",
        body="What are the best AI tools for developers?",
    )
    platform = HackerNewsPlatform(MockConfig())
    payload = platform.adapt_content(content)
    assert payload["title"] == content.title
    assert "text" in payload
    assert "url" not in payload


def test_adapt_content_title_truncation():
    content = PromotionContent(title="A" * 100, body="Body")
    platform = HackerNewsPlatform(MockConfig())
    payload = platform.adapt_content(content)
    assert len(payload["title"]) == 80


def test_post_login_failure(sample_content):
    platform = HackerNewsPlatform(MockConfig())
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.cookies = {}
    mock_client.post.return_value = mock_resp
    mock_client.cookies = {}
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "Login failed" in result.error


def test_post_fnid_extraction_failure(sample_content):
    platform = HackerNewsPlatform(MockConfig())
    mock_client = MagicMock()

    login_resp = MagicMock()
    login_resp.cookies = {"user": "abc123"}
    submit_resp = MagicMock()
    submit_resp.is_success = True
    submit_resp.text = "<html><body>No form here</body></html>"

    mock_client.post.return_value = login_resp
    mock_client.get.return_value = submit_resp
    mock_client.cookies = {}
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "fnid" in result.error.lower()


def test_post_success(sample_content):
    platform = HackerNewsPlatform(MockConfig())
    mock_client = MagicMock()

    login_resp = MagicMock()
    login_resp.cookies = {"user": "abc123"}

    submit_resp = MagicMock()
    submit_resp.is_success = True
    submit_resp.text = '<input type="hidden" name="fnid" value="TOKEN123">'

    post_resp = MagicMock()
    post_resp.status_code = 200
    post_resp.url = "https://news.ycombinator.com/newest"
    post_resp.text = ""

    mock_client.post.side_effect = [login_resp, post_resp]
    mock_client.get.return_value = submit_resp
    mock_client.cookies = {}
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is True
    assert "newest" in result.url


def test_post_rate_limited(sample_content):
    platform = HackerNewsPlatform(MockConfig())
    mock_client = MagicMock()

    login_resp = MagicMock()
    login_resp.cookies = {"user": "abc123"}

    submit_resp = MagicMock()
    submit_resp.is_success = True
    submit_resp.text = '<input type="hidden" name="fnid" value="TOKEN123">'

    post_resp = MagicMock()
    post_resp.status_code = 200
    post_resp.url = "https://news.ycombinator.com/submit"
    post_resp.text = "Please slow down. You're submitting too fast."

    mock_client.post.side_effect = [login_resp, post_resp]
    mock_client.get.return_value = submit_resp
    mock_client.cookies = {}
    platform._client = mock_client

    result = platform.post(sample_content)
    assert result.success is False
    assert "Rate limited" in result.error
