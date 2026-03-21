"""Tests for AuthManager credential status and cookie storage."""

import os
import tempfile

import pytest

from auth.manager import AuthManager, AuthStatus
from core.settings import PromotionSettings


class TestAuthStatus:
    """Tests for the AuthStatus dataclass."""

    def test_auth_status_fields(self):
        status = AuthStatus(
            configured=True,
            valid=True,
            expires_hint="long-lived",
            message="OK",
        )
        assert status.configured is True
        assert status.valid is True
        assert status.expires_hint == "long-lived"
        assert status.message == "OK"


class TestAuthManagerDefaults:
    """All platforms unconfigured when no env vars set."""

    def test_all_unconfigured_by_default(self):
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()

        assert "zhihu" in statuses
        assert "x" in statuses
        assert "xiaohongshu" in statuses
        assert "wechat" in statuses

        # zhihu — not configured
        assert statuses["zhihu"].configured is False
        assert statuses["zhihu"].expires_hint == "~1 month"

        # x — not configured
        assert statuses["x"].configured is False
        assert statuses["x"].expires_hint == "long-lived"

        # xiaohongshu — always unconfigured (QR login only)
        assert statuses["xiaohongshu"].configured is False
        assert "qr" in statuses["xiaohongshu"].message.lower()

        # wechat — not configured
        assert statuses["wechat"].configured is False
        assert statuses["wechat"].expires_hint == "long-lived"

    def test_returns_all_platforms(self):
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert len(statuses) == 22  # 18 platforms + 3 directories + xiaohongshu


class TestAuthManagerConfigured:
    """Status is configured when proper env vars are set."""

    def test_zhihu_configured(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "zhihu_session_abc")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert statuses["zhihu"].configured is True
        assert statuses["zhihu"].expires_hint == "~1 month"

    def test_x_configured_needs_all_four(self, monkeypatch):
        # Only 3 of 4 fields — still not configured
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert statuses["x"].configured is False

    def test_x_configured_all_four(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
        monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
        monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert statuses["x"].configured is True
        assert statuses["x"].expires_hint == "long-lived"

    def test_xiaohongshu_always_unconfigured(self, monkeypatch):
        """Xiaohongshu requires QR login — never reports configured from env."""
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert statuses["xiaohongshu"].configured is False

    def test_wechat_configured(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_WECHAT_APP_ID", "wx123")
        monkeypatch.setenv("PROMOTE_WECHAT_APP_SECRET", "secret456")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert statuses["wechat"].configured is True
        assert statuses["wechat"].expires_hint == "long-lived"

    def test_wechat_partial_not_configured(self, monkeypatch):
        monkeypatch.setenv("PROMOTE_WECHAT_APP_ID", "wx123")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings)
        statuses = mgr.status_all()
        assert statuses["wechat"].configured is False


class TestAuthManagerSetCookie:
    """Tests for set_cookie writing to env file."""

    def test_set_cookie_writes_to_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings, env_file_path=str(env_file))
        mgr.set_cookie("zhihu", "new_cookie_value")

        content = env_file.read_text()
        assert "PROMOTE_ZHIHU_COOKIE=new_cookie_value" in content

    def test_set_cookie_creates_env_file_if_missing(self, tmp_path):
        env_file = tmp_path / ".env"
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings, env_file_path=str(env_file))
        mgr.set_cookie("zhihu", "fresh_cookie")

        assert env_file.exists()
        content = env_file.read_text()
        assert "PROMOTE_ZHIHU_COOKIE=fresh_cookie" in content

    def test_set_cookie_updates_existing_value(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("PROMOTE_ZHIHU_COOKIE=old_value\nOTHER_VAR=keep\n")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings, env_file_path=str(env_file))
        mgr.set_cookie("zhihu", "updated_value")

        content = env_file.read_text()
        assert "PROMOTE_ZHIHU_COOKIE=updated_value" in content
        assert "old_value" not in content
        assert "OTHER_VAR=keep" in content

    def test_set_cookie_unsupported_platform(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("")
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings, env_file_path=str(env_file))
        with pytest.raises(ValueError, match="not supported"):
            mgr.set_cookie("reddit", "some_cookie")

    def test_set_cookie_no_env_file_path(self):
        settings = PromotionSettings(_env_file=None)
        mgr = AuthManager(settings, env_file_path=None)
        with pytest.raises(ValueError, match="env_file_path"):
            mgr.set_cookie("zhihu", "some_cookie")
