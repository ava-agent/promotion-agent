"""Tests for the auth CLI commands (legacy v3 — skipped in v4)."""

import pytest

pytestmark = pytest.mark.skip(reason="Legacy CLI tests — v4 is MCP-only, no CLI")


def test_auth_status():
    pass


def test_set_cookie():
    pass
