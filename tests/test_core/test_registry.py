"""Tests for platform registry."""

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.registry import (
    _PLATFORM_REGISTRY,
    get_platform,
    list_platforms,
    register_platform,
)
from promotion_agent.core.result import PostResult


def test_register_and_get_platform():
    @register_platform
    class _TestPlatform(BasePlatform):
        PLATFORM_NAME = "_test_registry"
        DISPLAY_NAME = "Test"
        REQUIRED_CONFIG_KEYS = []

        def validate_config(self):
            return True

        def post(self, content):
            return PostResult(platform=self.PLATFORM_NAME, success=True)

        def adapt_content(self, content):
            return {}

    assert "_test_registry" in _PLATFORM_REGISTRY
    cls = get_platform("_test_registry")
    assert cls is _TestPlatform

    # Cleanup
    del _PLATFORM_REGISTRY["_test_registry"]


def test_list_platforms():
    import promotion_agent.platforms  # noqa: F401

    platforms = list_platforms()
    assert "moltbook" in platforms
    assert "reddit" in platforms
    assert "devto" in platforms


def test_get_unknown_platform():
    import pytest

    with pytest.raises(KeyError, match="Unknown platform"):
        get_platform("nonexistent_platform_xyz")
