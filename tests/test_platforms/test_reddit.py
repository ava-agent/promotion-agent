"""Tests for Reddit platform."""

from unittest.mock import MagicMock, patch

from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.reddit import RedditPlatform


class MockConfig:
    reddit_client_id = "test_id"
    reddit_client_secret = "test_secret"
    reddit_username = "test_user"
    reddit_password = "test_pass"
    reddit_user_agent = "test-agent:v0.1"
    reddit_default_subreddit = "test"


def test_validate_config():
    platform = RedditPlatform(MockConfig())
    assert platform.validate_config() is True


def test_validate_config_missing():
    class Empty:
        reddit_client_id = None
        reddit_client_secret = None
        reddit_username = None
        reddit_password = None
        reddit_user_agent = None
        reddit_default_subreddit = "test"

    platform = RedditPlatform(Empty())
    assert platform.validate_config() is False


def test_adapt_content_selftext():
    platform = RedditPlatform(MockConfig())
    content = PromotionContent(
        title="Test Project",
        body="Description here",
        url="https://github.com/test",
        metadata={"reddit_subreddit": "Python"},
    )
    payload = platform.adapt_content(content)
    assert payload["subreddit"] == "Python"
    assert payload["title"] == "Test Project"
    assert "selftext" in payload
    assert "https://github.com/test" in payload["selftext"]


def test_adapt_content_link_post():
    platform = RedditPlatform(MockConfig())
    content = PromotionContent(
        title="Test Project",
        body="Description",
        url="https://github.com/test",
        metadata={"reddit_subreddit": "Python", "reddit_link_post": True},
    )
    payload = platform.adapt_content(content)
    assert "url" in payload
    assert payload["url"] == "https://github.com/test"


def test_title_truncation():
    platform = RedditPlatform(MockConfig())
    long_title = "A" * 500
    content = PromotionContent(title=long_title, body="Body")
    payload = platform.adapt_content(content)
    assert len(payload["title"]) == 300


@patch("promotion_agent.platforms.reddit.praw.Reddit")
def test_post_success(mock_reddit_cls):
    mock_submission = MagicMock()
    mock_submission.permalink = "/r/test/comments/abc123/test/"
    mock_submission.id = "abc123"

    mock_subreddit = MagicMock()
    mock_subreddit.submit.return_value = mock_submission

    mock_instance = mock_reddit_cls.return_value
    mock_instance.subreddit.return_value = mock_subreddit

    platform = RedditPlatform(MockConfig())
    content = PromotionContent(
        title="Test",
        body="Test body",
        metadata={"reddit_subreddit": "test"},
    )
    result = platform.post(content)
    assert result.success is True
    assert "abc123" in result.url
    assert result.post_id == "abc123"


@patch("promotion_agent.platforms.reddit.praw.Reddit")
def test_post_failure(mock_reddit_cls):
    mock_subreddit = MagicMock()
    mock_subreddit.submit.side_effect = Exception("Rate limited")

    mock_instance = mock_reddit_cls.return_value
    mock_instance.subreddit.return_value = mock_subreddit

    platform = RedditPlatform(MockConfig())
    content = PromotionContent(
        title="Test",
        body="Body",
        metadata={"reddit_subreddit": "test"},
    )
    result = platform.post(content)
    assert result.success is False
    assert "Rate limited" in result.error
