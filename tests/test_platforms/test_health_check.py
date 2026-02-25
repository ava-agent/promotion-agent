"""Tests for health_check() across all 11 platforms."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from xmlrpc.client import Fault

import httpx

from promotion_agent.platforms.moltbook import MoltBookPlatform
from promotion_agent.platforms.reddit import RedditPlatform
from promotion_agent.platforms.devto import DevToPlatform
from promotion_agent.platforms.hackernews import HackerNewsPlatform
from promotion_agent.platforms.x_twitter import XTwitterPlatform
from promotion_agent.platforms.producthunt import ProductHuntPlatform
from promotion_agent.platforms.linkedin import LinkedInPlatform
from promotion_agent.platforms.juejin import JuejinPlatform
from promotion_agent.platforms.csdn import CSDNPlatform
from promotion_agent.platforms.zhihu import ZhihuPlatform
from promotion_agent.platforms.cnblogs import CNBlogsPlatform


# -- MoltBook --


def test_moltbook_health_check_success(mock_config):
    platform = MoltBookPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(200, json=[])
    platform._client = mock_client
    assert platform.health_check() is True


def test_moltbook_health_check_failure(mock_config):
    platform = MoltBookPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("Connection error")
    platform._client = mock_client
    assert platform.health_check() is False


# -- Reddit --


@patch("promotion_agent.platforms.reddit.praw.Reddit")
def test_reddit_health_check_success(mock_reddit_cls, mock_config):
    platform = RedditPlatform(mock_config)
    assert platform.health_check() is True


@patch("promotion_agent.platforms.reddit.praw.Reddit")
def test_reddit_health_check_failure(mock_reddit_cls, mock_config):
    mock_instance = mock_reddit_cls.return_value
    mock_instance.user.me.side_effect = Exception("Auth error")
    platform = RedditPlatform(mock_config)
    assert platform.health_check() is False


# -- Dev.to --


def test_devto_health_check_success(mock_config):
    platform = DevToPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(200, json=[])
    platform._client = mock_client
    assert platform.health_check() is True


def test_devto_health_check_failure(mock_config):
    platform = DevToPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(401, text="Unauthorized")
    platform._client = mock_client
    assert platform.health_check() is False


# -- Hacker News --


def test_hackernews_health_check_success(mock_config):
    platform = HackerNewsPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(200, text="<html>Hacker News</html>")
    platform._client = mock_client
    assert platform.health_check() is True


def test_hackernews_health_check_failure(mock_config):
    platform = HackerNewsPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("Timeout")
    platform._client = mock_client
    assert platform.health_check() is False


# -- X (Twitter) --


@patch("promotion_agent.platforms.x_twitter.tweepy.Client")
def test_x_health_check_success(mock_tweepy_cls, mock_config):
    mock_instance = mock_tweepy_cls.return_value
    mock_me = MagicMock()
    mock_me.data = {"id": "123", "name": "test"}
    mock_instance.get_me.return_value = mock_me
    platform = XTwitterPlatform(mock_config)
    platform._client = mock_instance
    assert platform.health_check() is True


@patch("promotion_agent.platforms.x_twitter.tweepy.Client")
def test_x_health_check_failure(mock_tweepy_cls, mock_config):
    mock_instance = mock_tweepy_cls.return_value
    mock_instance.get_me.side_effect = Exception("Auth error")
    platform = XTwitterPlatform(mock_config)
    platform._client = mock_instance
    assert platform.health_check() is False


# -- Product Hunt --


def test_producthunt_health_check_success(mock_config):
    platform = ProductHuntPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(
        200, json={"data": {"viewer": {"user": {"id": "1"}}}}
    )
    platform._client = mock_client
    assert platform.health_check() is True


def test_producthunt_health_check_failure(mock_config):
    platform = ProductHuntPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(
        200, json={"data": {"viewer": None}}
    )
    platform._client = mock_client
    assert platform.health_check() is False


# -- LinkedIn --


def test_linkedin_health_check_success(mock_config):
    platform = LinkedInPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(200, json={"sub": "person123"})
    platform._client = mock_client
    assert platform.health_check() is True


def test_linkedin_health_check_failure(mock_config):
    platform = LinkedInPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(401, text="Unauthorized")
    platform._client = mock_client
    assert platform.health_check() is False


# -- Juejin --


def test_juejin_health_check_success(mock_config):
    platform = JuejinPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.post.return_value = httpx.Response(200, json={"data": []})
    platform._client = mock_client
    assert platform.health_check() is True


def test_juejin_health_check_failure(mock_config):
    platform = JuejinPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.post.side_effect = Exception("Connection refused")
    platform._client = mock_client
    assert platform.health_check() is False


# -- CSDN --


def test_csdn_health_check_success(mock_config):
    platform = CSDNPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(200, json={"username": "test"})
    platform._client = mock_client
    assert platform.health_check() is True


def test_csdn_health_check_failure(mock_config):
    platform = CSDNPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(403, text="Forbidden")
    platform._client = mock_client
    assert platform.health_check() is False


# -- Zhihu --


def test_zhihu_health_check_success(mock_config):
    platform = ZhihuPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.return_value = httpx.Response(200, json={"id": "test"})
    platform._client = mock_client
    assert platform.health_check() is True


def test_zhihu_health_check_failure(mock_config):
    platform = ZhihuPlatform(mock_config)
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("SSL error")
    platform._client = mock_client
    assert platform.health_check() is False


# -- CNBlogs --


def test_cnblogs_health_check_success(mock_config):
    platform = CNBlogsPlatform(mock_config)
    mock_proxy = MagicMock()
    mock_proxy.metaWeblog.getRecentPosts.return_value = [{"title": "Test"}]
    platform._proxy = mock_proxy
    assert platform.health_check() is True


def test_cnblogs_health_check_failure(mock_config):
    platform = CNBlogsPlatform(mock_config)
    mock_proxy = MagicMock()
    mock_proxy.metaWeblog.getRecentPosts.side_effect = Fault(403, "Unauthorized")
    platform._proxy = mock_proxy
    assert platform.health_check() is False
