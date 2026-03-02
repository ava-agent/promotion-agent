# Promotion Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platforms: 11](https://img.shields.io/badge/platforms-11-green.svg)](#supported-platforms)

**One command to post your GitHub/AI projects to 11 social media platforms.**

Supports both standalone CLI usage and [OpenClaw](https://github.com/anthropics/openclaw) AI Agent Skill integration.

## Supported Platforms

| Platform | Flag | Auth Method | Notes |
|----------|------|-------------|-------|
| **MoltBook** | `-p moltbook` | API Key | AI agent social network |
| **Reddit** | `-p reddit` | OAuth (4 keys) | r/MachineLearning, r/Python, etc. |
| **Dev.to** | `-p devto` | API Key | Full Markdown, max 4 tags |
| **Hacker News** | `-p hackernews` | Username/Password | "Show HN:" prefix for launches |
| **X (Twitter)** | `-p x` | OAuth 1.0a (4 keys) | 280 chars, free tier 500/month |
| **Product Hunt** | `-p producthunt` | Bearer Token | GraphQL API, product launches |
| **LinkedIn** | `-p linkedin` | OAuth 2.0 Token | Professional announcements |
| **掘金** | `-p juejin` | Cookie | China's largest frontend community |
| **CSDN** | `-p csdn` | Cookie | China's largest dev community |
| **知乎** | `-p zhihu` | Cookie | Column articles (专栏) |
| **博客园** | `-p cnblogs` | Token (MetaWeblog) | Official XML-RPC API |

## Quick Start

### 1. Install

```bash
pip install -e .
# or from GitHub
pip install git+https://github.com/ava-agent/promotion-agent.git
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your API keys
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
promote platforms check      # Health check API connectivity
```

### 4. Post

```bash
# Preview first (always recommended)
promote post --all --dry-run --title "My AI Project" --body "Description" --url "https://github.com/user/repo"

# Post to all configured platforms
promote post --all --title "My AI Project" --body "Description" --url "https://github.com/user/repo" --tag ai

# Post to specific platforms
promote post -p devto -p reddit --title "My AI Project" --file ./article.md --tag ai --tag python
```

## CLI Reference

### `promote post` - Post content

```bash
promote post [OPTIONS]

Options:
  -p, --platform TEXT    Target platform (repeatable: -p reddit -p devto)
  --all                  Post to all configured platforms
  -t, --title TEXT       Post title (required)
  -b, --body TEXT        Post body text
  -f, --file PATH        Read body from markdown file
  --template TEXT        Use a named template
  --var TEXT             Template variable KEY=VALUE (repeatable)
  --tag TEXT             Tags (repeatable)
  --url TEXT             Project URL (included in every post)
  --subreddit TEXT       Reddit: target subreddit
  --submolt TEXT         MoltBook: target submolt
  --draft                Dev.to: save as draft
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
promote templates show github_project_announce
promote templates render github_project_announce \
  --var project_name="My Project" \
  --var description="AI-powered tool" \
  --var github_url="https://github.com/user/repo"
```

### `promote config` - Configuration

```bash
promote config show       # Display all config (secrets masked)
promote config validate   # Validate credentials for each platform
```

## Platform Configuration

### International Platforms

**MoltBook** — Get API key from [moltbook.com](https://moltbook.com):
```bash
PROMOTE_MOLTBOOK_API_KEY=mb_your_key
```

**Reddit** — Create app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps):
```bash
PROMOTE_REDDIT_CLIENT_ID=xxx
PROMOTE_REDDIT_CLIENT_SECRET=xxx
PROMOTE_REDDIT_USERNAME=xxx
PROMOTE_REDDIT_PASSWORD=xxx
```

**Dev.to** — Generate at [dev.to/settings/extensions](https://dev.to/settings/extensions):
```bash
PROMOTE_DEVTO_API_KEY=xxx
```

**Hacker News** — Your HN credentials:
```bash
PROMOTE_HN_USERNAME=xxx
PROMOTE_HN_PASSWORD=xxx
```

**X (Twitter)** — Create app at [developer.x.com](https://developer.x.com):
```bash
PROMOTE_X_CONSUMER_KEY=xxx
PROMOTE_X_CONSUMER_SECRET=xxx
PROMOTE_X_ACCESS_TOKEN=xxx
PROMOTE_X_ACCESS_TOKEN_SECRET=xxx
```

**Product Hunt** — Create app at [api.producthunt.com/v2/oauth/applications](https://api.producthunt.com/v2/oauth/applications):
```bash
PROMOTE_PRODUCTHUNT_TOKEN=xxx
```

**LinkedIn** — Create app at [linkedin.com/developers](https://www.linkedin.com/developers/):
```bash
PROMOTE_LINKEDIN_ACCESS_TOKEN=xxx  # Token expires in 60 days
```

### Chinese Platforms (Cookie Auth)

For 掘金, CSDN, 知乎 — extract cookies from browser:

1. Log in to the platform in your browser
2. Open DevTools (F12) > Network tab
3. Copy the `Cookie` header from any request
4. Save: `promote auth set-cookie juejin "your_cookie_string"`

```bash
PROMOTE_JUEJIN_COOKIE=xxx
PROMOTE_CSDN_COOKIE=xxx
PROMOTE_ZHIHU_COOKIE=xxx
```

**博客园 (CNBlogs)** — Official API, get token from Settings:
```bash
PROMOTE_CNBLOGS_BLOG_URL=your_blog_id
PROMOTE_CNBLOGS_USERNAME=xxx
PROMOTE_CNBLOGS_TOKEN=xxx
```

## Content Templates

Three built-in Jinja2 templates:

| Template | Use Case | Key Variables |
|----------|----------|---------------|
| `github_project_announce` | New project launch | `project_name`, `description`, `github_url`, `features` |
| `project_update` | Version release | `project_name`, `version`, `summary`, `changes` |
| `tutorial_share` | Technical tutorial | `title`, `introduction`, `prerequisites`, `steps` |

Example:
```bash
promote post --all \
  --template github_project_announce \
  --var project_name="My AI Tool" \
  --var description="AI-powered automation" \
  --var github_url="https://github.com/user/my-ai-tool" \
  --url "https://github.com/user/my-ai-tool" \
  --tag ai --tag automation
```

## OpenClaw Integration

This project works as an [OpenClaw](https://github.com/anthropics/openclaw) Skill.

### Install as OpenClaw Skill

```bash
git clone https://github.com/ava-agent/promotion-agent.git ~/.openclaw/skills/promotion-agent
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

See `openclaw.json.example` for the full template.

### Usage with OpenClaw

Once configured, just tell the agent:

> "Help me promote my project on all platforms"

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

# Run with coverage
pytest --cov=promotion_agent
```

## License

[MIT](LICENSE)
