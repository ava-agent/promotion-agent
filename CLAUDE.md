# CLAUDE.md — promotion-agent

## Project Overview

Multi-platform content publishing tool, implemented as a Claude Code Plugin with an embedded MCP Server. Supports 18 social platforms + 3 AI directory submission sites.

## Tech Stack

- **Python 3.10+**, async-first
- **FastMCP** (`mcp` package) for MCP server
- **httpx** (async) for HTTP — most platforms
- **praw** (sync, wrapped with `asyncio.to_thread`) for Reddit
- **tweepy** (sync, wrapped with `asyncio.to_thread`) for X/Twitter
- **xmlrpc.client** (sync, wrapped with `asyncio.to_thread`) for CNBlogs
- **pytest** + **pytest-asyncio** for testing

## Architecture

```
server.py              → FastMCP app, 12 tools
core/base_platform.py  → BasePlatform (abstract), BaseHttpPlatform (httpx mixin)
core/registry.py       → @register_platform decorator, _PLATFORM_REGISTRY
core/content.py        → PromotionContent dataclass
core/result.py         → PostResult dataclass
core/settings.py       → Pydantic Settings (PROMOTE_ env prefix)
platforms/*.py          → One file per platform, each with @register_platform
auth/manager.py        → AuthManager (data-driven status + cookie storage)
hooks/check_auth.py    → PreToolUse hook — blocks publish without credentials
```

## Key Patterns

### Adding a New Platform

1. Create `platforms/<name>.py`
2. Subclass `BaseHttpPlatform` (or `BasePlatform` for non-httpx)
3. Add `@register_platform` decorator
4. Implement: `validate_config()`, `adapt_content()`, `post()`, `health_check()`
5. Add settings fields to `core/settings.py`
6. Add auth definition to `auth/manager.py` `_AUTH_DEFINITIONS`
7. Add auth check to `hooks/check_auth.py` `checks` dict
8. Import in `server.py` to trigger registration

### Platform Class Pattern (httpx)

```python
@register_platform
class FooPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "foo"
    DISPLAY_NAME = "Foo"
    REQUIRED_CONFIG_KEYS = ["foo_token"]

    def __init__(self, config):
        self._token = getattr(config, "foo_token", None)
        self._client = None  # Required by BaseHttpPlatform

    def _default_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._token or ''}"}

    def validate_config(self) -> bool:
        return bool(self._token)

    def adapt_content(self, content: PromotionContent) -> dict: ...
    async def post(self, content: PromotionContent) -> PostResult: ...
    async def health_check(self) -> bool: ...
```

### Sync Library Wrapping

For sync-only libraries (praw, tweepy, xmlrpc):
```python
result = await asyncio.to_thread(self._sync_helper, args)
```

## Import Paths

- `from platforms.<name> import <Class>` — platform classes
- `from core.base_platform import BasePlatform, BaseHttpPlatform`
- `from core.content import PromotionContent`
- `from core.result import PostResult`
- `from core.registry import register_platform, get_platform`
- **Never** use `promotion_agent.*` (that was v3 legacy)

## Testing

- Run: `python3 -m pytest tests/ -q`
- Fixtures in `tests/conftest.py`: `sample_content`, `mock_config`, etc.
- Use `AsyncMock` for httpx clients, `MagicMock` for sync libraries
- `@pytest.mark.asyncio` on all async test functions
- Tests under `tests/test_cli/` are legacy (v3) and skipped

## MCP Tools (12)

- **Publish (6)**: `publish_zhihu`, `publish_x`, `publish_xiaohongshu`, `publish_wechat`, `publish` (generic), `submit_directory`
- **Auth (4)**: `auth_status`, `auth_set_cookie`, `auth_qr_login`, `auth_health_check`
- **Utility (2)**: `list_platforms`, `preview_content`

## Environment Variables

All prefixed with `PROMOTE_`. See `.env.example` for the full list. Key env var: `PROMOTE_ENV_FILE` controls the .env file path (defaults to `<project>/.env`).
