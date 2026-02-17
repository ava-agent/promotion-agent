"""Tests for the post CLI command."""

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


def test_post_requires_title():
    result = runner.invoke(app, ["post", "--body", "test body", "--all"])
    assert result.exit_code != 0


def test_post_requires_body():
    result = runner.invoke(app, ["post", "--title", "test", "--all"])
    assert result.exit_code != 0


def test_post_requires_platform():
    result = runner.invoke(app, ["post", "--title", "test", "--body", "body"])
    assert result.exit_code != 0


def test_post_dry_run(monkeypatch, tmp_path):
    # Avoid reading real .env files
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(tmp_path / "nonexistent.env"))
    result = runner.invoke(
        app,
        [
            "post",
            "--title",
            "Test Title",
            "--body",
            "Test body content",
            "--all",
            "--dry-run",
            "--url",
            "https://github.com/test",
            "--tag",
            "ai",
        ],
    )
    assert result.exit_code == 0
    assert "DRY RUN" in result.output
    assert "Test Title" in result.output
    assert "ai" in result.output


def test_platforms_list():
    result = runner.invoke(app, ["platforms", "list"])
    assert result.exit_code == 0
    assert "moltbook" in result.output.lower()
    assert "reddit" in result.output.lower()
    assert "dev.to" in result.output.lower()


def test_templates_list():
    result = runner.invoke(app, ["templates", "list"])
    assert result.exit_code == 0


def test_config_show(monkeypatch, tmp_path):
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(tmp_path / "nonexistent.env"))
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "PROMOTE_" in result.output
