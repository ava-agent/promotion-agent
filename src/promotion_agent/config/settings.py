"""Configuration management using Pydantic Settings."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class PromotionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROMOTE_",
        case_sensitive=False,
    )

    # MoltBook
    moltbook_api_key: Optional[str] = None
    moltbook_default_submolt: str = "general"

    # Reddit
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None
    reddit_user_agent: Optional[str] = None
    reddit_default_subreddit: str = "test"

    # Dev.to
    devto_api_key: Optional[str] = None

    # 掘金 (Juejin) - Cookie auth
    juejin_cookie: Optional[str] = None

    # CSDN - Cookie auth
    csdn_cookie: Optional[str] = None

    # 知乎 (Zhihu) - Cookie auth
    zhihu_cookie: Optional[str] = None

    # 博客园 (CNBlogs) - MetaWeblog API
    cnblogs_blog_url: Optional[str] = None
    cnblogs_username: Optional[str] = None
    cnblogs_token: Optional[str] = None

    # Hacker News - Username/password web form auth
    hn_username: Optional[str] = None
    hn_password: Optional[str] = None

    # X (Twitter) - OAuth 1.0a
    x_consumer_key: Optional[str] = None
    x_consumer_secret: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None

    # Product Hunt - OAuth 2.0 Bearer token
    producthunt_token: Optional[str] = None

    # LinkedIn - OAuth 2.0 access token (expires in 60 days)
    linkedin_access_token: Optional[str] = None

    # General
    github_username: str = "kevinten10"
