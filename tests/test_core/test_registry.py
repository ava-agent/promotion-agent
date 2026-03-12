"""Tests for platform registry."""

import pytest

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.result import PostResult
from core.registry import (
    _PLATFORM_REGISTRY,
    get_platform,
    list_platforms,
    register_platform,
)


def test_register_and_get_platform():
    @register_platform
    class _TestPlatform(BasePlatform):
        PLATFORM_NAME = "_test_registry"
        DISPLAY_NAME = "Test"
        REQUIRED_CONFIG_KEYS = []

        def validate_config(self):
            return True

        async def post(self, content):
            return PostResult(platform=self.PLATFORM_NAME, success=True)

        def adapt_content(self, content):
            return {}

    assert "_test_registry" in _PLATFORM_REGISTRY
    cls = get_platform("_test_registry")
    assert cls is _TestPlatform

    # Cleanup
    del _PLATFORM_REGISTRY["_test_registry"]


def test_get_unknown_platform():
    with pytest.raises(KeyError, match="Unknown platform"):
        get_platform("nonexistent_platform_xyz")


def test_list_platforms_returns_dict():
    initial = list_platforms()
    assert isinstance(initial, dict)


def test_register_multiple_platforms():
    @register_platform
    class _PlatformA(BasePlatform):
        PLATFORM_NAME = "_test_a"
        DISPLAY_NAME = "A"
        REQUIRED_CONFIG_KEYS = []

        def validate_config(self):
            return True

        async def post(self, content):
            return PostResult(platform=self.PLATFORM_NAME, success=True)

        def adapt_content(self, content):
            return {}

    @register_platform
    class _PlatformB(BasePlatform):
        PLATFORM_NAME = "_test_b"
        DISPLAY_NAME = "B"
        REQUIRED_CONFIG_KEYS = []

        def validate_config(self):
            return True

        async def post(self, content):
            return PostResult(platform=self.PLATFORM_NAME, success=True)

        def adapt_content(self, content):
            return {}

    platforms = list_platforms()
    assert "_test_a" in platforms
    assert "_test_b" in platforms

    # Cleanup
    del _PLATFORM_REGISTRY["_test_a"]
    del _PLATFORM_REGISTRY["_test_b"]


def test_list_platforms_returns_copy():
    """list_platforms returns a copy, not the internal registry."""
    platforms = list_platforms()
    platforms["fake"] = None
    assert "fake" not in _PLATFORM_REGISTRY
