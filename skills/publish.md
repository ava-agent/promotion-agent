---
name: publish
description: Publish articles to social media platforms (21 platforms including 知乎, 掘金, CSDN, 小红书, 微信公众号, X/Twitter, Medium, Hashnode, Dev.to, Reddit, LinkedIn, etc). Use when user asks to publish, post, promote, or share content to social platforms.
---

# Social Media Publisher

Publish content to supported platforms through the promotion-agent MCP server.

## Supported Platforms

**Chinese**: 知乎 (zhihu), 掘金 (juejin), CSDN (csdn), 小红书 (xiaohongshu), 微信公众号 (wechat), 微博 (weibo), V2EX (v2ex), SegmentFault (segmentfault), OSCHINA (oschina), 博客园 (cnblogs)
**International**: X/Twitter (x), Medium (medium), Hashnode (hashnode), Dev.to (devto), Reddit (reddit), LinkedIn (linkedin), Product Hunt (producthunt), Hacker News (hackernews), MoltBook (moltbook)
**AI Directories**: TAAFT, Futurepedia, Toolify

## Workflow

1. **Identify content source**
   - If user provides a file path, read the file
   - If file matches `*-社媒版.md` pattern, auto-split by `## ` headings:
     - "微信公众号" / "公众号" → wechat
     - "知乎" → zhihu
     - "小红书" → xiaohongshu
     - "X" / "Twitter" / "Thread" → x
     - "掘金" → juejin
     - "CSDN" → csdn
     - "Medium" → medium
     - "Hashnode" → hashnode
     - "Dev.to" → devto
     - "Reddit" → reddit
     - "LinkedIn" → linkedin
     - "微博" / "Weibo" → weibo
     - "V2EX" → v2ex
     - "SegmentFault" → segmentfault
     - "OSCHINA" / "开源中国" → oschina
     - "博客园" / "CNBlogs" → cnblogs
   - Otherwise use conversation context

2. **Confirm target platforms**
   - Ask user which platforms to publish to (if not obvious from content)
   - Show available platforms via `list_platforms` tool

3. **Check authentication**
   - Call `auth_status` tool
   - If any target platform is not configured, guide user:
     - 知乎/掘金/CSDN/SegmentFault/OSCHINA: "Please paste your cookie (F12 → Network → Cookie header)"
     - X: "Set PROMOTE_X_* env vars in .env"
     - 小红书: "Use auth_qr_login to scan QR code"
     - 微信: "Set PROMOTE_WECHAT_* env vars in .env"
     - Dev.to: "Set PROMOTE_DEVTO_API_KEY from dev.to/settings/extensions"
     - Medium: "Set PROMOTE_MEDIUM_INTEGRATION_TOKEN from medium.com/me/settings/security"
     - Hashnode: "Set PROMOTE_HASHNODE_TOKEN from hashnode.com/settings/developer"
     - Reddit: "Set PROMOTE_REDDIT_* env vars"
     - LinkedIn: "Set PROMOTE_LINKEDIN_ACCESS_TOKEN (OAuth 2.0, expires ~60 days)"
     - Product Hunt: "Set PROMOTE_PRODUCTHUNT_TOKEN"
     - V2EX: "Set PROMOTE_V2EX_TOKEN from v2ex.com/settings/tokens"
     - 微博: "Set PROMOTE_WEIBO_ACCESS_TOKEN (requires open platform app)"
     - 博客园: "Set PROMOTE_CNBLOGS_* env vars"
     - Hacker News: "Set PROMOTE_HN_USERNAME and PROMOTE_HN_PASSWORD"
     - MoltBook: "Set PROMOTE_MOLTBOOK_API_KEY"

4. **Preview content**
   - For original 4 platforms: call `publish_<platform>` with `dry_run: true`
   - For other platforms: call `publish(platform=..., dry_run=true)`
   - For AI directories: call `submit_directory(directory=..., dry_run=true)`
   - Show adapted content per platform
   - For X/Twitter threads, show numbered tweet list with character counts
   - Ask user to confirm

5. **Publish**
   - Call tools with `dry_run: false`
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
