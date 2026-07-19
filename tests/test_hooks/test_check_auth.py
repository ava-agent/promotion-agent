"""Tests for auth-check hook script."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)


def run_hook(
    tool_input: dict, extra_env: Optional[dict] = None
) -> subprocess.CompletedProcess:
    env = {**os.environ}
    # Clear auth vars for clean test state
    for key in list(env):
        if key.startswith("PROMOTE_"):
            del env[key]
    if extra_env:
        env.update(extra_env)

    return subprocess.run(
        [sys.executable, "hooks/check_auth.py"],
        input=json.dumps(tool_input),
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
    )


def test_publish_zhihu_no_cookie():
    """No cookie without dry_run should block (exit 2)."""
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_zhihu",
            "input": {"title": "T", "body": "B"},
        }
    )
    assert result.returncode == 2
    assert "cookie" in result.stderr.lower() or "auth" in result.stderr.lower()


def test_publish_zhihu_with_cookie():
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_zhihu",
            "input": {"title": "T", "body": "B"},
        },
        extra_env={"PROMOTE_ZHIHU_COOKIE": "valid_cookie"},
    )
    assert result.returncode == 0
    # No warning when cookie is present
    assert "missing" not in result.stdout.lower()


def test_publish_x_no_creds():
    """No X creds without dry_run should block (exit 2)."""
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_x",
            "input": {"text": "Hello"},
        }
    )
    assert result.returncode == 2
    assert "PROMOTE_X" in result.stderr or "auth" in result.stderr.lower()


def test_publish_x_with_xquik_creds():
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_x",
            "input": {"text": "Hello"},
        },
        extra_env={
            "PROMOTE_X_PROVIDER": "xquik",
            "PROMOTE_XQUIK_API_KEY": "test-api-key",
            "PROMOTE_XQUIK_ACCOUNT": "test-account",
        },
    )
    assert result.returncode == 0
    assert "missing" not in result.stdout.lower()


def test_publish_x_requires_selected_provider_credentials():
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_x",
            "input": {"text": "Hello"},
        },
        extra_env={
            "PROMOTE_X_PROVIDER": "xquik",
            "PROMOTE_X_CONSUMER_KEY": "consumer-key",
            "PROMOTE_X_CONSUMER_SECRET": "consumer-secret",
            "PROMOTE_X_ACCESS_TOKEN": "access-token",
            "PROMOTE_X_ACCESS_TOKEN_SECRET": "access-token-secret",
        },
    )
    assert result.returncode == 2
    assert "Xquik API Key" in result.stderr
    assert "Xquik Account" in result.stderr


def test_publish_zhihu_no_cookie_non_dry_run_blocks():
    """Non-dry-run with missing auth should block (exit 2)."""
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_zhihu",
            "input": {"title": "T", "body": "B", "dry_run": False},
        }
    )
    assert result.returncode == 2
    assert "missing" in result.stderr.lower() or "auth" in result.stderr.lower()


def test_publish_zhihu_no_cookie_dry_run_allows():
    """Dry-run with missing auth should warn but allow (exit 0)."""
    result = run_hook(
        {
            "tool_name": "mcp__promotion-agent__publish_zhihu",
            "input": {"title": "T", "body": "B", "dry_run": True},
        }
    )
    assert result.returncode == 0
    # Should have a warning message
    assert "missing" in result.stdout.lower() or "dry_run" in result.stdout.lower()


def test_unknown_tool_passes():
    """Unknown tools should pass through without blocking."""
    result = run_hook(
        {
            "tool_name": "mcp__other-server__some_tool",
            "input": {"foo": "bar"},
        }
    )
    assert result.returncode == 0
    assert result.stdout == ""
