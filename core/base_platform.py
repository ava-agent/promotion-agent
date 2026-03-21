"""Abstract base class for all platform implementations (async)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import httpx

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


class BaseHttpPlatform(BasePlatform):
    """BasePlatform with a built-in lazy httpx.AsyncClient.

    Subclasses must:
      - Set ``self._client = None`` in ``__init__``
      - Override ``_default_headers()`` to return platform-specific headers

    Optionally override ``_client_kwargs()`` to customize base_url,
    follow_redirects, or other httpx.AsyncClient constructor args.
    """

    _client: Optional[httpx.AsyncClient] = None

    def _default_headers(self) -> dict[str, str]:
        """Override to provide platform-specific HTTP headers."""
        return {}

    def _client_kwargs(self) -> dict:
        """Override to provide extra httpx.AsyncClient constructor args."""
        return {}

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=self._default_headers(),
                timeout=30.0,
                trust_env=False,
                **self._client_kwargs(),
            )
        return self._client
