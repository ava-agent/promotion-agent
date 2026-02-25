# Promotion Agent

Automate posting and promoting GitHub/AI projects to **11 social media platforms** with one command.

Supports both standalone CLI usage and [OpenClaw](https://github.com/anthropics/openclaw) AI Agent Skill integration.

## Supported Platforms

| Platform | Flag | Auth Method | Docs |
|----------|------|-------------|------|
| **MoltBook** | `-p moltbook` | API Key | AI agent social network |
| **Reddit** | `-p reddit` | OAuth (client + user) | r/MachineLearning, r/Python, etc. |
| **Dev.to** | `-p devto` | API Key | Full Markdown, max 4 tags |
| **Hacker News** | `-p hackernews` | Username/Password | "Show HN:" prefix for launches |
| **X (Twitter)** | `-p x` | OAuth 1.0a (4 keys) | 280 chars, free 500/month |
| **Product Hunt** | `-p producthunt` | Bearer Token | GraphQL API, product launches |
| **LinkedIn** | `-p linkedin` | OAuth 2.0 Token | Professional announcements |
| **掘金 (Juejin)** | `-p juejin` | Cookie | China's largest frontend community |
| **CSDN** | `-p csdn` | Cookie | China's largest dev community |
| **知乎 (Zhihu)** | `-p zhihu` | Cookie | Column articles (专栏) |
| **博客园 (CNBlogs)** | `-p cnblogs` | Token (MetaWeblog) | Official XML-RPC API |

## Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Configure credentials

Copy the example and fill in your keys:

```bash
cp .env.example .env
```

Or set environment variables with the `PROMOTE_` prefix:

```bash
export PROMOTE_DEVTO_API_KEY=your_key
export PROMOTE_HN_USERNAME=your_username
export PROMOTE_HN_PASSWORD=your_password
```

### 3. Verify

```bash
promote platforms list       # Show all 11 platforms
promote config show          # Show config (secrets masked)
promote config validate      # Check which platforms have valid credentials
```

### 4. Post

```bash
# Preview first (always recommended)
promote post --all --dry-run --title "My AI Project" --body "Description" --url "https://github.com/you/repo"

# Post to all configured platforms
promote post --all --title "My AI Project" --body "Description" --url "https://github.com/you/repo" --tag ai

# Post to a single platform
promote post -p devto --title "My AI Project" --file ./article.md --tag ai --tag python
```

## CLI Reference

### `promote post` - Post content

```bash
promote post [OPTIONS]

Options:
  -p, --platform TEXT    Target platform (can repeat: -p reddit -p devto)
  --all                  Post to all configured platforms
  -t, --title TEXT       Post title (required)
  -b, --body TEXT        Post body text
  -f, --file PATH        Read body from markdown file
  --template TEXT        Use a named template
  --var TEXT             Template variable KEY=VALUE (can repeat)
  --tag TEXT             Tags (can repeat)
  --url TEXT             Project URL (included in every post)
  --subreddit TEXT       Reddit: target subreddit
  --submolt TEXT         MoltBook: target submolt
  --draft                Dev.to: save as draft instead of publishing
  --dry-run              Preview without posting
```

### `promote platforms` - Platform management

```bash
promote platforms list     # List all registered platforms + required config
promote platforms check    # Health check (test API connectivity)
```

### `promote auth` - Cookie management

```bash
promote auth status                          # Show cookie status
promote auth set-cookie juejin "cookie..."   # Save cookie for a platform
promote auth clear-cookie juejin             # Remove saved cookie
```

### `promote templates` - Content templates

```bash
promote templates list                       # List available templates
promote templates show github_project_announce  # View template source
promote templates render github_project_announce \
  --var project_name="Trip Agent" \
  --var description="AI travel planner" \
  --var github_url="https://github.com/kevinten10/trip-agent"
```

### `promote config` - Configuration

```bash
promote config show       # Display all config (secrets masked)
promote config validate   # Validate credentials for each platform
```

## Platform Configuration Guide

### International Platforms

**MoltBook** - Get your API key from [moltbook.com](https://moltbook.com) settings:
```bash
PROMOTE_MOLTBOOK_API_KEY=mb_your_key_here
```

**Reddit** - Create an app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (script type):
```bash
PROMOTE_REDDIT_CLIENT_ID=your_client_id
PROMOTE_REDDIT_CLIENT_SECRET=your_client_secret
PROMOTE_REDDIT_USERNAME=your_username
PROMOTE_REDDIT_PASSWORD=your_password
```

**Dev.to** - Generate at [dev.to/settings/extensions](https://dev.to/settings/extensions):
```bash
PROMOTE_DEVTO_API_KEY=your_api_key
```

**Hacker News** - Your HN account credentials:
```bash
PROMOTE_HN_USERNAME=your_username
PROMOTE_HN_PASSWORD=your_password
```

**X (Twitter)** - Create app at [developer.x.com](https://developer.x.com), get 4 keys from "Keys and Tokens":
```bash
PROMOTE_X_CONSUMER_KEY=your_consumer_key
PROMOTE_X_CONSUMER_SECRET=your_consumer_secret
PROMOTE_X_ACCESS_TOKEN=your_access_token
PROMOTE_X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

**Product Hunt** - Create app at [producthunt.com/v2/oauth/applications](https://api.producthunt.com/v2/oauth/applications):
```bash
PROMOTE_PRODUCTHUNT_TOKEN=your_bearer_token
```

**LinkedIn** - Create app at [linkedin.com/developers](https://www.linkedin.com/developers/), get OAuth 2.0 token with `w_member_social` scope. Token expires in 60 days.
```bash
PROMOTE_LINKEDIN_ACCESS_TOKEN=your_access_token
```

### Chinese Platforms (Cookie Auth)

For 掘金, CSDN, 知乎 — cookies can be extracted two ways:

**Option A: Manual (F12)**
1. Log in to the platform in your browser
2. Open DevTools (F12) > Network tab
3. Copy the `Cookie` header from any request
4. Save: `promote auth set-cookie juejin "your_cookie_string"`

**Option B: Auto-extract via OpenClaw browser**
When using as an OpenClaw Skill, the AI agent can automatically extract cookies from your browser using Extension Relay mode. Just ask: "Help me set up Juejin credentials".

```bash
PROMOTE_JUEJIN_COOKIE=your_cookie
PROMOTE_CSDN_COOKIE=your_cookie
PROMOTE_ZHIHU_COOKIE=your_cookie
```

**博客园 (CNBlogs)** - Official API, go to [cnblogs.com Settings > API Token]:
```bash
PROMOTE_CNBLOGS_BLOG_URL=your_blog_id
PROMOTE_CNBLOGS_USERNAME=your_username
PROMOTE_CNBLOGS_TOKEN=your_api_token
```

## Content Templates

Three built-in Jinja2 templates for common scenarios:

| Template | Use Case | Key Variables |
|----------|----------|---------------|
| `github_project_announce` | New project launch | `project_name`, `description`, `github_url`, `features`, `install_command` |
| `project_update` | Version release | `project_name`, `version`, `summary`, `github_url`, `changes` |
| `tutorial_share` | Technical tutorial | `title`, `introduction`, `github_url`, `prerequisites`, `steps` |

Example:
```bash
promote post --all \
  --template github_project_announce \
  --var project_name="Trip Agent" \
  --var description="AI-powered travel planning agent" \
  --var github_url="https://github.com/kevinten10/trip-agent" \
  --url "https://github.com/kevinten10/trip-agent" \
  --tag ai --tag travel
```

## OpenClaw Integration

This project works as an [OpenClaw](https://github.com/anthropics/openclaw) Skill. The AI agent reads `SKILL.md` and can autonomously promote your projects.

### Install as OpenClaw Skill

```bash
# Clone to OpenClaw skills directory
git clone https://github.com/ava-agent/promotion-agent.git ~/.openclaw/skills/promotion-agent

# Install
bash ~/.openclaw/skills/promotion-agent/scripts/install.sh
```

### Configure in openclaw.json

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "promotion-agent": {
        "enabled": true,
        "env": {
          "PROMOTE_DEVTO_API_KEY": "your_key",
          "PROMOTE_HN_USERNAME": "your_username",
          "PROMOTE_HN_PASSWORD": "your_password"
        }
      }
    }
  }
}
```

See `openclaw.json.example` for the full template with all platforms.

### Usage with OpenClaw

Once configured, just tell the agent:

> "Help me promote my Trip Agent project on all platforms"

The agent will:
1. Ask for project details and target platforms
2. Choose the right language per platform (English/Chinese)
3. Draft platform-adapted content using templates
4. Preview with `--dry-run` and ask for confirmation
5. Post and report results with URLs

## Architecture

```
src/promotion_agent/
├── core/                  # Base abstractions
│   ├── base_platform.py   # BasePlatform ABC
│   ├── registry.py        # @register_platform decorator
│   ├── content.py         # PromotionContent dataclass
│   └── result.py          # PostResult dataclass
├── platforms/             # 11 platform adapters (plugin architecture)
│   ├── moltbook.py        # httpx + challenge-response
│   ├── reddit.py          # PRAW
│   ├── devto.py           # httpx (Forem API)
│   ├── hackernews.py      # httpx (web form scraping)
│   ├── x_twitter.py       # tweepy (v2 API)
│   ├── producthunt.py     # httpx (GraphQL)
│   ├── linkedin.py        # httpx (ugcPosts API)
│   ├── juejin.py          # httpx (draft→publish)
│   ├── csdn.py            # httpx (saveArticle)
│   ├── zhihu.py           # httpx (draft→publish)
│   └── cnblogs.py         # xmlrpc (MetaWeblog)
├── cli/                   # Typer CLI
│   ├── app.py             # Root: post, auth, platforms, templates, config
│   └── commands/          # Command implementations
├── config/                # Pydantic Settings (PROMOTE_ env prefix)
└── content/               # Jinja2 template engine
```

### Adding a New Platform

1. Create `src/promotion_agent/platforms/newplatform.py`
2. Implement `BasePlatform` with `@register_platform` decorator
3. Add config fields to `config/settings.py`
4. Add import to `platforms/__init__.py`
5. Add tests to `tests/test_platforms/test_newplatform.py`

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/ tests/
```

## License

MIT
