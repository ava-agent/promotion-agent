"""Tests for async base platform."""

import pytest

from core.base_platform import BasePlatform
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
