"""Abstract base class for all platform implementations (async)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.content import PromotionContent
from core.result import PostResult


class BasePlatform(ABC):
    """Abstract base class for social media platforms.

    In v4, post() and health_check() are async to support non-blocking I/O
    within the MCP server event loop. validate_config() and adapt_content()
    remain synchronous as they are pure computation.
    """

    PLATFORM_NAME: str = ""
    DISPLAY_NAME: str = ""
    REQUIRED_CONFIG_KEYS: list[str] = []

    @abstractmethod
    def validate_config(self) -> bool:
        """Check if all required configuration is present."""
        ...

    @abstractmethod
    async def post(self, content: PromotionContent) -> PostResult:
        """Publish content to the platform."""
        ...

    @abstractmethod
    def adapt_content(self, content: PromotionContent) -> dict:
        """Transform generic content into platform-specific payload."""
        ...

    async def health_check(self) -> bool:
        """Verify API connectivity. Override for real checks."""
        return True
