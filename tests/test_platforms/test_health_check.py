"""Tests for health_check() across all platforms (async v4)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from xmlrpc.client import Fault

import httpx
import pytest

from platforms.moltbook import MoltBookPlatform
from platforms.reddit import RedditPlatform
from platforms.devto import DevToPlatform
from platforms.hackernews import HackerNewsPlatform
from platforms.x_twitter import XTwitterPlatform
from platforms.producthunt import ProductHuntPlatform
from platforms.linkedin import LinkedInPlatform
from platforms.juejin import JuejinPlatform
from platforms.csdn import CSDNPlatform
from platforms.zhihu import ZhihuPlatform
from platforms.cnblogs import CNBlogsPlatform


# -- MoltBook --


@pytest.mark.asyncio
async def test_moltbook_health_check_success(mock_config):
    platform = MoltBookPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_moltbook_health_check_failure(mock_config):
    platform = MoltBookPlatform(mock_config)
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Connection error")
    platform._client = mock_client
    assert await platform.health_check() is False


# -- Reddit --


@pytest.mark.asyncio
@patch("platforms.reddit.praw.Reddit")
async def test_reddit_health_check_success(mock_reddit_cls, mock_config):
    platform = RedditPlatform(mock_config)
    assert await platform.health_check() is True


@pytest.mark.asyncio
@patch("platforms.reddit.praw.Reddit")
async def test_reddit_health_check_failure(mock_reddit_cls, mock_config):
    mock_instance = mock_reddit_cls.return_value
    mock_instance.user.me.side_effect = Exception("Auth error")
    platform = RedditPlatform(mock_config)
    assert await platform.health_check() is False


# -- Dev.to --


@pytest.mark.asyncio
async def test_devto_health_check_success(mock_config):
    platform = DevToPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_devto_health_check_failure(mock_config):
    platform = DevToPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = False
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is False


# -- Hacker News --


@pytest.mark.asyncio
async def test_hackernews_health_check_success(mock_config):
    platform = HackerNewsPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_hackernews_health_check_failure(mock_config):
    platform = HackerNewsPlatform(mock_config)
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("Timeout")
    platform._client = mock_client
    assert await platform.health_check() is False


# -- X (Twitter) --


@pytest.mark.asyncio
@patch("platforms.x_twitter.tweepy.Client")
async def test_x_health_check_success(mock_tweepy_cls, mock_config):
    mock_instance = mock_tweepy_cls.return_value
    mock_me = MagicMock()
    mock_me.data = {"id": "123", "name": "test"}
    mock_instance.get_me.return_value = mock_me
    platform = XTwitterPlatform(mock_config)
    platform._client = mock_instance
    assert await platform.health_check() is True


@pytest.mark.asyncio
@patch("platforms.x_twitter.tweepy.Client")
async def test_x_health_check_failure(mock_tweepy_cls, mock_config):
    mock_instance = mock_tweepy_cls.return_value
    mock_instance.get_me.side_effect = Exception("Auth error")
    platform = XTwitterPlatform(mock_config)
    platform._client = mock_instance
    assert await platform.health_check() is False


# -- Product Hunt --


@pytest.mark.asyncio
async def test_producthunt_health_check_success(mock_config):
    platform = ProductHuntPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    resp.json.return_value = {"data": {"viewer": {"user": {"id": "1"}}}}
    mock_client.post.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_producthunt_health_check_failure(mock_config):
    platform = ProductHuntPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    resp.json.return_value = {"data": {"viewer": None}}
    mock_client.post.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is False


# -- LinkedIn --


@pytest.mark.asyncio
async def test_linkedin_health_check_success(mock_config):
    platform = LinkedInPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_linkedin_health_check_failure(mock_config):
    platform = LinkedInPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = False
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is False


# -- Juejin --


@pytest.mark.asyncio
async def test_juejin_health_check_success(mock_config):
    platform = JuejinPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.post.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_juejin_health_check_failure(mock_config):
    platform = JuejinPlatform(mock_config)
    mock_client = AsyncMock()
    mock_client.post.side_effect = Exception("Connection refused")
    platform._client = mock_client
    assert await platform.health_check() is False


# -- CSDN --


@pytest.mark.asyncio
async def test_csdn_health_check_success(mock_config):
    platform = CSDNPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_csdn_health_check_failure(mock_config):
    platform = CSDNPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = False
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is False


# -- Zhihu --


@pytest.mark.asyncio
async def test_zhihu_health_check_success(mock_config):
    platform = ZhihuPlatform(mock_config)
    mock_client = AsyncMock()
    resp = MagicMock()
    resp.is_success = True
    mock_client.get.return_value = resp
    platform._client = mock_client
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_zhihu_health_check_failure(mock_config):
    platform = ZhihuPlatform(mock_config)
    mock_client = AsyncMock()
    mock_client.get.side_effect = Exception("SSL error")
    platform._client = mock_client
    assert await platform.health_check() is False


# -- CNBlogs --


@pytest.mark.asyncio
async def test_cnblogs_health_check_success(mock_config):
    platform = CNBlogsPlatform(mock_config)
    mock_proxy = MagicMock()
    mock_proxy.metaWeblog.getRecentPosts.return_value = [{"title": "Test"}]
    platform._proxy = mock_proxy
    assert await platform.health_check() is True


@pytest.mark.asyncio
async def test_cnblogs_health_check_failure(mock_config):
    platform = CNBlogsPlatform(mock_config)
    mock_proxy = MagicMock()
    mock_proxy.metaWeblog.getRecentPosts.side_effect = Fault(403, "Unauthorized")
    platform._proxy = mock_proxy
    assert await platform.health_check() is False
