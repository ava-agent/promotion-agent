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
