"""Tests for the post CLI command (legacy v3 — skipped in v4)."""

import pytest

pytestmark = pytest.mark.skip(reason="Legacy CLI tests — v4 is MCP-only, no CLI")


def test_post_dry_run():
    pass


def test_platforms_list():
    pass
