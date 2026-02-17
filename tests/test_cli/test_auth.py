"""Tests for the auth CLI commands."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from promotion_agent.cli.app import app
from promotion_agent.config.loader import load_settings

runner = CliRunner()


@pytest.fixture(autouse=True)
def clear_settings_cache():
    """Clear the lru_cache between tests."""
    load_settings.cache_clear()
    yield
    load_settings.cache_clear()


def test_auth_status(monkeypatch, tmp_path):
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(tmp_path / "nonexistent.env"))
    result = runner.invoke(app, ["auth", "status"])
    assert result.exit_code == 0
    assert "juejin" in result.output
    assert "csdn" in result.output
    assert "zhihu" in result.output


def test_set_cookie(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))

    result = runner.invoke(app, ["auth", "set-cookie", "juejin", "test_cookie_value"])
    assert result.exit_code == 0
    assert "Saved" in result.output

    # Verify the file was written
    content = env_file.read_text()
    assert "PROMOTE_JUEJIN_COOKIE=test_cookie_value" in content


def test_set_cookie_unknown_platform(monkeypatch, tmp_path):
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(tmp_path / ".env"))
    result = runner.invoke(app, ["auth", "set-cookie", "twitter", "cookie"])
    assert result.exit_code != 0


def test_clear_cookie(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PROMOTE_JUEJIN_COOKIE=old_value\nPROMOTE_CSDN_COOKIE=csdn\n")
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))

    result = runner.invoke(app, ["auth", "clear-cookie", "juejin"])
    assert result.exit_code == 0
    assert "Removed" in result.output

    content = env_file.read_text()
    assert "PROMOTE_JUEJIN_COOKIE" not in content
    assert "PROMOTE_CSDN_COOKIE=csdn" in content


def test_clear_cookie_not_found(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))

    result = runner.invoke(app, ["auth", "clear-cookie", "zhihu"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_set_cookie_updates_existing(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PROMOTE_JUEJIN_COOKIE=old\nPROMOTE_DEVTO_API_KEY=keep\n")
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))

    result = runner.invoke(app, ["auth", "set-cookie", "juejin", "new_cookie"])
    assert result.exit_code == 0

    content = env_file.read_text()
    assert "PROMOTE_JUEJIN_COOKIE=new_cookie" in content
    assert "PROMOTE_DEVTO_API_KEY=keep" in content
