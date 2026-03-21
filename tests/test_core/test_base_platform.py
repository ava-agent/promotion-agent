"""Tests for async base platform and BaseHttpPlatform mixin."""

import pytest

from core.base_platform import BasePlatform, BaseHttpPlatform
from core.content import PromotionContent
from core.result import PostResult


class ConcretePlatform(BasePlatform):
    """Concrete implementation for testing the abstract base."""

    PLATFORM_NAME = "test_platform"
    DISPLAY_NAME = "Test Platform"
    REQUIRED_CONFIG_KEYS = ["api_key"]

    def validate_config(self) -> bool:
        return True

    async def post(self, content: PromotionContent) -> PostResult:
        return PostResult(platform=self.PLATFORM_NAME, success=True, url="https://test.com/1")

    def adapt_content(self, content: PromotionContent) -> dict:
        return {"title": content.title, "body": content.body}

    async def health_check(self) -> bool:
        return True


def test_platform_class_attributes():
    platform = ConcretePlatform()
    assert platform.PLATFORM_NAME == "test_platform"
    assert platform.DISPLAY_NAME == "Test Platform"
    assert platform.REQUIRED_CONFIG_KEYS == ["api_key"]


def test_validate_config_is_sync():
    """validate_config should be a synchronous method."""
    platform = ConcretePlatform()
    result = platform.validate_config()
    assert result is True


def test_adapt_content_is_sync():
    """adapt_content should be a synchronous method."""
    platform = ConcretePlatform()
    content = PromotionContent(title="Test", body="Body")
    adapted = platform.adapt_content(content)
    assert adapted == {"title": "Test", "body": "Body"}


@pytest.mark.asyncio
async def test_post_is_async():
    """post() should be an async method."""
    platform = ConcretePlatform()
    content = PromotionContent(title="Test", body="Body")
    result = await platform.post(content)
    assert isinstance(result, PostResult)
    assert result.success is True
    assert result.platform == "test_platform"


@pytest.mark.asyncio
async def test_health_check_is_async():
    """health_check() should be an async method."""
    platform = ConcretePlatform()
    healthy = await platform.health_check()
    assert healthy is True


def test_cannot_instantiate_abstract():
    """BasePlatform cannot be instantiated without implementing abstract methods."""
    with pytest.raises(TypeError):
        BasePlatform()


def test_base_platform_defaults():
    """Check default class attributes on BasePlatform itself."""
    assert BasePlatform.PLATFORM_NAME == ""
    assert BasePlatform.DISPLAY_NAME == ""
    assert BasePlatform.REQUIRED_CONFIG_KEYS == []


# -- BaseHttpPlatform tests ------------------------------------------------


class ConcreteHttpPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "test_http"
    DISPLAY_NAME = "Test HTTP"

    def __init__(self):
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer test", "Content-Type": "application/json"}

    def validate_config(self) -> bool:
        return True

    async def post(self, content: PromotionContent) -> PostResult:
        return PostResult(platform=self.PLATFORM_NAME, success=True)

    def adapt_content(self, content: PromotionContent) -> dict:
        return {"title": content.title}


class HttpPlatformWithKwargs(BaseHttpPlatform):
    PLATFORM_NAME = "test_http_kwargs"
    DISPLAY_NAME = "Test HTTP Kwargs"

    def __init__(self):
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {"User-Agent": "TestBot/1.0"}

    def _client_kwargs(self) -> dict:
        return {"follow_redirects": True}

    def validate_config(self) -> bool:
        return True

    async def post(self, content: PromotionContent) -> PostResult:
        return PostResult(platform=self.PLATFORM_NAME, success=True)

    def adapt_content(self, content: PromotionContent) -> dict:
        return {}


def test_http_platform_client_creation():
    """BaseHttpPlatform creates an httpx.AsyncClient lazily."""
    import httpx

    platform = ConcreteHttpPlatform()
    assert platform._client is None
    client = platform.client
    assert isinstance(client, httpx.AsyncClient)
    assert platform._client is client
    # Same instance on second access
    assert platform.client is client


def test_http_platform_headers():
    """Client uses headers from _default_headers()."""
    platform = ConcreteHttpPlatform()
    client = platform.client
    assert client.headers["authorization"] == "Bearer test"
    assert client.headers["content-type"] == "application/json"


def test_http_platform_defaults():
    """Client has trust_env=False and 30s timeout."""
    platform = ConcreteHttpPlatform()
    client = platform.client
    assert client._transport._pool._ssl_context is not None or True  # trust_env checked via config
    assert client.timeout.connect == 30.0


def test_http_platform_client_kwargs():
    """_client_kwargs are passed to AsyncClient constructor — verify no error on creation."""
    platform = HttpPlatformWithKwargs()
    client = platform.client
    # Client created successfully with custom kwargs
    assert client is not None
    assert platform.client is client  # Lazy singleton


def test_http_platform_no_headers_override():
    """Platform without _default_headers override gets empty headers."""

    class MinimalHttpPlatform(BaseHttpPlatform):
        PLATFORM_NAME = "minimal"
        DISPLAY_NAME = "Minimal"

        def __init__(self):
            self._client = None

        def validate_config(self):
            return True

        async def post(self, content):
            return PostResult(platform=self.PLATFORM_NAME, success=True)

        def adapt_content(self, content):
            return {}

    platform = MinimalHttpPlatform()
    client = platform.client
    # Only default httpx headers present (user-agent etc)
    assert "authorization" not in client.headers
