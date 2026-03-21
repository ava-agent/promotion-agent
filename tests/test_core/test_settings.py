"""Tests for settings and env loader."""

import os
import tempfile

import pytest

from core.settings import PromotionSettings
from core.loader import discover_env_file


class TestPromotionSettings:
    """Tests for the trimmed v4 PromotionSettings."""

    def test_defaults_are_none(self):
        """All fields default to None when no env vars are set."""
        settings = PromotionSettings(
            _env_file=None,
        )
        assert settings.zhihu_cookie is None
        assert settings.x_consumer_key is None
        assert settings.x_consumer_secret is None
        assert settings.x_access_token is None
        assert settings.x_access_token_secret is None
        assert settings.wechat_app_id is None
        assert settings.wechat_app_secret is None

    def test_env_prefix(self, monkeypatch):
        """Settings read from PROMOTE_* env vars."""
        monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "test_cookie_123")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck_abc")
        settings = PromotionSettings(_env_file=None)
        assert settings.zhihu_cookie == "test_cookie_123"
        assert settings.x_consumer_key == "ck_abc"

    def test_all_x_twitter_fields(self, monkeypatch):
        """All four X/Twitter OAuth fields work."""
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
        settings = PromotionSettings(_env_file=None)
        assert settings.x_consumer_key == "ck"
        assert settings.x_consumer_secret == "cs"
        assert settings.x_access_token == "at"
        assert settings.x_access_token_secret == "ats"

    def test_wechat_fields(self, monkeypatch):
        """WeChat app_id and app_secret are recognized."""
        monkeypatch.setenv("PROMOTE_WECHAT_APP_ID", "wx123")
        monkeypatch.setenv("PROMOTE_WECHAT_APP_SECRET", "secret456")
        settings = PromotionSettings(_env_file=None)
        assert settings.wechat_app_id == "wx123"
        assert settings.wechat_app_secret == "secret456"

    def test_v4_expanded_fields_exist(self):
        """v4 settings should have all 18+ platform fields."""
        settings = PromotionSettings(_env_file=None)
        # Legacy migrated fields now present
        assert hasattr(settings, "reddit_client_id")
        assert hasattr(settings, "devto_api_key")
        assert hasattr(settings, "moltbook_api_key")
        assert hasattr(settings, "juejin_cookie")
        assert hasattr(settings, "csdn_cookie")
        assert hasattr(settings, "hn_username")
        assert hasattr(settings, "producthunt_token")
        assert hasattr(settings, "linkedin_access_token")
        # New platform fields
        assert hasattr(settings, "medium_integration_token")
        assert hasattr(settings, "hashnode_token")
        assert hasattr(settings, "weibo_access_token")
        assert hasattr(settings, "v2ex_token")
        assert hasattr(settings, "segmentfault_cookie")
        assert hasattr(settings, "oschina_cookie")

    def test_loads_from_env_file(self, tmp_path):
        """Settings can load from an .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("PROMOTE_ZHIHU_COOKIE=from_file\n")
        settings = PromotionSettings(_env_file=str(env_file))
        assert settings.zhihu_cookie == "from_file"


class TestDiscoverEnvFile:
    """Tests for env file discovery logic."""

    def test_promote_env_file_envvar(self, monkeypatch, tmp_path):
        """PROMOTE_ENV_FILE env var takes highest priority."""
        env_file = tmp_path / "custom.env"
        env_file.write_text("PROMOTE_ZHIHU_COOKIE=custom\n")
        monkeypatch.setenv("PROMOTE_ENV_FILE", str(env_file))
        result = discover_env_file()
        assert result == str(env_file)

    def test_promote_env_file_nonexistent(self, monkeypatch):
        """PROMOTE_ENV_FILE pointing to nonexistent file returns None."""
        monkeypatch.setenv("PROMOTE_ENV_FILE", "/tmp/nonexistent_env_file_xyz")
        result = discover_env_file()
        assert result is None

    def test_cwd_env_file(self, monkeypatch, tmp_path):
        """Falls back to .env in cwd."""
        env_file = tmp_path / ".env"
        env_file.write_text("PROMOTE_X_CONSUMER_KEY=cwd_key\n")
        monkeypatch.delenv("PROMOTE_ENV_FILE", raising=False)
        monkeypatch.chdir(tmp_path)
        result = discover_env_file()
        assert result == str(env_file)

    def test_config_dir_env_file(self, monkeypatch, tmp_path):
        """Falls back to ~/.config/promotion-agent/.env."""
        # Create a fake home config dir
        config_dir = tmp_path / ".config" / "promotion-agent"
        config_dir.mkdir(parents=True)
        env_file = config_dir / ".env"
        env_file.write_text("PROMOTE_X_CONSUMER_KEY=config_key\n")

        monkeypatch.delenv("PROMOTE_ENV_FILE", raising=False)
        # Ensure cwd has no .env
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        monkeypatch.setenv("HOME", str(tmp_path))

        result = discover_env_file()
        assert result == str(env_file)

    def test_no_env_file_found(self, monkeypatch, tmp_path):
        """Returns None when no .env file is found anywhere."""
        monkeypatch.delenv("PROMOTE_ENV_FILE", raising=False)
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        monkeypatch.chdir(empty_dir)
        # Point HOME to a dir with no config
        fake_home = tmp_path / "fakehome"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        result = discover_env_file()
        assert result is None
