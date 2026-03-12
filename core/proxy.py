"""MCPProxy — lazy loading and process management for external MCP servers.

v4.0 supports HTTP (streamable_http) transport only.
See spec section 6.1 for stdio fallback.
"""

from __future__ import annotations

import asyncio
import atexit
import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, Optional

import httpx


@dataclass
class ExternalMCPConfig:
    """Configuration for an external MCP server managed by MCPProxy."""

    name: str
    repo: str
    local_path: str
    start_cmd: list[str]
    endpoint: str
    protocol: str = "streamable_http"
    pin_commit: str = "HEAD"


class MCPProxy:
    """Manages lifecycle of external MCP server processes.

    Responsibilities:
      - Lazy clone + start of external MCP repos
      - Health checking via JSON-RPC tools/list
      - Forwarding tool calls via JSON-RPC tools/call
      - Process cleanup on exit

    v4.0 supports HTTP (streamable_http) transport only.
    See spec section 6.1 for stdio fallback.
    """

    def __init__(self) -> None:
        self._configs: Dict[str, ExternalMCPConfig] = {}
        self._processes: Dict[str, subprocess.Popen] = {}
        self._running: Dict[str, bool] = {}
        atexit.register(self.shutdown_all)

    def register(self, config: ExternalMCPConfig) -> None:
        """Register an external MCP configuration."""
        self._configs[config.name] = config

    async def is_running(self, name: str) -> bool:
        """Check if an external MCP server is alive via health check."""
        if name not in self._running or not self._running[name]:
            return False
        if name not in self._configs:
            return False
        return await self._health_check(self._configs[name])

    async def _health_check(self, config: ExternalMCPConfig) -> bool:
        """Send MCP tools/list JSON-RPC request as a liveness check."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    config.endpoint,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/list",
                        "params": {},
                    },
                    timeout=10.0,
                )
                return resp.status_code == 200
        except Exception:
            return False

    async def ensure_running(self, name: str) -> None:
        """Ensure the named MCP server is running.

        If not running: git clone if needed, subprocess.Popen, poll health
        for up to 30 seconds.
        """
        if await self.is_running(name):
            return

        if name not in self._configs:
            raise KeyError(f"MCP '{name}' not registered")

        config = self._configs[name]

        # Git clone if local path doesn't exist
        if not os.path.isdir(config.local_path):
            subprocess.run(
                ["git", "clone", config.repo, config.local_path],
                check=True,
                capture_output=True,
            )

        # Checkout pinned commit
        if config.pin_commit != "HEAD":
            subprocess.run(
                ["git", "checkout", config.pin_commit],
                cwd=config.local_path,
                check=True,
                capture_output=True,
            )

        # Start the MCP server process
        process = subprocess.Popen(
            config.start_cmd,
            cwd=config.local_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._processes[name] = process
        self._running[name] = True

        # Poll health for up to 30 seconds
        for _ in range(60):
            if await self._health_check(config):
                return
            await asyncio.sleep(0.5)

        # Timed out — clean up
        process.terminate()
        self._processes.pop(name, None)
        self._running.pop(name, None)
        raise TimeoutError(
            f"MCP '{name}' did not become healthy within 30 seconds"
        )

    async def call_tool(
        self, name: str, tool_name: str, arguments: dict
    ) -> dict:
        """Forward a JSON-RPC tools/call request to an external MCP endpoint.

        Returns the 'result' field from the JSON-RPC response.
        """
        if name not in self._configs:
            raise KeyError(f"MCP '{name}' not registered")

        config = self._configs[name]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                config.endpoint,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments,
                    },
                },
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("result", data)

    def shutdown_all(self) -> None:
        """Terminate all managed child processes."""
        for name, proc in list(self._processes.items()):
            if proc.poll() is None:
                proc.terminate()
        self._processes.clear()
        self._running.clear()
