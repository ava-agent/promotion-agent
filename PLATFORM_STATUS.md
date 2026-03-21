# Platform Status

**Last updated**: 2026-03-19

## Overview

| Platform | Status | Notes |
|----------|--------|-------|
| 知乎 (Zhihu) | Stable | Cookie auth, API publishing |
| 掘金 (Juejin) | Good | Draft creation works; publish API may return "parameter error" — manual publish from drafts |
| CSDN | Limited | API may be blocked by WAF (403) — manual publish as fallback |
| 小红书 (Xiaohongshu) | Stable | External MCP proxy, QR code login |
| 微信公众号 (WeChat) | Stable | External MCP proxy (Arcs-MCP) |
| 微博 (Weibo) | Stable | OAuth 2.0, requires open platform app approval |
| V2EX | Stable | API v2 with personal access token |
| SegmentFault | Stable | Cookie auth |
| OSCHINA | Stable | Cookie auth |
| 博客园 (CNBlogs) | Stable | MetaWeblog XML-RPC, most reliable Chinese platform API |
| X/Twitter | Stable | OAuth 1.0a via tweepy, free tier: 500 posts/month |
| Medium | Stable | Integration Token, REST API v1 |
| Hashnode | Stable | Personal Access Token, GraphQL API |
| Dev.to | Stable | API Key, Forem REST API |
| Reddit | Stable | OAuth via praw library |
| LinkedIn | Stable | OAuth 2.0 (token expires ~60 days) |
| Product Hunt | Stable | Bearer Token, GraphQL API |
| Hacker News | Fragile | Web form scraping, no official API — may break on HTML changes |
| MoltBook | Stable | API Key, challenge-response verification |
| TAAFT | Best-effort | Form submission, CAPTCHA may require manual |
| Futurepedia | Best-effort | Form submission, CAPTCHA may require manual |
| Toolify | Best-effort | Form submission, CAPTCHA may require manual |

## Known Limitations

| Platform | Limitation | Workaround |
|----------|-----------|------------|
| 掘金 | Publish API unstable | Draft auto-created; publish manually at juejin.cn/editor/drafts |
| CSDN | WAF blocks API calls | Publish manually via CSDN web editor |
| Hacker News | Web scraping, no API | May fail on HN HTML changes; "please slow down" rate limit |
| 微博 | Requires platform app approval | Must register Weibo Open Platform application |
| LinkedIn | Token expires in 60 days | Re-obtain via OAuth 2.0 flow |
| AI Directories | CAPTCHA on some submissions | Manual submission if CAPTCHA detected |
