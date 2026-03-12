"""Configuration management using Pydantic Settings (v4 trimmed)."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class PromotionSettings(BaseSettings):
    """Trimmed settings for v4 — only platforms supported by the MCP server.

    Supported platforms: Zhihu, X/Twitter, WeChat Official Account.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROMOTE_",
        case_sensitive=False,
    )

    # 知乎 (Zhihu) - Cookie auth
    zhihu_cookie: Optional[str] = None

    # X (Twitter) - OAuth 1.0a
    x_consumer_key: Optional[str] = None
    x_consumer_secret: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None

    # 微信公众号 (WeChat Official Account) - App credentials
    wechat_app_id: Optional[str] = None
    wechat_app_secret: Optional[str] = None
