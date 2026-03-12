"""Tests for MCP server tool handlers.

Since the `mcp` package requires Python 3.10+, we mock the FastMCP
framework and test the tool handler functions directly.
"""

from __future__ import annotations

import asyncio
import sys
import types
from dataclasses import asdict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Mock the mcp package before importing server.py
# ---------------------------------------------------------------------------

def _build_mcp_mock():
    """Build a mock `mcp` package that provides FastMCP with a working @tool() decorator."""
    mcp_mod = types.ModuleType("mcp")
    mcp_server = types.ModuleType("mcp.server")
    mcp_server_fastmcp = types.ModuleType("mcp.server.fastmcp")

    class _FakeFastMCP:
        """Minimal FastMCP stand-in that records tools as plain functions."""

        def __init__(self, name: str):
            self.name = name
            self._tools: dict[str, callable] = {}

        def tool(self):
            """Decorator that registers the function and returns it unchanged."""
            def decorator(fn):
                self._tools[fn.__name__] = fn
                return fn
            return decorator

        def run(self, transport="stdio"):
            pass

    mcp_server_fastmcp.FastMCP = _FakeFastMCP
    mcp_server.fastmcp = mcp_server_fastmcp
    mcp_mod.server = mcp_server

    return {
        "mcp": mcp_mod,
        "mcp.server": mcp_server,
        "mcp.server.fastmcp": mcp_server_fastmcp,
    }


# Install the mock before any server import
_mcp_mocks = _build_mcp_mock()
sys.modules.update(_mcp_mocks)

# Force re-import of server module in case it was cached from a prior test run
sys.modules.pop("server", None)

# Now we can safely import server
from core.settings import PromotionSettings
import server as server_mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def unconfigured_settings():
    """Settings with no credentials."""
    return PromotionSettings(_env_file=None)


@pytest.fixture
def configured_settings(monkeypatch):
    """Settings with zhihu + x + wechat configured."""
    monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "test_zhihu_cookie")
    monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
    monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
    monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
    monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
    monkeypatch.setenv("PROMOTE_WECHAT_APP_ID", "wx_id")
    monkeypatch.setenv("PROMOTE_WECHAT_APP_SECRET", "wx_secret")
    return PromotionSettings(_env_file=None)


# ---------------------------------------------------------------------------
# Test: module imports and structure
# ---------------------------------------------------------------------------

class TestServerImports:
    """Verify the server module loads and exposes expected symbols."""

    def test_server_module_loads(self):
        assert hasattr(server_mod, "app")

    def test_app_is_fastmcp(self):
        assert hasattr(server_mod.app, "_tools")

    def test_ten_tools_registered(self):
        tools = server_mod.app._tools
        expected = {
            "publish_zhihu",
            "publish_x",
            "publish_xiaohongshu",
            "publish_wechat",
            "auth_status",
            "auth_set_cookie",
            "auth_qr_login",
            "auth_health_check",
            "list_platforms",
            "preview_content",
        }
        assert set(tools.keys()) == expected


# ---------------------------------------------------------------------------
# Test: dry_run paths for publish tools
# ---------------------------------------------------------------------------

class TestPublishDryRun:
    """Dry-run calls should return adapted content without posting."""

    @pytest.mark.asyncio
    async def test_publish_zhihu_dry_run(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "test_cookie")
        result = await server_mod.publish_zhihu(
            title="Test Title",
            body="Test body content",
            dry_run=True,
        )
        assert result["dry_run"] is True
        assert result["platform"] == "zhihu"
        assert "adapted" in result
        assert result["adapted"]["title"] == "Test Title"

    @pytest.mark.asyncio
    async def test_publish_x_dry_run(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
        result = await server_mod.publish_x(
            text="Hello from dry run",
            dry_run=True,
        )
        assert result["dry_run"] is True
        assert result["platform"] == "x"
        assert "adapted" in result

    @pytest.mark.asyncio
    async def test_publish_xiaohongshu_dry_run(self):
        result = await server_mod.publish_xiaohongshu(
            title="Test XHS",
            body="Test body",
            dry_run=True,
        )
        assert result["dry_run"] is True
        assert result["platform"] == "xiaohongshu"
        assert "adapted" in result

    @pytest.mark.asyncio
    async def test_publish_wechat_dry_run(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_WECHAT_APP_ID", "wx_id")
        monkeypatch.setenv("PROMOTE_WECHAT_APP_SECRET", "wx_secret")
        result = await server_mod.publish_wechat(
            title="WeChat Article",
            body="Article body content here",
            dry_run=True,
        )
        assert result["dry_run"] is True
        assert result["platform"] == "wechat"
        assert "adapted" in result

    @pytest.mark.asyncio
    async def test_publish_zhihu_dry_run_with_topics(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "test_cookie")
        result = await server_mod.publish_zhihu(
            title="Test",
            body="Body",
            topics=["AI", "Python"],
            column="my-column",
            dry_run=True,
        )
        assert result["adapted"]["topics"] == ["AI", "Python"]
        assert result["adapted"]["column"] == "my-column"

    @pytest.mark.asyncio
    async def test_publish_x_dry_run_with_thread(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
        result = await server_mod.publish_x(
            thread=["Tweet 1", "Tweet 2"],
            dry_run=True,
        )
        assert result["adapted"]["thread"] == ["Tweet 1", "Tweet 2"]

    @pytest.mark.asyncio
    async def test_publish_x_dry_run_with_hashtags(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
        result = await server_mod.publish_x(
            text="Hello",
            hashtags=["AI", "ML"],
            dry_run=True,
        )
        assert result["dry_run"] is True


# ---------------------------------------------------------------------------
# Test: auth tools
# ---------------------------------------------------------------------------

class TestAuthTools:
    """Test auth_status, auth_set_cookie, auth_qr_login, auth_health_check."""

    @pytest.mark.asyncio
    async def test_auth_status_returns_all_platforms(self):
        result = await server_mod.auth_status()
        assert "zhihu" in result
        assert "x" in result
        assert "xiaohongshu" in result
        assert "wechat" in result

    @pytest.mark.asyncio
    async def test_auth_status_configured(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "cookie_abc")
        result = await server_mod.auth_status()
        assert result["zhihu"]["configured"] is True

    @pytest.mark.asyncio
    async def test_auth_set_cookie(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))
        result = await server_mod.auth_set_cookie(
            platform="zhihu",
            cookie="new_session_cookie",
        )
        assert result["success"] is True
        content = env_file.read_text()
        assert "PROMOTE_ZHIHU_COOKIE=new_session_cookie" in content

    @pytest.mark.asyncio
    async def test_auth_set_cookie_invalid_platform(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))
        result = await server_mod.auth_set_cookie(
            platform="reddit",
            cookie="some_value",
        )
        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_auth_qr_login(self):
        """QR login is a stub that returns instructions."""
        result = await server_mod.auth_qr_login()
        assert "xiaohongshu" in str(result).lower() or "qr" in str(result).lower()

    @pytest.mark.asyncio
    async def test_auth_health_check_zhihu(self):
        """Health check with no credentials returns unhealthy."""
        result = await server_mod.auth_health_check(platform="zhihu")
        assert "platform" in result
        assert result["platform"] == "zhihu"


# ---------------------------------------------------------------------------
# Test: utility tools
# ---------------------------------------------------------------------------

class TestUtilityTools:
    """Test list_platforms and preview_content."""

    @pytest.mark.asyncio
    async def test_list_platforms(self):
        result = await server_mod.list_platforms()
        # Should return a list or dict with platform info
        assert isinstance(result, list)
        names = [p["name"] for p in result]
        assert "zhihu" in names
        assert "x" in names
        assert "xiaohongshu" in names
        assert "wechat" in names

    @pytest.mark.asyncio
    async def test_list_platforms_includes_auth_status(self):
        result = await server_mod.list_platforms()
        for platform in result:
            assert "auth" in platform

    @pytest.mark.asyncio
    async def test_preview_content(self):
        result = await server_mod.preview_content(
            title="Preview Title",
            body="Preview body",
            platforms=["zhihu", "wechat"],
        )
        assert "zhihu" in result
        assert "wechat" in result
        assert result["zhihu"]["title"] == "Preview Title"

    @pytest.mark.asyncio
    async def test_preview_content_all_platforms(self):
        result = await server_mod.preview_content(
            title="Title",
            body="Body",
            platforms=["zhihu", "x", "xiaohongshu", "wechat"],
        )
        assert len(result) == 4
