# CLI Reference

Complete command reference for the `promote` CLI tool.

## Installation

```bash
pip install -e .
# or
pip install -e ~/.openclaw/skills/promotion-agent
```

## Commands

### `promote post`

Post content to one or more platforms.

```bash
# Post to all configured platforms
promote post --all --title "TITLE" --body "BODY" --url "URL" --tag TAG

# Post to a single platform
promote post -p PLATFORM --title "TITLE" --body "BODY"

# Preview without posting
promote post --all --dry-run --title "TITLE" --body "BODY"

# Save as draft (Dev.to only)
promote post -p devto --draft --title "TITLE" --body "BODY"
```

**Options:**

| Flag | Description |
|------|-------------|
| `-p, --platform` | Target platform (can be repeated) |
| `--all` | Post to all configured platforms |
| `--title` | Post title |
| `--body` | Post body content |
| `--url` | Project URL (usually GitHub) |
| `--tag` | Content tags (can be repeated) |
| `--file` | Read body from a file |
| `--dry-run` | Preview only, don't post |
| `--draft` | Save as draft (Dev.to) |
| `--subreddit` | Target subreddit (Reddit) |

### Platform-Specific Examples

```bash
# Reddit (requires subreddit)
promote post -p reddit --subreddit Python --title "TITLE" --body "BODY"

# Dev.to (full markdown article)
promote post -p devto --title "TITLE" --file article.md --tag ai --tag python

# Hacker News (Show HN format)
promote post -p hackernews --title "Show HN: My AI Tool" --url "URL"

# Twitter (short announcement)
promote post -p x --title "Launched my project!" --url "URL" --tag ai

# Product Hunt (with tagline)
promote post -p producthunt --title "My Tool" --body "Tagline" --url "URL"

# Chinese platforms
promote post -p juejin --title "标题" --body "内容"
promote post -p csdn --title "标题" --body "内容"
promote post -p zhihu --title "标题" --body "内容"
promote post -p cnblogs --title "标题" --body "内容"
```

---

### `promote platforms`

Manage and inspect platforms.

```bash
# List all registered platforms
promote platforms list

# Health check all platforms
promote platforms check
```

---

### `promote templates`

Manage content templates.

```bash
# List available templates
promote templates list

# Render a template with variables
promote templates render github_project_announce \
  --var project_name="NAME" \
  --var description="DESC" \
  --var github_url="URL"
```

**Available Templates:**
- `github_project_announce` — GitHub project launch announcement
- `project_update` — Project update post
- `tutorial_share` — Tutorial sharing post

---

### `promote config`

View and validate configuration.

```bash
# Show current config (secrets masked)
promote config show

# Validate all credentials
promote config validate
```

---

### `promote auth`

Manage authentication cookies.

```bash
# Show auth status for all platforms
promote auth status

# Set cookie for a platform
promote auth set-cookie juejin "cookie_string"
promote auth set-cookie csdn "cookie_string"
promote auth set-cookie zhihu "cookie_string"

# Clear a platform's cookie
promote auth clear-cookie juejin
```

## Environment Variables

All configuration uses the `PROMOTE_` prefix:

```bash
# MoltBook
PROMOTE_MOLTBOOK_API_KEY=

# Reddit
PROMOTE_REDDIT_CLIENT_ID=
PROMOTE_REDDIT_CLIENT_SECRET=
PROMOTE_REDDIT_USERNAME=
PROMOTE_REDDIT_PASSWORD=

# Dev.to
PROMOTE_DEVTO_API_KEY=

# Hacker News
PROMOTE_HN_USERNAME=
PROMOTE_HN_PASSWORD=

# Twitter / X
PROMOTE_X_CONSUMER_KEY=
PROMOTE_X_CONSUMER_SECRET=
PROMOTE_X_ACCESS_TOKEN=
PROMOTE_X_ACCESS_TOKEN_SECRET=

# Product Hunt
PROMOTE_PRODUCTHUNT_TOKEN=

# LinkedIn
PROMOTE_LINKEDIN_ACCESS_TOKEN=

# Chinese platforms (cookie auth)
PROMOTE_JUEJIN_COOKIE=
PROMOTE_CSDN_COOKIE=
PROMOTE_ZHIHU_COOKIE=

# CNBlogs (MetaWeblog API)
PROMOTE_CNBLOGS_BLOG_URL=
PROMOTE_CNBLOGS_USERNAME=
PROMOTE_CNBLOGS_TOKEN=

# General
PROMOTE_GITHUB_USERNAME=
```
