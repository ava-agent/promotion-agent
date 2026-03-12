# promotion-agent v4 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform promotion-agent from an archived CLI tool into a Claude Code Plugin with embedded MCP Server, supporting 4 social media platforms (知乎, 小红书, X/Twitter, 微信公众号).

**Architecture:** MCP Server (stdio) as the core, with per-platform `@app.tool()` handlers. Self-implemented platforms (zhihu, x_twitter) use async-migrated v3 code. Proxy platforms (xiaohongshu, wechat) forward to lazy-loaded external MCP servers. Plugin layer adds skill, hook, and agent for Claude Code integration.

**Tech Stack:** Python 3.9+, MCP Python SDK, httpx (async), tweepy (via asyncio.to_thread), pydantic, python-dotenv

**Spec:** `docs/superpowers/specs/2026-03-12-promotion-agent-v4-mcp-plugin-design.md`

---

## Chunk 1: Foundation — Branch, Core Modules, Config

### Task 1: Create v4 branch and plugin directory scaffold

**Files:**
- Create: `plugin.json`
- Create: `server.py` (empty placeholder)
- Create: `core/` directory (from v3 `src/promotion_agent/core/`)
- Create: `platforms/` directory (empty)
- Create: `auth/` directory (empty)
- Create: `skills/` directory (empty)
- Create: `hooks/` directory (empty)
- Create: `agents/` directory (empty)

- [ ] **Step 1: Create and checkout v4 branch**

```bash
cd /Users/kevinten/projects/promotion-agent
git checkout -b v4-mcp-plugin
```

- [ ] **Step 2: Create plugin directory scaffold**

Create the v4 plugin directory structure at project root. The plugin will live at the repo root (users clone or symlink to `~/.claude/plugins/promotion-agent/`).

```bash
mkdir -p core platforms auth skills hooks agents
```

- [ ] **Step 3: Write plugin.json**

Create `plugin.json`:

```json
{
  "name": "promotion-agent",
  "version": "4.0.0",
  "description": "多平台社媒自动发布（知乎、小红书、X/Twitter、微信公众号）",
  "mcpServers": {
    "promotion-agent": {
      "command": "python",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.py"],
      "env": {
        "PROMOTE_ENV_FILE": "${CLAUDE_PLUGIN_ROOT}/.env"
      }
    }
  },
  "skills": ["skills/*.md"],
  "hooks": ["hooks/*.json"],
  "agents": ["agents/*.md"]
}
```

- [ ] **Step 4: Create empty server.py placeholder**

```python
"""promotion-agent MCP Server — placeholder."""
```

- [ ] **Step 5: Commit scaffold**

```bash
git add plugin.json server.py core/ platforms/ auth/ skills/ hooks/ agents/
git commit -m "chore: scaffold v4 plugin directory structure"
```

---

### Task 2: Migrate and async-ify core modules

Port `content.py`, `result.py`, `base_platform.py`, `registry.py` from `src/promotion_agent/core/` to `core/`. Convert `BasePlatform` to async interface.

**Files:**
- Create: `core/__init__.py`
- Create: `core/content.py` (copy from `src/promotion_agent/core/content.py`)
- Create: `core/result.py` (copy from `src/promotion_agent/core/result.py`, add `error_type` field)
- Create: `core/base_platform.py` (async version of `src/promotion_agent/core/base_platform.py`)
- Create: `core/registry.py` (copy from `src/promotion_agent/core/registry.py`)
- Test: `tests/test_core/test_content.py`
- Test: `tests/test_core/test_result.py`
- Test: `tests/test_core/test_registry.py`

- [ ] **Step 1: Write test for PromotionContent**

Create `tests/__init__.py` and `tests/test_core/__init__.py` (empty).

Create `tests/test_core/test_content.py`:

```python
from core.content import ContentFormat, PromotionContent


def test_promotion_content_defaults():
    c = PromotionContent(title="T", body="B")
    assert c.format == ContentFormat.MARKDOWN
    assert c.tags == []
    assert c.url is None
    assert c.metadata == {}


def test_promotion_content_with_metadata():
    c = PromotionContent(
        title="T",
        body="B",
        tags=["ai"],
        url="https://example.com",
        metadata={"zhihu_column": "my-col"},
    )
    assert c.metadata["zhihu_column"] == "my-col"
```

- [ ] **Step 2: Run test — expect FAIL (module not found)**

```bash
cd /Users/kevinten/projects/promotion-agent
python -m pytest tests/test_core/test_content.py -v
```

Expected: `ModuleNotFoundError: No module named 'core'`

- [ ] **Step 3: Copy content.py from v3**

Copy `src/promotion_agent/core/content.py` → `core/content.py` unchanged. Create `core/__init__.py` (empty).

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/test_core/test_content.py -v
```

- [ ] **Step 5: Write test for PostResult with error_type**

Create `tests/test_core/test_result.py`:

```python
from dataclasses import asdict

from core.result import PostResult


def test_post_result_success():
    r = PostResult(platform="zhihu", success=True, url="https://zhuanlan.zhihu.com/p/123", post_id="123")
    d = asdict(r)
    assert d["success"] is True
    assert d["error"] is None
    assert d["error_type"] is None


def test_post_result_error():
    r = PostResult(platform="zhihu", success=False, error="Cookie expired", error_type="auth_expired")
    d = asdict(r)
    assert d["success"] is False
    assert d["error_type"] == "auth_expired"
```

- [ ] **Step 6: Run test — expect FAIL**

```bash
python -m pytest tests/test_core/test_result.py -v
```

Expected: FAIL because `error_type` field doesn't exist in v3 `PostResult`.

- [ ] **Step 7: Create core/result.py with error_type field**

```python
"""Result models for platform posting operations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PostResult:
    """Result of posting to a single platform."""

    platform: str
    success: bool
    url: Optional[str] = None
    post_id: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
```

- [ ] **Step 8: Run test — expect PASS**

```bash
python -m pytest tests/test_core/test_result.py -v
```

- [ ] **Step 9: Write test for async BasePlatform**

Create `tests/test_core/test_base_platform.py`:

```python
import asyncio

import pytest

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.result import PostResult


class DummyPlatform(BasePlatform):
    PLATFORM_NAME = "dummy"
    DISPLAY_NAME = "Dummy"

    def validate_config(self) -> bool:
        return True

    def adapt_content(self, content: PromotionContent) -> dict:
        return {"text": content.body}

    async def post(self, content: PromotionContent) -> PostResult:
        return PostResult(platform="dummy", success=True)

    async def health_check(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_dummy_platform_post():
    p = DummyPlatform()
    result = await p.post(PromotionContent(title="T", body="B"))
    assert result.success is True


@pytest.mark.asyncio
async def test_health_check_default():
    p = DummyPlatform()
    assert await p.health_check() is True


def test_validate_config():
    p = DummyPlatform()
    assert p.validate_config() is True
```

- [ ] **Step 10: Run test — expect FAIL**

```bash
python -m pytest tests/test_core/test_base_platform.py -v
```

- [ ] **Step 11: Create core/base_platform.py (async version)**

```python
"""Abstract base class for all platform implementations (async)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.content import PromotionContent
from core.result import PostResult


class BasePlatform(ABC):
    """Abstract base class for social media platforms.

    v4: post() and health_check() are async.
    validate_config() and adapt_content() remain sync.
    """

    PLATFORM_NAME: str = ""
    DISPLAY_NAME: str = ""
    REQUIRED_CONFIG_KEYS: list[str] = []

    @abstractmethod
    def validate_config(self) -> bool:
        ...

    @abstractmethod
    def adapt_content(self, content: PromotionContent) -> dict:
        ...

    @abstractmethod
    async def post(self, content: PromotionContent) -> PostResult:
        ...

    async def health_check(self) -> bool:
        return True
```

- [ ] **Step 12: Run test — expect PASS**

```bash
python -m pytest tests/test_core/test_base_platform.py -v
```

- [ ] **Step 13: Write test for registry**

Create `tests/test_core/test_registry.py`:

```python
from core.registry import register_platform, get_platform, list_platforms, _PLATFORM_REGISTRY
from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.result import PostResult


def setup_function():
    _PLATFORM_REGISTRY.clear()


class FakePlatform(BasePlatform):
    PLATFORM_NAME = "fake"
    DISPLAY_NAME = "Fake"

    def validate_config(self):
        return True

    def adapt_content(self, content):
        return {}

    async def post(self, content):
        return PostResult(platform="fake", success=True)


def test_register_and_get():
    register_platform(FakePlatform)
    cls = get_platform("fake")
    assert cls is FakePlatform


def test_list_platforms():
    register_platform(FakePlatform)
    all_p = list_platforms()
    assert "fake" in all_p


def test_get_unknown_raises():
    import pytest
    with pytest.raises(KeyError, match="Unknown platform"):
        get_platform("nonexistent")
```

- [ ] **Step 14: Copy registry.py from v3, update imports**

Copy `src/promotion_agent/core/registry.py` → `core/registry.py`. Change import from `promotion_agent.core.base_platform` to `core.base_platform`.

```python
"""Platform plugin registry with decorator-based registration."""

from __future__ import annotations

from typing import Type

from core.base_platform import BasePlatform

_PLATFORM_REGISTRY: dict[str, Type[BasePlatform]] = {}


def register_platform(cls: Type[BasePlatform]) -> Type[BasePlatform]:
    _PLATFORM_REGISTRY[cls.PLATFORM_NAME] = cls
    return cls


def get_platform(name: str) -> Type[BasePlatform]:
    if name not in _PLATFORM_REGISTRY:
        available = ", ".join(_PLATFORM_REGISTRY.keys())
        raise KeyError(f"Unknown platform '{name}'. Available: {available}")
    return _PLATFORM_REGISTRY[name]


def list_platforms() -> dict[str, Type[BasePlatform]]:
    return dict(_PLATFORM_REGISTRY)
```

- [ ] **Step 15: Run all core tests — expect PASS**

```bash
python -m pytest tests/test_core/ -v
```

- [ ] **Step 16: Commit core modules**

```bash
git add core/ tests/test_core/
git commit -m "feat(core): async base platform, content, result, registry"
```

---

### Task 3: Migrate config/settings for v4

Trim settings to v4's 4 platforms only. Keep pydantic-settings + PROMOTE_ prefix + env file loading.

**Files:**
- Create: `core/settings.py` (trimmed from `src/promotion_agent/config/settings.py`)
- Create: `core/loader.py` (adapted from `src/promotion_agent/config/loader.py`)
- Test: `tests/test_core/test_settings.py`

- [ ] **Step 1: Write test for v4 settings**

Create `tests/test_core/test_settings.py`:

```python
import os

from core.settings import PromotionSettings


def test_settings_defaults():
    s = PromotionSettings(_env_file=None)
    assert s.zhihu_cookie is None
    assert s.x_consumer_key is None


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "test_cookie_123")
    monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck_abc")
    s = PromotionSettings(_env_file=None)
    assert s.zhihu_cookie == "test_cookie_123"
    assert s.x_consumer_key == "ck_abc"
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_core/test_settings.py -v
```

- [ ] **Step 3: Create core/settings.py**

```python
"""Configuration for v4 — only 4 target platforms."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class PromotionSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PROMOTE_",
        case_sensitive=False,
    )

    # 知乎 — Cookie auth
    zhihu_cookie: Optional[str] = None

    # X/Twitter — OAuth 1.0a
    x_consumer_key: Optional[str] = None
    x_consumer_secret: Optional[str] = None
    x_access_token: Optional[str] = None
    x_access_token_secret: Optional[str] = None

    # 微信公众号 — AppID + Secret
    wechat_app_id: Optional[str] = None
    wechat_app_secret: Optional[str] = None
```

- [ ] **Step 4: Create core/loader.py**

```python
"""Configuration loader — env file discovery for v4."""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

from core.settings import PromotionSettings


def _find_env_file() -> str | None:
    candidates = [
        Path.cwd() / ".env",
        Path.home() / ".config" / "promotion-agent" / ".env",
    ]
    for path in candidates:
        try:
            if path.is_file():
                return str(path)
        except (OSError, PermissionError):
            continue
    return None


@lru_cache
def load_settings() -> PromotionSettings:
    env_file = os.environ.get("PROMOTE_ENV_FILE") or _find_env_file()
    if env_file:
        return PromotionSettings(_env_file=env_file)
    return PromotionSettings()
```

- [ ] **Step 5: Run test — expect PASS**

```bash
python -m pytest tests/test_core/test_settings.py -v
```

- [ ] **Step 6: Commit config**

```bash
git add core/settings.py core/loader.py tests/test_core/test_settings.py
git commit -m "feat(core): v4 settings — trimmed to 4 platforms"
```

---

## Chunk 2: Self-Implemented Platforms — Zhihu (async) + X/Twitter (async + thread)

### Task 4: Migrate zhihu.py to async

Convert `httpx.Client` → `httpx.AsyncClient`. Make `post()` and `health_check()` async.

**Files:**
- Create: `platforms/__init__.py`
- Create: `platforms/zhihu.py` (async version of `src/promotion_agent/platforms/zhihu.py`)
- Test: `tests/test_platforms/__init__.py`
- Test: `tests/test_platforms/test_zhihu.py`

- [ ] **Step 1: Write async test for zhihu**

Create `tests/test_platforms/__init__.py` (empty).

Create `tests/test_platforms/test_zhihu.py`:

```python
"""Tests for async Zhihu platform."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from core.content import PromotionContent
from platforms.zhihu import ZhihuPlatform


class MockConfig:
    zhihu_cookie = "test_cookie"


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="Test Article",
        body="This is a test.",
        tags=["ai"],
        url="https://github.com/test",
    )


def test_validate_config():
    p = ZhihuPlatform(MockConfig())
    assert p.validate_config() is True


def test_validate_config_missing():
    class Empty:
        zhihu_cookie = None
    p = ZhihuPlatform(Empty())
    assert p.validate_config() is False


def test_adapt_content(sample_content):
    p = ZhihuPlatform(MockConfig())
    payload = p.adapt_content(sample_content)
    assert payload["title"] == sample_content.title
    assert sample_content.url in payload["content"]


@pytest.mark.asyncio
async def test_post_success(sample_content):
    p = ZhihuPlatform(MockConfig())

    mock_client = AsyncMock()
    mock_client.post.return_value = httpx.Response(200, json={"id": "draft_789"})
    mock_client.put.return_value = httpx.Response(
        200, json={"url": "https://zhuanlan.zhihu.com/p/draft_789"}
    )
    p._client = mock_client

    result = await p.post(sample_content)
    assert result.success is True
    assert "draft_789" in result.url


@pytest.mark.asyncio
async def test_post_draft_fails(sample_content):
    p = ZhihuPlatform(MockConfig())

    mock_client = AsyncMock()
    mock_client.post.return_value = httpx.Response(401, text="Unauthorized")
    p._client = mock_client

    result = await p.post(sample_content)
    assert result.success is False
    assert "draft" in result.error.lower()


@pytest.mark.asyncio
async def test_health_check_success():
    p = ZhihuPlatform(MockConfig())
    mock_client = AsyncMock()
    mock_client.get.return_value = httpx.Response(200, json={"id": "123"})
    p._client = mock_client

    assert await p.health_check() is True
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_platforms/test_zhihu.py -v
```

- [ ] **Step 3: Create platforms/zhihu.py (async)**

Create `platforms/__init__.py` (empty).

Create `platforms/zhihu.py`:

```python
"""知乎 (Zhihu) platform — async httpx, zhuanlan API.

Workflow: create draft → publish draft as column article.
Authentication: Cookie-based (from browser login session).
"""

from __future__ import annotations

from typing import Optional

import httpx

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class ZhihuPlatform(BasePlatform):
    PLATFORM_NAME = "zhihu"
    DISPLAY_NAME = "知乎"
    REQUIRED_CONFIG_KEYS = ["zhihu_cookie"]

    BASE_URL = "https://zhuanlan.zhihu.com/api"

    def __init__(self, config):
        self.cookie = getattr(config, "zhihu_cookie", None)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "Content-Type": "application/json",
                    "Cookie": self.cookie or "",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36",
                    "Origin": "https://zhuanlan.zhihu.com",
                    "Referer": "https://zhuanlan.zhihu.com/write",
                    "X-Requested-With": "XMLHttpRequest",
                },
                timeout=30.0,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n项目地址: {content.url}"

        topics = content.metadata.get("zhihu_topics", [])
        column = content.metadata.get("zhihu_column", "")

        return {
            "title": content.title,
            "content": body,
            "topics": topics,
            "column": column,
        }

    async def _create_draft(self, adapted: dict) -> Optional[str]:
        resp = await self.client.post(
            f"{self.BASE_URL}/articles/drafts",
            json={
                "title": adapted["title"],
                "content": adapted["content"],
                "delta_time": 0,
            },
        )
        if resp.is_success:
            data = resp.json()
            return str(data.get("id", ""))
        return None

    async def _publish_draft(self, draft_id: str, adapted: dict) -> dict:
        payload = {"title": adapted["title"], "content": adapted["content"]}
        if adapted.get("column"):
            payload["column"] = {"slug": adapted["column"]}
        if adapted.get("topics"):
            payload["topics"] = adapted["topics"]

        resp = await self.client.put(
            f"{self.BASE_URL}/articles/{draft_id}/publish",
            json=payload,
        )
        if resp.is_success:
            return resp.json()
        return {"error": resp.text, "status_code": resp.status_code}

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            draft_id = await self._create_draft(adapted)
            if not draft_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Failed to create draft on Zhihu",
                    error_type="platform_error",
                )

            pub_data = await self._publish_draft(draft_id, adapted)
            if "error" not in pub_data:
                article_url = pub_data.get(
                    "url", f"https://zhuanlan.zhihu.com/p/{draft_id}"
                )
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=article_url,
                    post_id=draft_id,
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(pub_data.get("error", "Publish failed")),
                error_type="platform_error",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="platform_error",
            )

    async def health_check(self) -> bool:
        try:
            resp = await self.client.get("https://www.zhihu.com/api/v4/me")
            return resp.is_success
        except Exception:
            return False
```

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/test_platforms/test_zhihu.py -v
```

- [ ] **Step 5: Commit zhihu async**

```bash
git add platforms/ tests/test_platforms/
git commit -m "feat(zhihu): async migration — httpx.AsyncClient, draft→publish"
```

---

### Task 5: Migrate x_twitter.py to async + add thread support

Wrap sync `tweepy.Client` with `asyncio.to_thread()`. Add new thread publishing via reply chain.

**Files:**
- Create: `platforms/x_twitter.py`
- Test: `tests/test_platforms/test_x_twitter.py`

- [ ] **Step 1: Write async tests for x_twitter (single tweet + thread)**

Create `tests/test_platforms/test_x_twitter.py`:

```python
"""Tests for async X/Twitter platform with thread support."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest
import tweepy

from core.content import PromotionContent
from platforms.x_twitter import XTwitterPlatform


class MockConfig:
    x_consumer_key = "test_ck"
    x_consumer_secret = "test_cs"
    x_access_token = "test_at"
    x_access_token_secret = "test_ats"


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="Test Tweet",
        body="Body",
        tags=["ai", "python"],
        url="https://github.com/test",
    )


def test_validate_config():
    p = XTwitterPlatform(MockConfig())
    assert p.validate_config() is True


def test_validate_config_partial():
    class Partial:
        x_consumer_key = "ck"
        x_consumer_secret = None
        x_access_token = "at"
        x_access_token_secret = None
    p = XTwitterPlatform(Partial())
    assert p.validate_config() is False


def test_adapt_single_tweet(sample_content):
    p = XTwitterPlatform(MockConfig())
    payload = p.adapt_content(sample_content)
    assert "text" in payload
    assert "thread" not in payload or payload["thread"] is None
    assert sample_content.url in payload["text"]


def test_adapt_thread():
    content = PromotionContent(
        title="Thread",
        body="",
        metadata={"thread": ["Tweet 1", "Tweet 2", "Tweet 3"]},
    )
    p = XTwitterPlatform(MockConfig())
    payload = p.adapt_content(content)
    assert payload["thread"] == ["Tweet 1", "Tweet 2", "Tweet 3"]
    assert payload["text"] is None


def test_adapt_280_limit():
    content = PromotionContent(title="A" * 300, body="B", url="https://x.com")
    p = XTwitterPlatform(MockConfig())
    payload = p.adapt_content(content)
    assert len(payload["text"]) <= 280


@pytest.mark.asyncio
async def test_post_single_tweet(sample_content):
    p = XTwitterPlatform(MockConfig())

    mock_response = MagicMock()
    mock_response.data = {"id": "111222333"}
    mock_client = MagicMock()
    mock_client.create_tweet.return_value = mock_response
    p._client = mock_client

    result = await p.post(sample_content)
    assert result.success is True
    assert "111222333" in result.url


@pytest.mark.asyncio
async def test_post_thread():
    content = PromotionContent(
        title="Thread",
        body="",
        metadata={"thread": ["First tweet", "Second tweet", "Third tweet"]},
    )
    p = XTwitterPlatform(MockConfig())

    call_count = 0
    def fake_create_tweet(**kwargs):
        nonlocal call_count
        call_count += 1
        resp = MagicMock()
        resp.data = {"id": str(1000 + call_count)}
        return resp

    mock_client = MagicMock()
    mock_client.create_tweet.side_effect = fake_create_tweet
    p._client = mock_client

    result = await p.post(content)
    assert result.success is True
    assert call_count == 3
    # post_id should be the first tweet
    assert result.post_id == "1001"
    # create_tweet called with in_reply_to for tweets 2 and 3
    calls = mock_client.create_tweet.call_args_list
    assert "in_reply_to_tweet_id" not in (calls[0].kwargs or {})
    assert calls[1].kwargs["in_reply_to_tweet_id"] == "1001"
    assert calls[2].kwargs["in_reply_to_tweet_id"] == "1002"


@pytest.mark.asyncio
async def test_post_failure(sample_content):
    p = XTwitterPlatform(MockConfig())

    mock_client = MagicMock()
    mock_client.create_tweet.side_effect = tweepy.TweepyException("Rate limit")
    p._client = mock_client

    result = await p.post(sample_content)
    assert result.success is False
    assert "Rate limit" in result.error
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_platforms/test_x_twitter.py -v
```

- [ ] **Step 3: Create platforms/x_twitter.py (async + thread)**

```python
"""X (Twitter) platform — async wrapper around tweepy, with thread support.

Authentication: OAuth 1.0a.
Free tier: 500 posts/month.
Thread: chain via in_reply_to_tweet_id.
"""

from __future__ import annotations

import asyncio
from typing import Optional

import tweepy

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class XTwitterPlatform(BasePlatform):
    PLATFORM_NAME = "x"
    DISPLAY_NAME = "X (Twitter)"
    REQUIRED_CONFIG_KEYS = [
        "x_consumer_key",
        "x_consumer_secret",
        "x_access_token",
        "x_access_token_secret",
    ]

    def __init__(self, config):
        self.consumer_key = getattr(config, "x_consumer_key", None)
        self.consumer_secret = getattr(config, "x_consumer_secret", None)
        self.access_token = getattr(config, "x_access_token", None)
        self.access_token_secret = getattr(config, "x_access_token_secret", None)
        self._client: Optional[tweepy.Client] = None

    @property
    def client(self) -> tweepy.Client:
        if self._client is None:
            self._client = tweepy.Client(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(
            self.consumer_key
            and self.consumer_secret
            and self.access_token
            and self.access_token_secret
        )

    def adapt_content(self, content: PromotionContent) -> dict:
        thread = content.metadata.get("thread")
        if thread:
            return {"text": None, "thread": thread}

        parts = []
        title = content.title
        if len(title) > 200:
            title = title[:197] + "..."
        parts.append(title)

        if content.url:
            parts.append(content.url)

        if content.tags:
            hashtags = " ".join(f"#{t}" for t in content.tags[:3])
            parts.append(hashtags)

        text = "\n\n".join(parts)
        if len(text) > 280:
            text = text[:277] + "..."

        return {"text": text, "thread": None}

    def _create_tweet_sync(self, **kwargs) -> dict:
        response = self.client.create_tweet(**kwargs)
        return response.data

    async def _post_single(self, text: str) -> PostResult:
        data = await asyncio.to_thread(self._create_tweet_sync, text=text)
        if data and "id" in data:
            tweet_id = str(data["id"])
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=True,
                url=f"https://x.com/i/status/{tweet_id}",
                post_id=tweet_id,
            )
        return PostResult(
            platform=self.PLATFORM_NAME,
            success=False,
            error="Unexpected response",
            error_type="platform_error",
        )

    async def _post_thread(self, tweets: list[str]) -> PostResult:
        first_id = None
        prev_id = None

        for i, text in enumerate(tweets):
            kwargs = {"text": text}
            if prev_id:
                kwargs["in_reply_to_tweet_id"] = prev_id

            data = await asyncio.to_thread(self._create_tweet_sync, **kwargs)
            if not data or "id" not in data:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Thread failed at tweet {i + 1}",
                    error_type="platform_error",
                )

            tweet_id = str(data["id"])
            if first_id is None:
                first_id = tweet_id
            prev_id = tweet_id

        return PostResult(
            platform=self.PLATFORM_NAME,
            success=True,
            url=f"https://x.com/i/status/{first_id}",
            post_id=first_id,
        )

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            if adapted.get("thread"):
                return await self._post_thread(adapted["thread"])
            elif adapted.get("text"):
                return await self._post_single(adapted["text"])
            else:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="No text or thread provided",
                    error_type="validation_error",
                )
        except tweepy.TweepyException as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="platform_error",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="platform_error",
            )

    async def health_check(self) -> bool:
        try:
            data = await asyncio.to_thread(lambda: self.client.get_me())
            return data.data is not None
        except Exception:
            return False
```

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/test_platforms/test_x_twitter.py -v
```

- [ ] **Step 5: Commit x_twitter async + thread**

```bash
git add platforms/x_twitter.py tests/test_platforms/test_x_twitter.py
git commit -m "feat(x_twitter): async migration + thread support via reply chain"
```

---

## Chunk 3: External MCP Proxy + Proxy Platforms

### Task 6: Implement MCPProxy — lazy loading and process management

**Files:**
- Create: `core/proxy.py`
- Test: `tests/test_core/test_proxy.py`

- [ ] **Step 1: Write test for MCPProxy**

Create `tests/test_core/test_proxy.py`:

```python
"""Tests for MCPProxy — external MCP lazy loading."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.proxy import MCPProxy, ExternalMCPConfig


@pytest.fixture
def xhs_config():
    return ExternalMCPConfig(
        name="xiaohongshu",
        repo="https://github.com/xpzouying/xiaohongshu-mcp",
        local_path="/tmp/test-externals/xiaohongshu-mcp",
        start_cmd=["go", "run", "main.go"],
        endpoint="http://localhost:18060/mcp",
        protocol="streamable_http",
    )


def test_external_mcp_config(xhs_config):
    assert xhs_config.name == "xiaohongshu"
    assert xhs_config.protocol == "streamable_http"


@pytest.mark.asyncio
async def test_is_running_false_when_no_process(xhs_config):
    proxy = MCPProxy()
    assert await proxy.is_running("xiaohongshu") is False


@pytest.mark.asyncio
async def test_call_tool_forwards_request(xhs_config):
    proxy = MCPProxy()
    proxy._configs = {"xiaohongshu": xhs_config}

    # Mock the HTTP call to external MCP
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_response.json.return_value = {"success": True, "platform": "xiaohongshu"}

    with patch("core.proxy.httpx.AsyncClient") as MockClient:
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client

        # Pretend it's already running
        proxy._running = {"xiaohongshu": True}

        result = await proxy.call_tool("xiaohongshu", "publish_note", {"title": "T"})
        assert result["success"] is True


def test_shutdown_all():
    proxy = MCPProxy()
    mock_proc = MagicMock()
    proxy._processes = {"xiaohongshu": mock_proc}
    proxy.shutdown_all()
    mock_proc.terminate.assert_called_once()
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_core/test_proxy.py -v
```

- [ ] **Step 3: Create core/proxy.py**

```python
"""External MCP proxy — lazy-load, manage, and forward to external MCP servers."""

from __future__ import annotations

import atexit
import asyncio
import logging
import subprocess
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ExternalMCPConfig:
    name: str
    repo: str
    local_path: str
    start_cmd: list[str]
    endpoint: str
    protocol: str = "streamable_http"
    pin_commit: str = "HEAD"


class MCPProxy:
    """Manages external MCP server lifecycle and request forwarding.

    v4.0 supports HTTP (streamable_http) transport only.
    If an external MCP turns out to be stdio-only during implementation,
    add a StdioTransport path using subprocess stdin/stdout + MCP framing.
    See spec section 6.1 for the dual-transport requirement.
    """

    def __init__(self):
        self._configs: dict[str, ExternalMCPConfig] = {}
        self._processes: dict[str, subprocess.Popen] = {}
        self._running: dict[str, bool] = {}
        atexit.register(self.shutdown_all)

    def register(self, config: ExternalMCPConfig) -> None:
        self._configs[config.name] = config

    async def is_running(self, name: str) -> bool:
        if name not in self._running or not self._running[name]:
            return False
        config = self._configs.get(name)
        if not config:
            return False
        return await self._health_check(config)

    async def _health_check(self, config: ExternalMCPConfig) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Try MCP tools/list as liveness check
                resp = await client.post(
                    config.endpoint,
                    json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
                )
                return resp.is_success
        except Exception:
            return False

    async def ensure_running(self, name: str) -> bool:
        if await self.is_running(name):
            return True

        config = self._configs.get(name)
        if not config:
            raise ValueError(f"No config registered for '{name}'")

        local = Path(config.local_path).expanduser()
        if not local.exists():
            logger.info(f"Cloning {config.repo} to {local}")
            await asyncio.to_thread(
                subprocess.run,
                ["git", "clone", config.repo, str(local)],
                check=True,
            )

        logger.info(f"Starting {name}: {config.start_cmd}")
        proc = subprocess.Popen(
            config.start_cmd,
            cwd=str(local),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._processes[name] = proc

        # Poll for health (30s timeout)
        for _ in range(30):
            await asyncio.sleep(1)
            if await self._health_check(config):
                self._running[name] = True
                return True
            if proc.poll() is not None:
                break

        return False

    async def call_tool(self, name: str, tool_name: str, arguments: dict) -> dict:
        config = self._configs.get(name)
        if not config:
            return {"success": False, "error": f"Unknown MCP: {name}", "error_type": "platform_error"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                config.endpoint,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                    "id": 1,
                },
            )
            if resp.is_success:
                data = resp.json()
                result = data.get("result", data)
                return result
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}: {resp.text}",
                "error_type": "proxy_timeout",
            }

    def shutdown_all(self) -> None:
        for name, proc in self._processes.items():
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        self._processes.clear()
        self._running.clear()
```

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/test_core/test_proxy.py -v
```

- [ ] **Step 5: Commit proxy**

```bash
git add core/proxy.py tests/test_core/test_proxy.py
git commit -m "feat(core): MCPProxy — lazy loading and external MCP management"
```

---

### Task 7: Implement proxy platforms — xiaohongshu + wechat

**Files:**
- Create: `platforms/xiaohongshu.py`
- Create: `platforms/wechat.py`
- Test: `tests/test_platforms/test_xiaohongshu.py`
- Test: `tests/test_platforms/test_wechat.py`

- [ ] **Step 1: Write test for xiaohongshu proxy platform**

Create `tests/test_platforms/test_xiaohongshu.py`:

```python
"""Tests for Xiaohongshu proxy platform."""

from unittest.mock import AsyncMock, patch

import pytest

from core.content import PromotionContent
from platforms.xiaohongshu import XiaohongshuPlatform


class MockConfig:
    pass  # No local config needed — auth managed by external MCP


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="小红书笔记",
        body="这是一篇测试笔记",
        tags=["测试", "AI"],
    )


def test_validate_config():
    p = XiaohongshuPlatform(MockConfig())
    # Always true — auth is managed by external MCP
    assert p.validate_config() is True


def test_adapt_content(sample_content):
    p = XiaohongshuPlatform(MockConfig())
    payload = p.adapt_content(sample_content)
    assert payload["title"] == "小红书笔记"
    assert len(payload["title"]) <= 20


@pytest.mark.asyncio
async def test_post_success(sample_content):
    p = XiaohongshuPlatform(MockConfig())

    mock_proxy = AsyncMock()
    mock_proxy.ensure_running.return_value = True
    mock_proxy.call_tool.return_value = {
        "success": True,
        "url": "https://www.xiaohongshu.com/note/abc123",
    }
    p._proxy = mock_proxy

    result = await p.post(sample_content)
    assert result.success is True
    assert "abc123" in result.url


@pytest.mark.asyncio
async def test_post_proxy_not_running(sample_content):
    p = XiaohongshuPlatform(MockConfig())

    mock_proxy = AsyncMock()
    mock_proxy.ensure_running.return_value = False
    p._proxy = mock_proxy

    result = await p.post(sample_content)
    assert result.success is False
    assert "proxy" in result.error.lower() or "start" in result.error.lower()
```

- [ ] **Step 2: Write test for wechat proxy platform**

Create `tests/test_platforms/test_wechat.py`:

```python
"""Tests for WeChat proxy platform."""

from unittest.mock import AsyncMock

import pytest

from core.content import PromotionContent
from platforms.wechat import WechatPlatform


class MockConfig:
    wechat_app_id = "test_app_id"
    wechat_app_secret = "test_secret"


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="微信公众号文章",
        body="这是一篇测试文章内容",
    )


def test_validate_config():
    p = WechatPlatform(MockConfig())
    assert p.validate_config() is True


def test_adapt_content(sample_content):
    p = WechatPlatform(MockConfig())
    payload = p.adapt_content(sample_content)
    assert payload["title"] == "微信公众号文章"
    assert "body" in payload


@pytest.mark.asyncio
async def test_post_success(sample_content):
    p = WechatPlatform(MockConfig())

    mock_proxy = AsyncMock()
    mock_proxy.ensure_running.return_value = True
    mock_proxy.call_tool.return_value = {
        "success": True,
        "url": "https://mp.weixin.qq.com/s/abc123",
    }
    p._proxy = mock_proxy

    result = await p.post(sample_content)
    assert result.success is True
```

- [ ] **Step 3: Run tests — expect FAIL**

```bash
python -m pytest tests/test_platforms/test_xiaohongshu.py tests/test_platforms/test_wechat.py -v
```

- [ ] **Step 4: Create platforms/xiaohongshu.py**

```python
"""小红书 (Xiaohongshu) platform — proxy to xiaohongshu-mcp."""

from __future__ import annotations

from typing import Optional

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.proxy import MCPProxy, ExternalMCPConfig
from core.registry import register_platform
from core.result import PostResult

XIAOHONGSHU_MCP = ExternalMCPConfig(
    name="xiaohongshu",
    repo="https://github.com/xpzouying/xiaohongshu-mcp",
    local_path="~/.promotion-agent/externals/xiaohongshu-mcp",
    start_cmd=["go", "run", "main.go"],
    endpoint="http://localhost:18060/mcp",
    protocol="streamable_http",
)


@register_platform
class XiaohongshuPlatform(BasePlatform):
    PLATFORM_NAME = "xiaohongshu"
    DISPLAY_NAME = "小红书"
    REQUIRED_CONFIG_KEYS = []

    def __init__(self, config, proxy: Optional[MCPProxy] = None):
        self._proxy = proxy

    @property
    def proxy(self) -> MCPProxy:
        if self._proxy is None:
            self._proxy = MCPProxy()
            self._proxy.register(XIAOHONGSHU_MCP)
        return self._proxy

    def validate_config(self) -> bool:
        return True  # Auth managed by external MCP

    def adapt_content(self, content: PromotionContent) -> dict:
        title = content.title
        if len(title) > 20:
            title = title[:17] + "..."

        return {
            "title": title,
            "body": content.body,
            "images": content.metadata.get("images", []),
            "tags": content.tags,
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            if not await self.proxy.ensure_running("xiaohongshu"):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Failed to start xiaohongshu-mcp proxy",
                    error_type="proxy_timeout",
                )

            adapted = self.adapt_content(content)
            result = await self.proxy.call_tool(
                "xiaohongshu",
                "publish_note",
                adapted,
            )

            if result.get("success"):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=result.get("url", ""),
                    post_id=result.get("post_id"),
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=result.get("error", "Unknown error"),
                error_type=result.get("error_type", "platform_error"),
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="platform_error",
            )

    async def health_check(self) -> bool:
        return await self.proxy.is_running("xiaohongshu")
```

- [ ] **Step 5: Create platforms/wechat.py**

```python
"""微信公众号 (WeChat Official Account) — proxy to Arcs-MCP."""

from __future__ import annotations

from typing import Optional

from core.base_platform import BasePlatform
from core.content import PromotionContent
from core.proxy import MCPProxy, ExternalMCPConfig
from core.registry import register_platform
from core.result import PostResult

WECHAT_MCP = ExternalMCPConfig(
    name="wechat",
    repo="https://github.com/Cyanty/Arcs-MCP",
    local_path="~/.promotion-agent/externals/arcs-mcp",
    start_cmd=["uv", "run", "server.py"],
    endpoint="http://localhost:8001/submit/mcp",
    protocol="streamable_http",
)


@register_platform
class WechatPlatform(BasePlatform):
    PLATFORM_NAME = "wechat"
    DISPLAY_NAME = "微信公众号"
    REQUIRED_CONFIG_KEYS = ["wechat_app_id", "wechat_app_secret"]

    def __init__(self, config, proxy: Optional[MCPProxy] = None):
        self.app_id = getattr(config, "wechat_app_id", None)
        self.app_secret = getattr(config, "wechat_app_secret", None)
        self._proxy = proxy

    @property
    def proxy(self) -> MCPProxy:
        if self._proxy is None:
            self._proxy = MCPProxy()
            self._proxy.register(WECHAT_MCP)
        return self._proxy

    def validate_config(self) -> bool:
        return bool(self.app_id and self.app_secret)

    def adapt_content(self, content: PromotionContent) -> dict:
        return {
            "title": content.title,
            "body": content.body,
            "cover_image": content.metadata.get("cover_image"),
            "digest": content.metadata.get("digest", content.body[:120]),
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            if not await self.proxy.ensure_running("wechat"):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="Failed to start Arcs-MCP proxy",
                    error_type="proxy_timeout",
                )

            adapted = self.adapt_content(content)
            result = await self.proxy.call_tool(
                "wechat",
                "submit_article_content_prompt",
                adapted,
            )

            if result.get("success"):
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=result.get("url", ""),
                    post_id=result.get("post_id"),
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=result.get("error", "Unknown error"),
                error_type=result.get("error_type", "platform_error"),
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
                error_type="platform_error",
            )

    async def health_check(self) -> bool:
        return await self.proxy.is_running("wechat")
```

- [ ] **Step 6: Run tests — expect PASS**

```bash
python -m pytest tests/test_platforms/test_xiaohongshu.py tests/test_platforms/test_wechat.py -v
```

- [ ] **Step 7: Commit proxy platforms**

```bash
git add platforms/xiaohongshu.py platforms/wechat.py tests/test_platforms/test_xiaohongshu.py tests/test_platforms/test_wechat.py
git commit -m "feat(platforms): xiaohongshu + wechat proxy platforms"
```

---

## Chunk 4: Auth Manager + MCP Server

### Task 8: Implement AuthManager

> **Spec divergence note:** The spec (Section 7.3) defines `AuthManager` with `trigger_qr_login()` and `health_check()`. In v4 these are placed directly in `server.py` tool handlers instead, since they require platform-specific proxy access. `AuthManager` handles credential storage/status only.

**Files:**
- Create: `auth/__init__.py`
- Create: `auth/manager.py`
- Test: `tests/test_auth/__init__.py`
- Test: `tests/test_auth/test_manager.py`

- [ ] **Step 1: Write test for AuthManager**

Create `tests/test_auth/__init__.py` (empty).

Create `tests/test_auth/test_manager.py`:

```python
"""Tests for AuthManager."""

import pytest

from auth.manager import AuthManager, AuthStatus
from core.settings import PromotionSettings


def test_auth_status_dataclass():
    s = AuthStatus(configured=True, valid=True, expires_hint="long-lived", message="OK")
    assert s.configured is True


def test_status_all_unconfigured():
    settings = PromotionSettings(_env_file=None)
    mgr = AuthManager(settings)
    statuses = mgr.status_all()
    assert "zhihu" in statuses
    assert statuses["zhihu"].configured is False
    assert "x" in statuses
    assert statuses["x"].configured is False


def test_status_all_configured(monkeypatch):
    monkeypatch.setenv("PROMOTE_ZHIHU_COOKIE", "test_cookie")
    monkeypatch.setenv("PROMOTE_X_CONSUMER_KEY", "ck")
    monkeypatch.setenv("PROMOTE_X_CONSUMER_SECRET", "cs")
    monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN", "at")
    monkeypatch.setenv("PROMOTE_X_ACCESS_TOKEN_SECRET", "ats")
    settings = PromotionSettings(_env_file=None)
    mgr = AuthManager(settings)
    statuses = mgr.status_all()
    assert statuses["zhihu"].configured is True
    assert statuses["x"].configured is True


def test_set_cookie(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("")
    settings = PromotionSettings(_env_file=str(env_file))
    mgr = AuthManager(settings, env_file_path=str(env_file))
    mgr.set_cookie("zhihu", "new_cookie_value")
    content = env_file.read_text()
    assert "PROMOTE_ZHIHU_COOKIE=new_cookie_value" in content
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_auth/test_manager.py -v
```

- [ ] **Step 3: Create auth/manager.py**

```python
"""Mixed auth management for v4 platforms."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core.settings import PromotionSettings


@dataclass
class AuthStatus:
    configured: bool
    valid: bool
    expires_hint: str
    message: str


class AuthManager:
    """Manages credentials for all platforms."""

    def __init__(self, settings: PromotionSettings, env_file_path: Optional[str] = None):
        self._settings = settings
        self._env_file = env_file_path

    def status_all(self) -> dict[str, AuthStatus]:
        return {
            "zhihu": self._zhihu_status(),
            "x": self._x_status(),
            "xiaohongshu": AuthStatus(
                configured=False,
                valid=False,
                expires_hint="session",
                message="Auth managed by xiaohongshu-mcp — use auth_qr_login",
            ),
            "wechat": self._wechat_status(),
        }

    def _zhihu_status(self) -> AuthStatus:
        cookie = self._settings.zhihu_cookie
        return AuthStatus(
            configured=bool(cookie),
            valid=bool(cookie),  # Can't verify without API call
            expires_hint="~1 month",
            message="Cookie set" if cookie else "Run auth_set_cookie to configure",
        )

    def _x_status(self) -> AuthStatus:
        has_all = bool(
            self._settings.x_consumer_key
            and self._settings.x_consumer_secret
            and self._settings.x_access_token
            and self._settings.x_access_token_secret
        )
        return AuthStatus(
            configured=has_all,
            valid=has_all,
            expires_hint="long-lived",
            message="OAuth configured" if has_all else "Set PROMOTE_X_* env vars",
        )

    def _wechat_status(self) -> AuthStatus:
        has_all = bool(self._settings.wechat_app_id and self._settings.wechat_app_secret)
        return AuthStatus(
            configured=has_all,
            valid=has_all,
            expires_hint="long-lived",
            message="AppID configured" if has_all else "Set PROMOTE_WECHAT_* env vars",
        )

    def set_cookie(self, platform: str, cookie: str) -> None:
        key_map = {"zhihu": "PROMOTE_ZHIHU_COOKIE"}
        env_key = key_map.get(platform)
        if not env_key:
            raise ValueError(f"Cookie auth not supported for '{platform}'")

        if not self._env_file:
            raise ValueError("No env file path configured")

        path = Path(self._env_file)
        lines = path.read_text().splitlines() if path.exists() else []

        # Update or append
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{env_key}="):
                lines[i] = f"{env_key}={cookie}"
                found = True
                break
        if not found:
            lines.append(f"{env_key}={cookie}")

        path.write_text("\n".join(lines) + "\n")
```

Create `auth/__init__.py` (empty).

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/test_auth/test_manager.py -v
```

- [ ] **Step 5: Commit auth manager**

```bash
git add auth/ tests/test_auth/
git commit -m "feat(auth): AuthManager with status, cookie setter, multi-platform support"
```

---

### Task 9: Implement MCP Server (server.py) with all 10 tools

**Files:**
- Modify: `server.py`
- Test: `tests/test_server.py`

- [ ] **Step 1: Write test for MCP server tool registration**

Create `tests/test_server.py`:

```python
"""Tests for MCP server tool handlers."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_server_imports():
    """Verify server.py can be imported without errors."""
    import server
    assert hasattr(server, "app")


@pytest.mark.asyncio
async def test_publish_zhihu_dry_run():
    """Test dry_run returns preview without publishing."""
    with patch("server.load_settings") as mock_load:
        mock_settings = MagicMock()
        mock_settings.zhihu_cookie = "test_cookie"
        mock_load.return_value = mock_settings

        from server import publish_zhihu
        result = await publish_zhihu(
            title="Test", body="Content", dry_run=True
        )
        assert result["success"] is True
        assert "preview" in result.get("message", "").lower() or "adapted" in result


@pytest.mark.asyncio
async def test_publish_x_dry_run():
    with patch("server.load_settings") as mock_load:
        mock_settings = MagicMock()
        mock_settings.x_consumer_key = "ck"
        mock_settings.x_consumer_secret = "cs"
        mock_settings.x_access_token = "at"
        mock_settings.x_access_token_secret = "ats"
        mock_load.return_value = mock_settings

        from server import publish_x
        result = await publish_x(text="Hello world", dry_run=True)
        assert result["success"] is True


@pytest.mark.asyncio
async def test_auth_status():
    with patch("server.load_settings") as mock_load:
        mock_settings = MagicMock()
        mock_settings.zhihu_cookie = None
        mock_settings.x_consumer_key = None
        mock_settings.x_consumer_secret = None
        mock_settings.x_access_token = None
        mock_settings.x_access_token_secret = None
        mock_settings.wechat_app_id = None
        mock_settings.wechat_app_secret = None
        mock_load.return_value = mock_settings

        from server import auth_status
        result = await auth_status()
        assert "zhihu" in result
        assert "x" in result


@pytest.mark.asyncio
async def test_list_platforms_tool():
    from server import list_platforms
    result = await list_platforms()
    assert "platforms" in result
    names = [p["name"] for p in result["platforms"]]
    assert "zhihu" in names
    assert "x" in names
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_server.py -v
```

- [ ] **Step 3: Write server.py with all 10 tools**

```python
"""promotion-agent MCP Server — 10 tools for 4 platforms.

Tools:
  Publish (4): publish_zhihu, publish_x, publish_xiaohongshu, publish_wechat
  Auth (4):    auth_status, auth_set_cookie, auth_qr_login, auth_health_check
  Utility (2): list_platforms, preview_content
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict

from mcp.server import Server
from mcp.server.stdio import stdio_server

from core.content import PromotionContent
from core.loader import load_settings
from core.result import PostResult
from auth.manager import AuthManager

# Import platforms to trigger @register_platform
import platforms.zhihu
import platforms.x_twitter
import platforms.xiaohongshu
import platforms.wechat

from platforms.zhihu import ZhihuPlatform
from platforms.x_twitter import XTwitterPlatform
from platforms.xiaohongshu import XiaohongshuPlatform
from platforms.wechat import WechatPlatform

app = Server("promotion-agent")


def _settings():
    return load_settings()


def _env_file_path() -> str:
    import os
    return os.environ.get("PROMOTE_ENV_FILE", os.path.join(os.path.dirname(__file__), ".env"))


def _auth_manager():
    return AuthManager(_settings(), env_file_path=_env_file_path())


# ── Publish Tools ──────────────────────────────────────────

@app.tool()
async def publish_zhihu(
    title: str,
    body: str,
    column: str = "",
    topics: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """发布文章到知乎专栏"""
    topics = topics or []
    platform = ZhihuPlatform(_settings())
    content = PromotionContent(
        title=title,
        body=body,
        metadata={"zhihu_column": column, "zhihu_topics": topics},
    )
    if dry_run:
        adapted = platform.adapt_content(content)
        return {"success": True, "platform": "zhihu", "message": "Preview mode", "adapted": adapted}
    result = await platform.post(content)
    return asdict(result)


@app.tool()
async def publish_x(
    text: str = "",
    thread: list[str] | None = None,
    url: str = "",
    hashtags: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """发推文到 X/Twitter（支持 Thread）"""
    thread = thread or []
    hashtags = hashtags or []
    platform = XTwitterPlatform(_settings())
    metadata = {}
    if thread:
        metadata["thread"] = thread

    content = PromotionContent(
        title=text or "",
        body="",
        tags=hashtags or [],
        url=url if url else None,
        metadata=metadata,
    )

    if dry_run:
        adapted = platform.adapt_content(content)
        return {"success": True, "platform": "x", "message": "Preview mode", "adapted": adapted}
    result = await platform.post(content)
    return asdict(result)


@app.tool()
async def publish_xiaohongshu(
    title: str,
    body: str,
    images: list[str] | None = None,
    tags: list[str] | None = None,
    dry_run: bool = False,
) -> dict:
    """发布图文笔记到小红书"""
    images = images or []
    tags = tags or []
    platform = XiaohongshuPlatform(_settings())
    content = PromotionContent(
        title=title,
        body=body,
        tags=tags,
        metadata={"images": images},
    )
    if dry_run:
        adapted = platform.adapt_content(content)
        return {"success": True, "platform": "xiaohongshu", "message": "Preview mode", "adapted": adapted}
    result = await platform.post(content)
    return asdict(result)


@app.tool()
async def publish_wechat(
    title: str,
    body: str,
    cover_image: str = "",
    digest: str = "",
    dry_run: bool = False,
) -> dict:
    """发布文章到微信公众号"""
    platform = WechatPlatform(_settings())
    content = PromotionContent(
        title=title,
        body=body,
        description=digest if digest else None,
        metadata={"cover_image": cover_image} if cover_image else {},
    )
    if dry_run:
        adapted = platform.adapt_content(content)
        return {"success": True, "platform": "wechat", "message": "Preview mode", "adapted": adapted}
    result = await platform.post(content)
    return asdict(result)


# ── Auth Tools ─────────────────────────────────────────────

@app.tool()
async def auth_status() -> dict:
    """查看所有平台的认证状态"""
    mgr = _auth_manager()
    statuses = mgr.status_all()
    return {
        name: {
            "configured": s.configured,
            "valid": s.valid,
            "expires_hint": s.expires_hint,
            "message": s.message,
        }
        for name, s in statuses.items()
    }


@app.tool()
async def auth_set_cookie(platform: str, cookie: str) -> dict:
    """设置 Cookie 认证（知乎）"""
    try:
        mgr = _auth_manager()
        mgr.set_cookie(platform, cookie)
        return {"success": True, "message": f"Cookie updated for {platform}"}
    except ValueError as e:
        return {"success": False, "error": str(e)}


@app.tool()
async def auth_qr_login() -> dict:
    """触发小红书扫码登录"""
    platform = XiaohongshuPlatform(_settings())
    try:
        running = await platform.proxy.ensure_running("xiaohongshu")
        if not running:
            return {"success": False, "error": "Failed to start xiaohongshu-mcp"}
        result = await platform.proxy.call_tool("xiaohongshu", "qr_login", {})
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.tool()
async def auth_health_check(platform: str) -> dict:
    """验证指定平台的认证是否有效"""
    platform_map = {
        "zhihu": lambda: ZhihuPlatform(_settings()),
        "x": lambda: XTwitterPlatform(_settings()),
        "xiaohongshu": lambda: XiaohongshuPlatform(_settings()),
        "wechat": lambda: WechatPlatform(_settings()),
    }
    factory = platform_map.get(platform)
    if not factory:
        return {"success": False, "error": f"Unknown platform: {platform}"}

    p = factory()
    healthy = await p.health_check()
    return {"platform": platform, "healthy": healthy}


# ── Utility Tools ──────────────────────────────────────────

@app.tool()
async def list_platforms() -> dict:
    """列出所有支持的平台及状态"""
    mgr = _auth_manager()
    statuses = mgr.status_all()
    platforms_list = [
        {
            "name": "zhihu",
            "display_name": "知乎",
            "auth_type": "cookie",
            "configured": statuses["zhihu"].configured,
        },
        {
            "name": "x",
            "display_name": "X (Twitter)",
            "auth_type": "oauth_1.0a",
            "configured": statuses["x"].configured,
        },
        {
            "name": "xiaohongshu",
            "display_name": "小红书",
            "auth_type": "qr_login",
            "configured": statuses["xiaohongshu"].configured,
        },
        {
            "name": "wechat",
            "display_name": "微信公众号",
            "auth_type": "app_id_secret",
            "configured": statuses["wechat"].configured,
        },
    ]
    return {"platforms": platforms_list}


@app.tool()
async def preview_content(title: str, body: str, platforms: list[str]) -> dict:
    """预览内容在各平台的适配结果"""
    settings = _settings()
    content = PromotionContent(title=title, body=body)

    previews = {}
    for name in platforms:
        if name == "zhihu":
            p = ZhihuPlatform(settings)
        elif name == "x":
            p = XTwitterPlatform(settings)
        elif name == "xiaohongshu":
            p = XiaohongshuPlatform(settings)
        elif name == "wechat":
            p = WechatPlatform(settings)
        else:
            previews[name] = {"error": f"Unknown platform: {name}"}
            continue
        previews[name] = p.adapt_content(content)

    return {"previews": previews}


# ── Entry Point ────────────────────────────────────────────

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Run test — expect PASS**

```bash
python -m pytest tests/test_server.py -v
```

- [ ] **Step 5: Commit server**

```bash
git add server.py tests/test_server.py
git commit -m "feat(server): MCP server with 10 tools — publish, auth, utility"
```

---

## Chunk 5: Plugin Layer — Skill, Hook, Agent + Project Files

### Task 10: Create publish skill

**Files:**
- Create: `skills/publish.md`

- [ ] **Step 1: Write skills/publish.md**

```markdown
---
name: publish
description: Publish articles to social media platforms (知乎, 小红书, X/Twitter, 微信公众号). Use when user asks to publish, post, promote, or share content to social platforms.
---

# Social Media Publisher

Publish content to supported platforms through the promotion-agent MCP server.

## Workflow

1. **Identify content source**
   - If user provides a file path, read the file
   - If file matches `*-社媒版.md` pattern, auto-split by `## ` headings:
     - "微信公众号" / "公众号" → wechat
     - "知乎" → zhihu
     - "小红书" → xiaohongshu
     - "X" / "Twitter" / "Thread" → x
   - Otherwise use conversation context

2. **Confirm target platforms**
   - Ask user which platforms to publish to (if not obvious from content)
   - Show available platforms via `list_platforms` tool

3. **Check authentication**
   - Call `auth_status` tool
   - If any target platform is not configured, guide user:
     - 知乎: "Please paste your Zhihu cookie (F12 → Network → Cookie header)"
     - X: "Set PROMOTE_X_* env vars in .env"
     - 小红书: "Use auth_qr_login to scan QR code"
     - 微信: "Set PROMOTE_WECHAT_* env vars in .env"

4. **Preview content**
   - Call each `publish_<platform>` tool with `dry_run: true`
   - Show adapted content per platform
   - For X/Twitter threads, show numbered tweet list with character counts
   - Ask user to confirm

5. **Publish**
   - Call each `publish_<platform>` tool with `dry_run: false`
   - Report result per platform immediately

6. **Summary**
   - Show table of results: platform | status | URL

## X/Twitter Thread Detection

When content contains numbered tweets (e.g., from a `*-社媒版.md` X section):
- Split by numbered lines (`1/7`, `2/7`, etc. or `1.`, `2.`, etc.)
- Pass as `thread` parameter (not `text`)
- Show preview with character count per tweet

## Image Handling

- Resolve `![](images/xxx.png)` paths relative to the source file
- Pass absolute paths to `publish_xiaohongshu` and `publish_wechat`
```

- [ ] **Step 2: Commit skill**

```bash
git add skills/publish.md
git commit -m "feat(skill): publish.md — interactive multi-platform publish workflow"
```

---

### Task 11: Create auth-check hook

**Files:**
- Create: `hooks/auth-check.json`
- Create: `hooks/check_auth.py`
- Test: `tests/test_hooks/test_check_auth.py`

- [ ] **Step 1: Write test for check_auth.py**

Create `tests/test_hooks/__init__.py` (empty).

Create `tests/test_hooks/test_check_auth.py`:

```python
"""Tests for auth-check hook script."""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = str(Path(__file__).resolve().parent.parent.parent)


def run_hook(tool_input: dict, extra_env: dict | None = None) -> subprocess.CompletedProcess:
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
    result = run_hook({
        "tool_name": "mcp__promotion-agent__publish_zhihu",
        "input": {"title": "T", "body": "B"},
    })
    assert result.returncode == 0
    assert "cookie" in result.stdout.lower() or "auth" in result.stdout.lower()


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
    result = run_hook({
        "tool_name": "mcp__promotion-agent__publish_x",
        "input": {"text": "Hello"},
    })
    assert result.returncode == 0
    assert "PROMOTE_X" in result.stdout or "auth" in result.stdout.lower()
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
python -m pytest tests/test_hooks/test_check_auth.py -v
```

- [ ] **Step 3: Create hooks/auth-check.json**

```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": "mcp__promotion-agent__publish_*",
      "command": "python ${CLAUDE_PLUGIN_ROOT}/hooks/check_auth.py"
    }
  ]
}
```

- [ ] **Step 4: Create hooks/check_auth.py**

```python
#!/usr/bin/env python3
"""PreToolUse hook: check auth before publishing.

Exit 0: proceed (with optional stdout warning)
Exit 2: block tool call
"""

import json
import os
import sys


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Can't parse — don't block

    tool_name = data.get("tool_name", "")

    # Extract platform from tool name: mcp__promotion-agent__publish_zhihu → zhihu
    if "publish_" not in tool_name:
        sys.exit(0)
    platform = tool_name.split("publish_")[-1]

    checks = {
        "zhihu": [("PROMOTE_ZHIHU_COOKIE", "知乎 Cookie")],
        "x": [
            ("PROMOTE_X_CONSUMER_KEY", "X Consumer Key"),
            ("PROMOTE_X_CONSUMER_SECRET", "X Consumer Secret"),
            ("PROMOTE_X_ACCESS_TOKEN", "X Access Token"),
            ("PROMOTE_X_ACCESS_TOKEN_SECRET", "X Access Token Secret"),
        ],
        "wechat": [
            ("PROMOTE_WECHAT_APP_ID", "WeChat App ID"),
            ("PROMOTE_WECHAT_APP_SECRET", "WeChat App Secret"),
        ],
        "xiaohongshu": [],  # Auth managed by external MCP
    }

    required = checks.get(platform, [])
    missing = [name for env_key, name in required if not os.environ.get(env_key)]

    if not missing:
        sys.exit(0)  # All auth present — proceed

    # Check if this is a dry_run — warn but don't block
    tool_input = data.get("input", {})
    if tool_input.get("dry_run"):
        print(f"⚠️  Missing auth for {platform}: {', '.join(missing)} (dry_run allowed)")
        sys.exit(0)

    # Non-dry-run with missing auth — block the tool call
    print(f"❌ Missing auth for {platform}: {', '.join(missing)}", file=sys.stderr)
    print(f"Run auth_status for setup instructions.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run test — expect PASS**

```bash
python -m pytest tests/test_hooks/test_check_auth.py -v
```

- [ ] **Step 6: Commit hook**

```bash
git add hooks/ tests/test_hooks/
git commit -m "feat(hook): auth-check PreToolUse hook for publish tools"
```

---

### Task 12: Create publisher agent

**Files:**
- Create: `agents/publisher.md`

- [ ] **Step 1: Write agents/publisher.md**

```markdown
---
name: publisher
description: Batch publish content to multiple social media platforms. Use when user wants to publish to all platforms at once or automate the full publish workflow.
tools:
  - mcp__promotion-agent__publish_zhihu
  - mcp__promotion-agent__publish_x
  - mcp__promotion-agent__publish_xiaohongshu
  - mcp__promotion-agent__publish_wechat
  - mcp__promotion-agent__auth_status
  - mcp__promotion-agent__preview_content
  - mcp__promotion-agent__list_platforms
  - Read
  - Grep
---

# Batch Publisher Agent

You are a social media publishing agent. Your job is to publish content to multiple platforms autonomously.

## Workflow

1. Read the content source (file or provided text)
2. If the file is a `*-社媒版.md`, split by `## ` headings to extract per-platform content
3. Call `auth_status` to verify credentials
4. For each target platform, call `publish_<platform>` with `dry_run: true` first
5. Present all previews to the user and wait for confirmation
6. After confirmation, publish to each platform sequentially
7. Report a summary table with: platform | status | URL | error (if any)

## Error Handling

- If a platform fails, continue with remaining platforms
- Report all failures in the summary
- Suggest fixes for auth errors (cookie expired, missing env vars)
```

- [ ] **Step 2: Commit agent**

```bash
git add agents/publisher.md
git commit -m "feat(agent): publisher.md — batch publish subagent"
```

---

### Task 13: Update project files — pyproject.toml, .env.example, README

**Files:**
- Modify: `pyproject.toml`
- Modify: `.env.example`
- Modify: `README.md`

- [ ] **Step 1: Update pyproject.toml for v4**

Remove CLI entry point. Add `mcp` dependency. Update version.

```toml
[project]
name = "promotion-agent"
version = "4.0.0"
description = "Claude Code Plugin + MCP Server for multi-platform social media publishing"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "kevinten10"},
]
keywords = ["mcp", "claude-code", "social-media", "publishing"]

dependencies = [
    "mcp>=1.0.0",
    "httpx>=0.25.0",
    "tweepy>=4.14.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "respx>=0.20.0",
    "ruff>=0.1.6",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.ruff]
line-length = 88
target-version = "py39"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers", "--verbose", "--tb=short"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Update .env.example**

```env
# promotion-agent v4 — Claude Code Plugin
# Copy to .env and fill in your credentials

# ── 知乎 (Zhihu) — Cookie auth ──
# 从浏览器 F12 → Network → Cookie header 获取
PROMOTE_ZHIHU_COOKIE=

# ── X / Twitter — OAuth 1.0a ──
# 从 developer.x.com 获取
PROMOTE_X_CONSUMER_KEY=
PROMOTE_X_CONSUMER_SECRET=
PROMOTE_X_ACCESS_TOKEN=
PROMOTE_X_ACCESS_TOKEN_SECRET=

# ── 微信公众号 — AppID + Secret ──
# 从微信公众平台获取
PROMOTE_WECHAT_APP_ID=
PROMOTE_WECHAT_APP_SECRET=

# ── 小红书 ──
# Auth managed by xiaohongshu-mcp (QR code login)
# No env vars needed
```

- [ ] **Step 3: Write README.md for v4 plugin**

```markdown
# promotion-agent

Claude Code Plugin for multi-platform social media publishing.

Supports: **知乎** · **小红书** · **X/Twitter** · **微信公众号**

## Installation

```bash
# Clone to Claude Code plugins directory
git clone https://github.com/ava-agent/promotion-agent ~/.claude/plugins/promotion-agent

# Install Python dependencies
cd ~/.claude/plugins/promotion-agent
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Platform | Auth Type | Setup |
|----------|-----------|-------|
| 知乎 | Cookie | Browser F12 → Cookie header |
| X/Twitter | OAuth 1.0a | developer.x.com credentials |
| 微信公众号 | AppID+Secret | 微信公众平台 |
| 小红书 | QR Login | Automatic via `auth_qr_login` |

## Usage

In Claude Code, ask naturally:

- "帮我把这篇文章发到知乎"
- "Publish this to X as a thread"
- "发布到所有平台"

Or use the publish skill directly.

## MCP Tools

| Tool | Description |
|------|-------------|
| `publish_zhihu` | 发布到知乎专栏 |
| `publish_x` | 发推文（支持 Thread） |
| `publish_xiaohongshu` | 发布小红书笔记 |
| `publish_wechat` | 发布微信公众号文章 |
| `auth_status` | 查看认证状态 |
| `auth_set_cookie` | 设置 Cookie |
| `auth_qr_login` | 小红书扫码登录 |
| `auth_health_check` | 验证认证有效性 |
| `list_platforms` | 列出平台 |
| `preview_content` | 预览适配结果 |

## License

[MIT](LICENSE)
```

- [ ] **Step 4: Create/update .gitignore**

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.pytest_cache/

# Environment
.env

# External MCPs (cloned at runtime)
externals/

# IDE
.vscode/
.idea/
```

- [ ] **Step 5: Commit project files**

```bash
git add pyproject.toml .env.example README.md .gitignore
git commit -m "docs: update project files for v4 plugin — pyproject, env, README, gitignore"
```

---

### Task 14: Run full test suite and verify

- [ ] **Step 1: Install dev dependencies**

```bash
cd /Users/kevinten/projects/promotion-agent
pip install -e ".[dev]"
```

- [ ] **Step 2: Run full test suite**

```bash
python -m pytest tests/ -v --tb=short
```

Expected: All tests PASS.

- [ ] **Step 3: Verify MCP server imports and tool registration**

```bash
python -c "
import server
tools = [t.name for t in server.app._tool_manager._tools.values()]
print(f'Registered {len(tools)} tools: {tools}')
assert len(tools) == 10, f'Expected 10 tools, got {len(tools)}'
print('OK')
"
```

Expected: `Registered 10 tools: [...]` + `OK`.

> Note: MCP stdio transport uses Content-Length framing, not bare JSON on stdin. Use the MCP SDK client for full integration testing, or rely on the import test above for v4.0.

- [ ] **Step 4: Verify plugin.json is valid**

```bash
python -c "import json; json.load(open('plugin.json')); print('valid')"
```

- [ ] **Step 5: Final commit if any fixes needed**

Stage only specific files (not `git add -A` which could include .env or __pycache__):

```bash
git diff --name-only  # Review what changed
git add <specific-files>
git commit -m "fix: address test failures and integration issues"
```

---

## Summary

| Chunk | Tasks | What it delivers |
|-------|-------|-----------------|
| 1. Foundation | 1-3 | Branch, async core modules, v4 settings |
| 2. Self-Implemented | 4-5 | Zhihu (async) + X/Twitter (async + thread) |
| 3. Proxy | 6-7 | MCPProxy + xiaohongshu + wechat platforms |
| 4. Server + Auth | 8-9 | AuthManager + MCP server with 10 tools |
| 5. Plugin Layer | 10-14 | Skill, hook, agent, project files, tests |

Total: **14 tasks**, ~70 steps. Each step is a single action (2-5 min).
