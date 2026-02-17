"""Platform-specific content adaptation utilities."""

from promotion_agent.core.content import PromotionContent


def adapt_for_reddit(content: PromotionContent) -> PromotionContent:
    """Adapt content for Reddit conventions."""
    # Truncate title to Reddit's 300-char limit
    title = content.title[:300]
    # Add flair-style tags at the end if present
    body = content.body
    if content.tags:
        tag_line = " | ".join(f"#{t}" for t in content.tags)
        body = f"{body}\n\n---\n{tag_line}"
    return PromotionContent(
        title=title,
        body=body,
        tags=content.tags,
        url=content.url,
        description=content.description,
        metadata=content.metadata,
    )


def adapt_for_devto(content: PromotionContent) -> PromotionContent:
    """Adapt content for Dev.to conventions."""
    # Dev.to allows max 4 tags, lowercase, no spaces
    tags = [t.lower().replace(" ", "") for t in content.tags[:4]]
    return PromotionContent(
        title=content.title,
        body=content.body,
        tags=tags,
        url=content.url,
        description=content.description or content.title[:100],
        metadata=content.metadata,
    )


def adapt_for_moltbook(content: PromotionContent) -> PromotionContent:
    """Adapt content for MoltBook conventions."""
    # MoltBook is AI-focused, keep content technical
    return PromotionContent(
        title=content.title,
        body=content.body,
        tags=content.tags,
        url=content.url,
        description=content.description,
        metadata=content.metadata,
    )
