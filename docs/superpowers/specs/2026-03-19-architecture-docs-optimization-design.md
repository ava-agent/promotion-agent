# Design: Architecture & Documentation Optimization

## Context

promotion-agent v4 expanded from 4 to 22 platforms. Documentation is stale (references v3 CLI, Playwright). Code has significant duplication in auth/manager.py (190 lines), server.py (repeated publish pattern), and 14 platform files (httpx client boilerplate).

## Scope

Documentation overhaul + deep code refactor.

## Documentation Changes

### README.md — Full Rewrite
- 22 platforms (18 social + 3 AI directories + 1 proxy)
- Remove Playwright references (v4 removed it)
- Remove CLI commands — v4 is MCP-only
- Update architecture table: 12 tools
- Add generic `publish` + `submit_directory` to MCP Tools Reference
- Add new platform credential guides (Medium, Hashnode, Weibo, V2EX, SegmentFault, OSCHINA)
- Update troubleshooting for v4

### CLAUDE.md — New
- Python 3.10+, async-first, httpx
- Platform pattern: `@register_platform`, `BasePlatform` / `BaseHttpPlatform`
- Test pattern: pytest + pytest-asyncio, `AsyncMock`
- Import paths: `platforms.*`, `core.*`, `auth.*`

### Stale Docs
| File | Action |
|------|--------|
| `SKILL.md` | Rewrite for v4 MCP plugin |
| `SCREENSHOTS.md` | Delete (CLI screenshots) |
| `PLATFORM_STATUS.md` | Rewrite for 22 platforms |
| `publish_alternative_methods.md` | Delete |

## Code Refactor

### auth/manager.py — Data-Driven
Replace 18 individual `_<platform>_status()` methods with `_AUTH_DEFINITIONS` list of tuples. Single `_get_status()` method iterates the list. ~190 lines -> ~60 lines.

### server.py — Extract Helper
Extract `_do_publish()` helper to eliminate repeated platform instantiation + content adaptation + dry_run check across 6 tool functions. ~-50 lines.

### core/base_platform.py — BaseHttpPlatform Mixin
Add `BaseHttpPlatform(BasePlatform)` with lazy `httpx.AsyncClient`, `_default_headers()` override. 14 httpx-based platforms migrate to it, removing ~10 lines each (~140 total).

Platforms affected: devto, linkedin, producthunt, moltbook, hackernews, medium, hashnode, weibo, v2ex, segmentfault, oschina, zhihu, juejin, csdn.

Not affected (non-httpx): reddit (praw), cnblogs (xmlrpc), x_twitter (tweepy), xiaohongshu/wechat (proxy).

## Verification
- `pytest tests/` — all 203+ tests pass
- `python3 -c "from server import app"` — no import errors
- No functionality changes — pure refactor + docs
