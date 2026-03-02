# Promotion Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platforms: 11](https://img.shields.io/badge/platforms-11-green.svg)](#supported-platforms)

**One command to post your GitHub/AI projects to 11 social media platforms.**

Supports both standalone CLI usage and [OpenClaw](https://github.com/anthropics/openclaw) AI Agent Skill integration.

## Demo

> 📸 **Screenshots placeholder** — Run the commands below to capture actual output

```
┌─────────────────────────────────────────────────────────────────┐
│                    Promotion Agent Workflow                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📝 Content        ┌──────────────────┐      ┌─────────────┐  │
│   (title + body)    │                  │      │  MoltBook   │  │
│        │            │   Promotion      │      │   Reddit    │  │
│        ▼            │     Agent        │─────▶│   Dev.to    │  │
│   📁 Template  ───▶ │                  │      │  HackerNews │  │
│        │            │   promote post   │      │   X/Twitter │  │
│        ▼            │     --all        │      │ ProductHunt │  │
│   ⚙️ Config         │                  │      │   LinkedIn  │  │
│   (API keys)        └──────────────────┘      │    掘金      │  │
│                                              │    CSDN      │  │
│                                              │    知乎      │  │
│                                              │   博客园     │  │
│                                              └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

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

---

## Complete Usage Guide

### Step 1: Install

```bash
# From source
pip install -e .

# From GitHub
pip install git+https://github.com/ava-agent/promotion-agent.git
```

### Step 2: Configure Credentials

Create a `.env` file in your project directory:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```bash
# International Platforms
PROMOTE_MOLTBOOK_API_KEY=mb_your_key
PROMOTE_REDDIT_CLIENT_ID=xxx
PROMOTE_REDDIT_CLIENT_SECRET=xxx
PROMOTE_REDDIT_USERNAME=xxx
PROMOTE_REDDIT_PASSWORD=xxx
PROMOTE_DEVTO_API_KEY=xxx
PROMOTE_HN_USERNAME=xxx
PROMOTE_HN_PASSWORD=xxx
PROMOTE_X_CONSUMER_KEY=xxx
PROMOTE_X_CONSUMER_SECRET=xxx
PROMOTE_X_ACCESS_TOKEN=xxx
PROMOTE_X_ACCESS_TOKEN_SECRET=xxx
PROMOTE_PRODUCTHUNT_TOKEN=xxx
PROMOTE_LINKEDIN_ACCESS_TOKEN=xxx

# Chinese Platforms (Cookie Auth)
PROMOTE_JUEJIN_COOKIE=xxx
PROMOTE_CSDN_COOKIE=xxx
PROMOTE_ZHIHU_COOKIE=xxx
PROMOTE_CNBLOGS_BLOG_URL=xxx
PROMOTE_CNBLOGS_USERNAME=xxx
PROMOTE_CNBLOGS_TOKEN=xxx
```

> 📸 **Screenshot:** `promote config show` output (secrets masked)

### Step 3: Verify Setup

```bash
# List all 11 platforms
promote platforms list
```

> 📸 **Screenshot:** `promote platforms list` — Rich table with all platforms

```bash
# Check which platforms have valid credentials
promote platforms check
```

> 📸 **Screenshot:** `promote platforms check` — Status table with ✓/✗

### Step 4: Create Content

#### Option A: Direct Content

```bash
promote post --all --dry-run \
  --title "My AI Project" \
  --body "An AI-powered tool that automates your workflow." \
  --url "https://github.com/user/my-project" \
  --tag ai --tag automation
```

#### Option B: From Markdown File

```bash
# Create article.md
promote post -p devto --file article.md --title "My Article" --tag python
```

#### Option C: Using Templates

```bash
# List available templates
promote templates list
```

> 📸 **Screenshot:** `promote templates list` — Template names and descriptions

```bash
# Render a template
promote templates render github_project_announce \
  --var project_name="My AI Tool" \
  --var description="AI-powered automation" \
  --var github_url="https://github.com/user/my-ai-tool" \
  --var features="11 platforms, CLI, OpenClaw integration"
```

> 📸 **Screenshot:** `promote templates render` — Rendered markdown output

### Step 5: Preview (Dry Run)

**Always preview before posting:**

```bash
promote post --all --dry-run \
  --title "My AI Project" \
  --body "Description here" \
  --url "https://github.com/user/repo" \
  --tag ai
```

> 📸 **Screenshot:** `promote post --dry-run` — Shows adapted content for each platform

### Step 6: Post

```bash
# Post to all configured platforms
promote post --all \
  --title "My AI Project" \
  --body "Description here" \
  --url "https://github.com/user/repo" \
  --tag ai

# Post to specific platforms
promote post -p devto -p reddit -p hackernews \
  --title "My AI Project" \
  --file article.md
```

> 📸 **Screenshot:** Post results — Success table with URLs

---

## CLI Reference

### `promote post`

```bash
promote post [OPTIONS]

Options:
  -p, --platform TEXT    Target platform (repeatable)
  --all                  Post to all configured platforms
  -t, --title TEXT       Post title (required)
  -b, --body TEXT        Post body text
  -f, --file PATH        Read body from markdown file
  --template TEXT        Use a named template
  --var TEXT             Template variable KEY=VALUE (repeatable)
  --tag TEXT             Tags (repeatable)
  --url TEXT             Project URL
  --subreddit TEXT       Reddit: target subreddit
  --submolt TEXT         MoltBook: target submolt
  --draft                Dev.to: save as draft
  --dry-run              Preview without posting
```

### `promote platforms`

```bash
promote platforms list     # List all platforms + required config
promote platforms check    # Health check API connectivity
```

### `promote auth`

```bash
promote auth status                          # Show cookie status
promote auth set-cookie juejin "cookie..."   # Save cookie
promote auth clear-cookie juejin             # Remove cookie
```

### `promote templates`

```bash
promote templates list                       # List templates
promote templates show github_project_announce
promote templates render github_project_announce --var key=value
```

### `promote config`

```bash
promote config show       # Show config (secrets masked)
promote config validate   # Validate credentials
```

---

## Platform Configuration

### International Platforms

| Platform | Where to Get Credentials |
|----------|-------------------------|
| **MoltBook** | [moltbook.com](https://moltbook.com) Settings |
| **Reddit** | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) — Create "script" app |
| **Dev.to** | [dev.to/settings/extensions](https://dev.to/settings/extensions) |
| **Hacker News** | Your HN account credentials |
| **X (Twitter)** | [developer.x.com](https://developer.x.com) — Create app, get 4 keys |
| **Product Hunt** | [api.producthunt.com/v2/oauth/applications](https://api.producthunt.com/v2/oauth/applications) |
| **LinkedIn** | [linkedin.com/developers](https://www.linkedin.com/developers/) — Token expires in 60 days |

### Chinese Platforms (Cookie Auth)

For 掘金, CSDN, 知乎:

```
1. Log in to the platform in your browser
2. Open DevTools (F12) > Network tab
3. Refresh page, click any request
4. Copy the "Cookie" value from Request Headers
5. Save: promote auth set-cookie juejin "your_cookie"
```

> 📸 **Screenshot:** Browser DevTools showing Cookie extraction

### 博客园 (CNBlogs)

Official MetaWeblog API — get token from blog settings:

```bash
PROMOTE_CNBLOGS_BLOG_URL=your_blog_id
PROMOTE_CNBLOGS_USERNAME=your_username
PROMOTE_CNBLOGS_TOKEN=your_api_token
```

---

## Content Templates

| Template | Use Case | Variables |
|----------|----------|-----------|
| `github_project_announce` | New project launch | `project_name`, `description`, `github_url`, `features`, `install_command` |
| `project_update` | Version release | `project_name`, `version`, `summary`, `github_url`, `changes` |
| `tutorial_share` | Technical tutorial | `title`, `introduction`, `github_url`, `prerequisites`, `steps` |

---

## OpenClaw Integration

### Install as Skill

```bash
git clone https://github.com/ava-agent/promotion-agent.git ~/.openclaw/skills/promotion-agent
bash ~/.openclaw/skills/promotion-agent/scripts/install.sh
```

### Configure

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

### Usage

> "Help me promote my project on all platforms"

The AI agent will:
1. Gather project details
2. Choose language per platform (English/Chinese)
3. Draft platform-adapted content
4. Preview with `--dry-run`
5. Ask confirmation
6. Post and report URLs

---

## Architecture

```
src/promotion_agent/
├── core/                  # Base abstractions
│   ├── base_platform.py   # BasePlatform ABC
│   ├── registry.py        # @register_platform decorator
│   ├── content.py         # PromotionContent dataclass
│   └── result.py          # PostResult dataclass
├── platforms/             # 11 platform adapters
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
├── config/                # Pydantic Settings
└── content/               # Jinja2 templates
```

---

## Development

```bash
pip install -e ".[dev]"
pytest                    # Run tests
ruff check src/ tests/    # Lint
pytest --cov=promotion_agent  # Coverage
```

## License

[MIT](LICENSE)
