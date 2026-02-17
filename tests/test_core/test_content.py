"""Tests for content data models."""

from promotion_agent.core.content import ContentFormat, PromotionContent


def test_promotion_content_defaults():
    content = PromotionContent(title="Test", body="Body")
    assert content.title == "Test"
    assert content.body == "Body"
    assert content.format == ContentFormat.MARKDOWN
    assert content.tags == []
    assert content.url is None
    assert content.metadata == {}


def test_promotion_content_full():
    content = PromotionContent(
        title="My Project",
        body="Description here",
        format=ContentFormat.PLAIN,
        tags=["ai", "python"],
        url="https://github.com/test",
        description="Short desc",
        metadata={"reddit_subreddit": "test"},
    )
    assert content.tags == ["ai", "python"]
    assert content.url == "https://github.com/test"
    assert content.metadata["reddit_subreddit"] == "test"
