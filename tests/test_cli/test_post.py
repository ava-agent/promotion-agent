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
    # All 11 platforms should be registered
    assert "moltbook" in result.output.lower()
    assert "reddit" in result.output.lower()
    assert "dev.to" in result.output.lower()
    assert "hacker news" in result.output.lower()
    assert "x (twitter)" in result.output.lower()
    assert "product hunt" in result.output.lower()
    assert "linkedin" in result.output.lower()
    assert "掘金" in result.output
    assert "csdn" in result.output.lower()
    assert "知乎" in result.output
    assert "博客园" in result.output


def test_templates_list():
    result = runner.invoke(app, ["templates", "list"])
    assert result.exit_code == 0


def test_config_show(monkeypatch, tmp_path):
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(tmp_path / "nonexistent.env"))
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert "PROMOTE_" in result.output


def test_config_show_masks_secrets(monkeypatch, tmp_path):
    """Verify that cookies, tokens, and passwords are masked in config show."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "PROMOTE_JUEJIN_COOKIE=supersecretcookievalue123\n"
        "PROMOTE_DEVTO_API_KEY=devto_key_abcdef123456\n"
        "PROMOTE_REDDIT_PASSWORD=mypassword123\n"
        "PROMOTE_CNBLOGS_TOKEN=longtoken12345678\n"
    )
    monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    # Full secret values should NOT appear in output
    assert "supersecretcookievalue123" not in result.output
    assert "devto_key_abcdef123456" not in result.output
    assert "mypassword123" not in result.output
    assert "longtoken12345678" not in result.output
    # Masked format: first4****last4
    assert "supe" in result.output  # first 4 chars of cookie
    assert "****" in result.output  # mask indicator
