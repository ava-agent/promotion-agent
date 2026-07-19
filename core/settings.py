"""Configuration management using Pydantic Settings (v4)."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class PromotionSettings(BaseSettings):
    """Settings for v4 - 18 platforms + 3 AI directories.

    Supported: Zhihu, X/Twitter, Xiaohongshu, WeChat, Juejin, CSDN,
    Dev.to, Reddit, LinkedIn, Product Hunt, CNBlogs, Hacker News,
    MoltBook, Medium, Hashnode, Weibo, V2EX, SegmentFault, OSCHINA.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROMOTE_",
        case_sensitive=False,
    )

    # Zhihu - Cookie auth
    zhihu_cookie: Optional[str] = None

    # X (Twitter) - OAuth 1.0a or Xquik
    x_consumer_key: Optional[str] = None
    x_consumer_secret: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None
    x_provider: str = "direct"
    xquik_api_key: Optional[str] = None
    xquik_account: Optional[str] = None
    xquik_base_url: str = "https://xquik.com/api/v1"

    # WeChat Official Account - App credentials
    wechat_app_id: Optional[str] = None
    wechat_app_secret: Optional[str] = None

    # Juejin - Cookie auth
    juejin_cookie: Optional[str] = None

    # CSDN - Cookie auth
    csdn_cookie: Optional[str] = None

    # Dev.to - API Key
    devto_api_key: Optional[str] = None

    # Reddit - OAuth
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None
    reddit_username: Optional[str] = None
    reddit_password: Optional[str] = None

    # LinkedIn - OAuth 2.0 Bearer
    linkedin_access_token: Optional[str] = None

    # Product Hunt - OAuth 2.0 Bearer
    producthunt_token: Optional[str] = None

    # CNBlogs - MetaWeblog API
    cnblogs_blog_url: Optional[str] = None
    cnblogs_username: Optional[str] = None
    cnblogs_token: Optional[str] = None

    # Hacker News - Username + Password
    hn_username: Optional[str] = None
    hn_password: Optional[str] = None

    # MoltBook - API Key
    moltbook_api_key: Optional[str] = None

    # Medium - Integration Token
    medium_integration_token: Optional[str] = None

    # Hashnode - Personal Access Token
    hashnode_token: Optional[str] = None
    hashnode_publication_id: Optional[str] = None

    # Weibo - OAuth 2.0
    weibo_access_token: Optional[str] = None

    # V2EX - Personal Access Token
    v2ex_token: Optional[str] = None

    # SegmentFault - Cookie auth
    segmentfault_cookie: Optional[str] = None

    # OSCHINA - Cookie auth
    oschina_cookie: Optional[str] = None
