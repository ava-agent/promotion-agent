"""Custom exceptions for promotion-agent."""


class PromotionError(Exception):
    """Base exception for promotion-agent."""


class PlatformError(PromotionError):
    """Error from a specific platform."""

    def __init__(self, platform: str, message: str):
        self.platform = platform
        super().__init__(f"[{platform}] {message}")


class ConfigError(PromotionError):
    """Configuration error."""


class TemplateError(PromotionError):
    """Template rendering error."""
