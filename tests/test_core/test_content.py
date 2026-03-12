"""Tests for content data models."""

from core.content import ContentFormat, PromotionContent


def test_promotion_content_defaults():
    content = PromotionContent(title="Test", body="Body")
    assert content.title == "Test"
    assert content.body == "Body"
    assert content.format == ContentFormat.MARKDOWN
    assert content.tags == []
    assert content.url is None
    assert content.description is None
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
    assert content.description == "Short desc"
    assert content.metadata["reddit_subreddit"] == "test"


def test_content_format_values():
    assert ContentFormat.MARKDOWN.value == "markdown"
    assert ContentFormat.PLAIN.value == "plain"
    assert ContentFormat.HTML.value == "html"


def test_mutable_defaults_are_independent():
    """Ensure mutable default fields don't share state between instances."""
    c1 = PromotionContent(title="A", body="B")
    c2 = PromotionContent(title="C", body="D")
    c1.tags.append("tag1")
    c1.metadata["key"] = "val"
    assert c2.tags == []
    assert c2.metadata == {}
