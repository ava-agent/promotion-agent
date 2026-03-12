"""Platform plugin registry with decorator-based registration."""

from __future__ import annotations

from typing import Type

from core.base_platform import BasePlatform

_PLATFORM_REGISTRY: dict[str, Type[BasePlatform]] = {}


def register_platform(cls: Type[BasePlatform]) -> Type[BasePlatform]:
    """Class decorator to register a platform plugin."""
    _PLATFORM_REGISTRY[cls.PLATFORM_NAME] = cls
    return cls


def get_platform(name: str) -> Type[BasePlatform]:
    """Get a platform class by name."""
    if name not in _PLATFORM_REGISTRY:
        available = ", ".join(_PLATFORM_REGISTRY.keys())
        raise KeyError(f"Unknown platform '{name}'. Available: {available}")
    return _PLATFORM_REGISTRY[name]


def list_platforms() -> dict[str, Type[BasePlatform]]:
    """Return all registered platforms."""
    return dict(_PLATFORM_REGISTRY)
