"""Tests for MCPProxy — lazy loading and process management."""

from __future__ import annotations

import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.proxy import ExternalMCPConfig, MCPProxy


# --- ExternalMCPConfig dataclass ---


def test_external_mcp_config_defaults():
    cfg = ExternalMCPConfig(
        name="test-mcp",
        repo="https://github.com/org/test-mcp",
        local_path="/tmp/test-mcp",
        start_cmd=["python", "server.py"],
        endpoint="http://localhost:3000/mcp",
    )
    assert cfg.name == "test-mcp"
    assert cfg.protocol == "streamable_http"
    assert cfg.pin_commit == "HEAD"


def test_external_mcp_config_custom():
    cfg = ExternalMCPConfig(
        name="custom",
        repo="https://github.com/org/custom",
        local_path="/tmp/custom",
        start_cmd=["node", "index.js"],
        endpoint="http://localhost:4000/mcp",
        protocol="streamable_http",
        pin_commit="abc1234",
    )
    assert cfg.pin_commit == "abc1234"
    assert cfg.protocol == "streamable_http"


# --- MCPProxy.is_running ---


@pytest.mark.asyncio
async def test_is_running_returns_false_when_no_process():
    proxy = MCPProxy()
    result = await proxy.is_running("nonexistent")
    assert result is False


@pytest.mark.asyncio
async def test_is_running_returns_true_when_healthy():
    proxy = MCPProxy()
    cfg = ExternalMCPConfig(
        name="test",
        repo="https://github.com/org/test",
        local_path="/tmp/test",
        start_cmd=["python", "server.py"],
        endpoint="http://localhost:3000/mcp",
    )
    proxy.register(cfg)
    proxy._running["test"] = True

    with patch.object(proxy, "_health_check", new_callable=AsyncMock, return_value=True):
        result = await proxy.is_running("test")
    assert result is True


@pytest.mark.asyncio
async def test_is_running_returns_false_when_unhealthy():
    proxy = MCPProxy()
    cfg = ExternalMCPConfig(
        name="test",
        repo="https://github.com/org/test",
        local_path="/tmp/test",
        start_cmd=["python", "server.py"],
        endpoint="http://localhost:3000/mcp",
    )
    proxy.register(cfg)
    proxy._running["test"] = True

    with patch.object(proxy, "_health_check", new_callable=AsyncMock, return_value=False):
        result = await proxy.is_running("test")
    assert result is False


# --- MCPProxy.call_tool ---


@pytest.mark.asyncio
async def test_call_tool_forwards_request():
    """call_tool sends JSON-RPC tools/call to external MCP endpoint."""
    proxy = MCPProxy()
    cfg = ExternalMCPConfig(
        name="test-mcp",
        repo="https://github.com/org/test-mcp",
        local_path="/tmp/test-mcp",
        start_cmd=["python", "server.py"],
        endpoint="http://localhost:3000/mcp",
    )
    proxy.register(cfg)

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"content": [{"type": "text", "text": "ok"}]},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("core.proxy.httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        result = await proxy.call_tool("test-mcp", "publish_note", {"title": "Hi"})

    assert result == {"content": [{"type": "text", "text": "ok"}]}
    # Verify JSON-RPC structure was sent
    call_args = mock_client_instance.post.call_args
    payload = call_args[1]["json"]
    assert payload["method"] == "tools/call"
    assert payload["params"]["name"] == "publish_note"
    assert payload["params"]["arguments"] == {"title": "Hi"}


@pytest.mark.asyncio
async def test_call_tool_raises_on_unknown_name():
    proxy = MCPProxy()
    with pytest.raises(KeyError, match="not registered"):
        await proxy.call_tool("unknown", "tool", {})


# --- MCPProxy.shutdown_all ---


def test_shutdown_all_terminates_processes():
    proxy = MCPProxy()

    proc1 = MagicMock(spec=subprocess.Popen)
    proc1.poll.return_value = None  # still running
    proc2 = MagicMock(spec=subprocess.Popen)
    proc2.poll.return_value = None

    proxy._processes["mcp1"] = proc1
    proxy._processes["mcp2"] = proc2
    proxy._running["mcp1"] = True
    proxy._running["mcp2"] = True

    proxy.shutdown_all()

    proc1.terminate.assert_called_once()
    proc2.terminate.assert_called_once()
    assert len(proxy._processes) == 0
    assert len(proxy._running) == 0


def test_shutdown_all_skips_already_exited():
    proxy = MCPProxy()

    proc = MagicMock(spec=subprocess.Popen)
    proc.poll.return_value = 0  # already exited

    proxy._processes["mcp1"] = proc
    proxy._running["mcp1"] = True

    proxy.shutdown_all()

    proc.terminate.assert_not_called()
    assert len(proxy._processes) == 0
