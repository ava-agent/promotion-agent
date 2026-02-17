"""Content data models for promotion posts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ContentFormat(Enum):
    MARKDOWN = "markdown"
    PLAIN = "plain"
    HTML = "html"


@dataclass
class PromotionContent:
    """Platform-agnostic content to be posted."""

    title: str
    body: str
    format: ContentFormat = ContentFormat.MARKDOWN
    tags: list[str] = field(default_factory=list)
    url: Optional[str] = None
    description: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    # metadata carries platform-specific hints:
    #   reddit_subreddit, reddit_link_post
    #   moltbook_submolt
    #   devto_series, devto_published
