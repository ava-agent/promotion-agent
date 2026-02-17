"""Abstract base class for all platform implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from promotion_agent.core.content import PromotionContent
from promotion_agent.core.result import PostResult


class BasePlatform(ABC):
    """Abstract base class for social media platforms."""

    PLATFORM_NAME: str = ""
    DISPLAY_NAME: str = ""
    REQUIRED_CONFIG_KEYS: list[str] = []

    @abstractmethod
    def validate_config(self) -> bool:
        """Check if all required configuration is present."""
        ...

    @abstractmethod
    def post(self, content: PromotionContent) -> PostResult:
        """Publish content to the platform."""
        ...

    @abstractmethod
    def adapt_content(self, content: PromotionContent) -> dict:
        """Transform generic content into platform-specific payload."""
        ...

    def health_check(self) -> bool:
        """Verify API connectivity. Override for real checks."""
        return True
