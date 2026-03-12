# promotion-agent v4 — Claude Code Plugin + MCP Server

> Design spec for transforming promotion-agent from an archived CLI tool into a Claude Code Plugin with embedded MCP Server, supporting 4 social media platforms.

---

## 1. Goals

- Transform promotion-agent into a **Claude Code Plugin** with an embedded MCP Server
- Support 4 platforms: **知乎, 小红书, X/Twitter, 微信公众号**
- MCP gateway pattern: self-implemented platforms + proxy to external MCP Servers
- Per-platform MCP tools with precise parameter schemas
- Mixed auth: env vars for static credentials, MCP tools for dynamic credentials (Cookie/QR)
- External MCP lazy-loading: auto-start on first use, auto-cleanup on exit

## 2. Non-Goals

- CLI interface (removed, pure MCP)
- Other 9 platforms from v3 (Reddit, Dev.to, HN, etc.) — code preserved but not migrated
- Web UI or dashboard
- Content generation (user provides content, we just publish)

---

## 3. Migration from v3

### What Changes

| Component | v3 (current) | v4 (new) |
|:----------|:-------------|:---------|
| Entry point | `promote` CLI (Typer) | MCP Server (`server.py` stdio) |
| CLI layer | `cli/`, `formatters.py` | Removed |
| Platform classes | 11 sync implementations | 4 async implementations (2 self + 2 proxy) |
| Config | `PromotionSettings` pydantic-settings | Same, but loaded via `PROMOTE_ENV_FILE` |
| Tests | pytest mocking API calls | Adapted for async + MCP tool integration |
| `SKILL.md` | OpenClaw skill definition | Superseded by `plugin.json` + `skills/publish.md` |
| `pyproject.toml` | `promote` CLI entry point | Dependency-only (no CLI script) |
| README | Archived tool recommendations | Plugin installation & usage guide |

### Code Preservation

- v3 code stays on `main` branch as-is
- v4 work on `v4-mcp-plugin` branch
- Unused platform files (reddit, devto, etc.) not copied to plugin — remain in repo for reference

### Async Migration Strategy

The v3 codebase is fully synchronous (sync `httpx.Client`, sync `tweepy.Client`). The MCP Python SDK requires async tool handlers. Strategy:

- **知乎**: Convert `httpx.Client` → `httpx.AsyncClient`. The API calls (`POST drafts`, `PUT publish`) are straightforward async conversions.
- **X/Twitter**: Wrap `tweepy.Client` (sync) with `asyncio.to_thread()`. Tweepy's async client exists but has fewer features. Sync wrapping is safer for v4.0.
- **Proxy platforms** (小红书, 微信): Already async — `httpx.AsyncClient` for HTTP forwarding to external MCPs.
- **Base class**: `BasePlatform.post()` and `health_check()` become `async def`.

---

## 4. Architecture

```
~/.claude/plugins/promotion-agent/
├── plugin.json                    # Plugin manifest
│
├── server.py                      # MCP Server entry (stdio)
├── core/
│   ├── registry.py                # @register_platform decorator + factory
│   ├── content.py                 # PromotionContent dataclass
│   ├── result.py                  # PostResult dataclass
│   └── proxy.py                   # External MCP proxy + lazy process manager
│
├── platforms/
│   ├── zhihu.py                   # Self-implemented (httpx, zhuanlan API)
│   ├── x_twitter.py               # Self-implemented (tweepy, v2 API)
│   ├── xiaohongshu.py             # Proxy → xiaohongshu-mcp
│   └── wechat.py                  # Proxy → Arcs-MCP
│
├── auth/
│   └── manager.py                 # Mixed auth management
│
├── skills/
│   └── publish.md                 # Interactive multi-platform publish workflow
│
├── hooks/
│   ├── auth-check.json            # PreToolUse hook definition
│   └── check_auth.py              # Auth validation script
│
├── agents/
│   └── publisher.md               # Batch publish agent
│
├── .env.example                   # Auth config template
└── README.md                      # Installation & usage
```

### Data Flow

```
User: "帮我把这篇文章发到知乎"
  → Claude Code matches publish skill or MCP tool
    → server.py routes to zhihu.py
      → zhihu.py calls 知乎专栏 API (draft → publish)
        → returns PostResult(success=True, url="https://zhuanlan.zhihu.com/p/xxx")

User: "也发一份到小红书"
  → server.py routes to xiaohongshu.py
    → proxy.py checks if xiaohongshu-mcp is running
      → not running → auto subprocess.Popen → wait for health check
        → proxy forwards publish call to xiaohongshu-mcp
          → returns PostResult
```

---

## 5. MCP Tools (10 total)

### 5.1 Publish Tools (4)

#### publish_zhihu

Publish article to Zhihu Zhuanlan (知乎专栏).

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| title | string | yes | Article title |
| body | string | yes | Markdown body |
| column | string | no | Zhuanlan column slug |
| topics | string[] | no | Topic tags |
| dry_run | boolean | no | Preview only, default false |

Implementation: httpx → `POST /api/articles/drafts` → `PUT /api/articles/{id}/publish`

#### publish_x

Post tweet or thread to X/Twitter.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| text | string | yes* | Single tweet (≤280 chars) |
| thread | string[] | yes* | Thread mode: multiple tweets posted in reply chain |
| url | string | no | URL to append |
| hashtags | string[] | no | Hashtag list |
| dry_run | boolean | no | Preview only, default false |

*Either `text` or `thread` required, not both.

Implementation: tweepy `Client.create_tweet()`. Thread: chain via `in_reply_to_tweet_id`.

> **Note**: Thread support is **new code** — the v3 `x_twitter.py` only supports single tweets. The reply-chain logic must be implemented from scratch in v4.

#### publish_xiaohongshu

Publish image-text note to Xiaohongshu (小红书).

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| title | string | yes | Note title (≤20 chars) |
| body | string | yes | Note body |
| images | string[] | no | Local image file paths |
| tags | string[] | no | Topic tags |
| dry_run | boolean | no | Preview only, default false |

Implementation: proxy → xiaohongshu-mcp `publish_note` tool.

#### publish_wechat

Publish article to WeChat Official Account (微信公众号).

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| title | string | yes | Article title |
| body | string | yes | Markdown body |
| cover_image | string | no | Cover image file path |
| digest | string | no | Article summary |
| dry_run | boolean | no | Preview only, default false |

Implementation: proxy → Arcs-MCP `submit_article_content_prompt` tool.

### 5.2 Auth Tools (4)

#### auth_status

Check authentication status for all platforms.

Parameters: none.

Returns:
```json
{
  "zhihu": {"configured": true, "valid": true, "expires_hint": "~1 month"},
  "x": {"configured": true, "valid": true, "expires_hint": "long-lived"},
  "xiaohongshu": {"configured": false, "valid": false, "expires_hint": "session"},
  "wechat": {"configured": true, "valid": true, "expires_hint": "long-lived"}
}
```

#### auth_set_cookie

Set cookie-based credentials for a platform.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| platform | enum[zhihu] | yes | Target platform |
| cookie | string | yes | Cookie string from browser |

Writes to `${CLAUDE_PLUGIN_ROOT}/.env`.

#### auth_qr_login

Trigger QR code login for Xiaohongshu.

Parameters: none.

Returns: `{ "message": "请用小红书 App 扫码", "qr_url": "..." }` or status from xiaohongshu-mcp login flow.

#### auth_health_check

Verify credentials are valid by sending a test request.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| platform | enum[zhihu, x, xiaohongshu, wechat] | yes | Platform to check |

### 5.3 Utility Tools (2)

#### list_platforms

List all supported platforms and their current status.

Parameters: none.

Returns: platform name, auth type, current auth status, content constraints.

#### preview_content

Preview how content will be adapted for each platform without publishing.

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| title | string | yes | Content title |
| body | string | yes | Content body |
| platforms | string[] | yes | Target platform names |

Returns: per-platform adapted title, body, truncation warnings.

For self-implemented platforms (zhihu, x): runs local `adapt_content()` logic.
For proxy platforms (xiaohongshu, wechat): returns best-effort local adaptation (title length check, body truncation estimate) without calling external MCP.

### 5.4 MCP Tool Response Schema

All tools return structured JSON content. Success and error responses follow a unified envelope:

**Success:**
```json
{
  "success": true,
  "platform": "zhihu",
  "url": "https://zhuanlan.zhihu.com/p/123456",
  "post_id": "123456",
  "message": "Article published successfully"
}
```

**Error:**
```json
{
  "success": false,
  "platform": "zhihu",
  "error": "Cookie expired — run auth_set_cookie to refresh",
  "error_type": "auth_expired"
}
```

Error types: `auth_expired`, `auth_missing`, `rate_limited`, `proxy_timeout`, `platform_error`, `validation_error`.

On MCP protocol level, errors set `isError: true` in the tool response.

### 5.5 Server Skeleton

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio

app = Server("promotion-agent")

@app.tool()
async def publish_zhihu(title: str, body: str, column: str = "", topics: list[str] = [], dry_run: bool = False) -> dict:
    """发布文章到知乎专栏"""
    content = PromotionContent(title=title, body=body, metadata={"zhihu_column": column, "zhihu_topics": topics})
    if dry_run:
        return {"success": True, "platform": "zhihu", "message": "Preview mode", "adapted": platform.adapt_content(content)}
    result = await platform.post(content)
    return asdict(result)

@app.tool()
async def publish_x(text: str = "", thread: list[str] = [], url: str = "", hashtags: list[str] = [], dry_run: bool = False) -> dict:
    """发推文到 X/Twitter"""
    # ... maps params to PromotionContent, calls platform.post()

# ... other tools registered similarly

async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

Each `@app.tool()` handler is responsible for:
1. Mapping flat MCP parameters → `PromotionContent` (including platform-specific metadata keys)
2. Calling `platform.post(content)` or `platform.adapt_content(content)` for dry_run
3. Returning the unified response dict

---

## 6. External MCP Proxy & Lazy Loading

### 6.1 External MCP Registry

```python
EXTERNAL_MCPS = {
    "xiaohongshu": {
        "repo": "https://github.com/xpzouying/xiaohongshu-mcp",
        "local_path": "~/.promotion-agent/externals/xiaohongshu-mcp",
        "pin_commit": "HEAD",  # pin to specific commit after verification
        "start_cmd": ["go", "run", "main.go"],
        "endpoint": "http://localhost:18060/mcp",
        "protocol": "streamable_http",
    },
    "wechat": {
        "repo": "https://github.com/Cyanty/Arcs-MCP",
        "local_path": "~/.promotion-agent/externals/arcs-mcp",
        "pin_commit": "HEAD",  # pin to specific commit after verification
        "start_cmd": ["uv", "run", "server.py"],
        "endpoint": "http://localhost:8001/submit/mcp",
        "protocol": "streamable_http",
    },
}
```

**Transport protocol verification**: Both external MCPs must be verified to support HTTP transport at their listed endpoints during implementation. If either uses stdio-only transport, the proxy will spawn it as a subprocess and communicate via stdin/stdout using the MCP protocol instead of HTTP — `MCPProxy` must support both transport modes.

**Health check fallback**: If no `/health` endpoint exists, proxy falls back to sending an MCP `tools/list` request as a liveness check.
```

### 6.2 Lazy Loading Flow

1. `publish_xiaohongshu()` called
2. `proxy.is_running("xiaohongshu")` → check health endpoint
3. If not running:
   - Check local clone exists at `~/.promotion-agent/externals/xiaohongshu-mcp/`
   - If not → `git clone` the repo
   - `subprocess.Popen(start_cmd, cwd=local_path)`
   - Poll health endpoint (timeout 30s)
   - On timeout → return error with setup instructions
4. Forward request to external MCP endpoint
5. Normalize response to `PostResult`

### 6.3 Process Lifecycle

- All child processes tracked in `MCPProxy._processes` dict
- `atexit.register(proxy.shutdown_all)` for cleanup
- Processes kept alive between calls (no per-call start/stop)
- Optional: idle timeout to auto-kill after N minutes of inactivity

---

## 7. Authentication

### 7.1 Credential Sources (priority high → low)

1. Environment variables `PROMOTE_*` (system-level)
2. `${CLAUDE_PLUGIN_ROOT}/.env` (plugin-level, written by auth tools)
3. `~/.promotion-agent/.env` (global, cross-project)

### 7.2 Per-Platform Auth

| Platform | Type | Env Vars | Expiry | Refresh Method |
|:---------|:-----|:---------|:-------|:---------------|
| 知乎 | Cookie | `PROMOTE_ZHIHU_COOKIE` | ~1 month | `auth_set_cookie` tool |
| X/Twitter | OAuth 1.0a | `PROMOTE_X_CONSUMER_KEY`, `PROMOTE_X_CONSUMER_SECRET`, `PROMOTE_X_ACCESS_TOKEN`, `PROMOTE_X_ACCESS_TOKEN_SECRET` | Long-lived | Env vars, one-time setup |
| 小红书 | QR Login | Managed by xiaohongshu-mcp | Session | `auth_qr_login` tool |
| 微信公众号 | AppID+Secret | `PROMOTE_WECHAT_APP_ID`, `PROMOTE_WECHAT_APP_SECRET` | Long-lived | Env vars, one-time setup |

### 7.3 AuthManager

```python
class AuthManager:
    def status_all(self) -> dict[str, AuthStatus]
    def set_cookie(self, platform: str, cookie: str) -> None
    async def trigger_qr_login(self) -> dict
    async def health_check(self, platform: str) -> bool

@dataclass
class AuthStatus:
    configured: bool
    valid: bool
    expires_hint: str   # "long-lived" | "~1 month" | "session"
    message: str
```

---

## 8. Plugin Layer

### 8.1 plugin.json

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

### 8.2 Skill: publish.md

Interactive multi-platform publish workflow. Triggered when user asks to publish/post/promote content.

**Flow:**
1. Confirm content source (file path or conversation context)
2. Confirm target platforms
3. Check auth status, guide user to fix if needed
4. Preview content adaptation per platform
5. User confirms
6. Publish sequentially, report results per platform
7. Summary table with URLs

**Special handling:**
- Detects multi-platform files (e.g., `*-社媒版.md`) and auto-splits by platform sections
- X/Twitter Thread format: splits numbered tweets into `thread` parameter
- Images: resolves relative paths to absolute paths from file location

### 8.3 Hook: auth-check.json

PreToolUse hook on `mcp__promotion-agent__publish_*` tools.

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

**Hook contract for `check_auth.py`:**
- Receives: tool call JSON on stdin (includes `tool_name` and `input` fields)
- Extracts platform name from tool name (e.g., `publish_zhihu` → `zhihu`)
- Checks if corresponding env var is set and non-empty
- **Exit 0**: auth present → tool call proceeds
- **Exit 0 + stdout message**: auth missing → prints warning but does not block (allows `dry_run` to proceed without auth)
- **Exit 2**: critical issue → blocks tool call with error message on stderr

### 8.4 Agent: publisher.md

Batch publish agent for "publish to all platforms" scenarios. Runs as subagent, autonomously executes the full preview → confirm → publish → report cycle.

---

## 9. Content Handling

### 9.1 Social Media File Auto-Split

When user provides a file like `0310-AICoding-社媒版.md`:

1. Read file, split by `## ` headings
2. Match section titles to platforms:
   - "微信公众号" / "公众号" → wechat
   - "知乎" → zhihu
   - "小红书" → xiaohongshu
   - "X" / "Twitter" / "Thread" → x
3. Extract title, body, tags from each section
4. Resolve image paths from `![](images/xxx.png)` references

### 9.2 X/Twitter Thread

Thread publishing via reply chain:
```
tweet_1 = create_tweet(text=thread[0])
tweet_2 = create_tweet(text=thread[1], in_reply_to_tweet_id=tweet_1.id)
tweet_3 = create_tweet(text=thread[2], in_reply_to_tweet_id=tweet_2.id)
...
```

### 9.3 Image Handling

publish_xiaohongshu and publish_wechat accept local file paths. The MCP Server resolves paths and reads files before forwarding to platform APIs or external MCPs.

---

## 10. Dependencies

### Python (server.py)

| Package | Purpose |
|:--------|:--------|
| mcp | MCP Python SDK (server implementation) |
| httpx | HTTP client (知乎 API, external MCP proxy) |
| tweepy | X/Twitter v2 API |
| pydantic | Data validation |
| python-dotenv | .env file loading |

### External MCP Servers (lazy-loaded)

| Name | Language | Purpose |
|:-----|:---------|:--------|
| xiaohongshu-mcp | Go | 小红书 publishing |
| Arcs-MCP | Python (uv) | 微信公众号 publishing |

### Runtime Requirements

- Python 3.9+
- Go (for xiaohongshu-mcp, only if 小红书 is used)
- uv (for Arcs-MCP, only if 微信公众号 is used)
- git (for auto-cloning external MCPs on first use)

---

## 11. Risks & Mitigations

| Risk | Mitigation |
|:-----|:-----------|
| 小红书反爬封号 | dry_run 预览、不高频发布、文档警告 |
| 知乎 Cookie 过期 | auth_health_check 主动检测，hook 拦截过期发布 |
| 外部 MCP 项目变更/不兼容 | pin 到特定 commit，本地缓存 |
| 外部 MCP 启动失败 | 30s 超时 + 清晰错误信息 + 手动安装文档 |
| X API 免费额度限制 (500/月) | publish skill 强制预览步骤（非 dry_run 默认值），发布前提醒配额 |
