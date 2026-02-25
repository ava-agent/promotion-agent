---
name: promotion-agent
description: Promote GitHub projects to 11 social platforms (MoltBook, Reddit, Dev.to, Hacker News, X/Twitter, Product Hunt, LinkedIn, 掘金, CSDN, 知乎, 博客园). Create posts, cross-post with platform-adapted content, manage templates.
version: 3.0.0
author: kevinten10
homepage: https://github.com/ava-agent/promotion-agent
tags:
  - social
  - promotion
  - marketing
  - developer
  - cross-post
metadata: {"openclaw":{"emoji":"📣","category":"social","requires":{"bins":["promote"],"env":["PROMOTE_MOLTBOOK_API_KEY"]},"install":[{"type":"shell","command":"pip install -e ~/.openclaw/skills/promotion-agent"}]}}
---

# Promotion Agent

Post and promote GitHub projects across 11 social platforms with one command.

## Platforms

| Name | Command Flag | Auth |
|------|-------------|------|
| MoltBook | `-p moltbook` | API Key (env: `PROMOTE_MOLTBOOK_API_KEY`) |
| Reddit | `-p reddit` | OAuth (env: `PROMOTE_REDDIT_CLIENT_ID`, `PROMOTE_REDDIT_CLIENT_SECRET`, `PROMOTE_REDDIT_USERNAME`, `PROMOTE_REDDIT_PASSWORD`) |
| Dev.to | `-p devto` | API Key (env: `PROMOTE_DEVTO_API_KEY`) |
| Hacker News | `-p hackernews` | Username/Password (env: `PROMOTE_HN_USERNAME`, `PROMOTE_HN_PASSWORD`) |
| X (Twitter) | `-p x` | OAuth 1.0a (env: `PROMOTE_X_CONSUMER_KEY`, `PROMOTE_X_CONSUMER_SECRET`, `PROMOTE_X_ACCESS_TOKEN`, `PROMOTE_X_ACCESS_TOKEN_SECRET`) |
| Product Hunt | `-p producthunt` | Bearer Token (env: `PROMOTE_PRODUCTHUNT_TOKEN`) |
| LinkedIn | `-p linkedin` | OAuth 2.0 (env: `PROMOTE_LINKEDIN_ACCESS_TOKEN`) |
| 掘金 | `-p juejin` | Cookie (env: `PROMOTE_JUEJIN_COOKIE`) |
| CSDN | `-p csdn` | Cookie (env: `PROMOTE_CSDN_COOKIE`) |
| 知乎 | `-p zhihu` | Cookie (env: `PROMOTE_ZHIHU_COOKIE`) |
| 博客园 | `-p cnblogs` | Token (env: `PROMOTE_CNBLOGS_BLOG_URL`, `PROMOTE_CNBLOGS_USERNAME`, `PROMOTE_CNBLOGS_TOKEN`) |

## Quick Start

### First Run

```bash
pip install -e ~/.openclaw/skills/promotion-agent
promote platforms list
```

### Verify Credentials

```bash
promote config validate
promote platforms check
```

## Core Commands

### Post to Platforms

```bash
# All configured platforms
promote post --all --title "TITLE" --body "BODY" --url "GITHUB_URL" --tag TAG

# Single platform
promote post -p moltbook --title "TITLE" --body "BODY"
promote post -p reddit --subreddit SUBREDDIT --title "TITLE" --body "BODY"
promote post -p devto --title "TITLE" --file /path/to/article.md --tag ai --tag python
promote post -p juejin --title "标题" --body "内容"
promote post -p csdn --title "标题" --body "内容"
promote post -p zhihu --title "标题" --body "内容"
promote post -p cnblogs --title "标题" --body "内容"
promote post -p hackernews --title "Show HN: My AI Tool" --url "GITHUB_URL"
promote post -p x --title "Launched my AI project!" --url "GITHUB_URL" --tag ai
promote post -p producthunt --title "My AI Tool" --body "Tagline here" --url "GITHUB_URL"
promote post -p linkedin --title "Excited to share..." --body "BODY" --url "GITHUB_URL"

# Preview without posting
promote post --all --dry-run --title "TITLE" --body "BODY"

# Save as draft (Dev.to)
promote post -p devto --draft --title "TITLE" --body "BODY"
```

### Use Templates

```bash
promote templates list
promote templates render github_project_announce \
  --var project_name="NAME" \
  --var description="DESC" \
  --var github_url="URL"
```

### Management

```bash
promote platforms list      # Show registered platforms
promote platforms check     # Health check all
promote config show         # Show config (secrets masked)
promote config validate     # Validate credentials
```

## Workflow

When the user asks to promote a project, follow this exact flow:

1. **Gather info**: Ask for project name, GitHub URL, target platforms, key features
2. **Pick language**: International platforms → English. 国内平台 → 中文
3. **Draft content**: Use templates or write custom. Adapt per platform — never post identical content
4. **Dry run first**: Always run `promote post --dry-run` and show the preview
5. **Confirm**: Ask the user "Should I post this?" before executing
6. **Post**: Run `promote post` with the confirmed content
7. **Report**: Show the results table with URLs for each platform

## Platform Rules

**MoltBook** — AI agent network. Tech/AI content. Challenge-response handled automatically. Rate limit: 1 post per 30 min.

**Reddit** — Follow subreddit rules. Good subs: MachineLearning, artificial, Python, opensource, SideProject. Self-posts preferred. No cross-sub spam.

**Dev.to** — Full markdown. Max 4 tags. Use `--draft` to preview first. Add description for SEO.

**掘金** — Cookie auth (expires ~1 month). Draft → publish flow. Set category_id in metadata for correct channel.

**CSDN** — Cookie auth (expires ~1 month). Direct publish. Largest Chinese dev community.

**知乎** — Cookie auth (expires ~1 month). Publishes to 专栏 (column articles). Good for deep technical content.

**博客园** — Official MetaWeblog API. Token auth (long-lived). Most stable Chinese platform API.

**Hacker News** — No official API, web form scraping. Title max 80 chars. Use "Show HN:" prefix for project launches. Link posts preferred. Anti-spam: wait between submissions.

**X (Twitter)** — Official v2 API via tweepy. 280-char limit. Free tier: 500 posts/month. Include URL and hashtags. Short, punchy announcements.

**Product Hunt** — GraphQL v2 API. Bearer token from developer portal. Best for product launches. Tagline max 60 chars. Include product URL.

**LinkedIn** — ugcPosts API. OAuth 2.0 token (expires 60 days, refresh manually). Professional tone. Good for project milestones and launches.

## Cookie Auto-Extraction (Browser)

For Chinese platforms (掘金/CSDN/知乎) that use Cookie auth, you can auto-extract cookies using the OpenClaw browser tool instead of asking the user to manually copy from F12.

### Extraction Workflow

When a cookie-based platform shows "Missing credentials" or the user asks to set up auth:

1. **Open browser** to the platform's login page using the `computer` tool:
   - 掘金: `https://juejin.cn`
   - CSDN: `https://www.csdn.net`
   - 知乎: `https://www.zhihu.com`

2. **Check login status**: Look for a user avatar or username in the page. If not logged in, tell the user to log in manually in the browser, then retry.

3. **Extract cookies** via JavaScript execution in the `computer` tool:
   ```javascript
   document.cookie
   ```

4. **Save the cookie** using the CLI:
   ```bash
   promote auth set-cookie juejin "extracted_cookie_string"
   ```

5. **Verify** with:
   ```bash
   promote auth status
   promote platforms check
   ```

### Auth Management Commands

```bash
promote auth status                          # Show cookie status for all platforms
promote auth set-cookie juejin "cookie..."   # Save cookie for 掘金
promote auth set-cookie csdn "cookie..."     # Save cookie for CSDN
promote auth set-cookie zhihu "cookie..."    # Save cookie for 知乎
promote auth clear-cookie juejin             # Remove saved cookie
```

### Tips

- Use **Extension Relay mode** (`openclaw browser --relay`) to connect to the user's existing Chrome with logged-in sessions — this avoids needing to log in again
- Cookies expire approximately every 1 month. If posting fails with auth errors, re-extract
- After extraction, always run `promote platforms check` to verify the cookie works

## Rules

1. **Always dry-run first** — Show preview, get confirmation
2. **Adapt per platform** — Different language, tone, format for each
3. **Include project URL** — Every post must link to the GitHub repo
4. **Respect rate limits** — Don't batch-post to many subreddits at once
5. **Cookie expiry** — Warn user if 国内平台 auth fails (cookies expire monthly)
6. **Auto-extract cookies** — When cookie auth is missing, offer to extract via browser before giving up
