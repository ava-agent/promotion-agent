# Platform Overview

Promotion Agent supports cross-posting to 11 social media platforms across Chinese and international ecosystems.

![11 Supported Platforms](/images/platforms-overview.png)

## Platform Summary

### International Platforms (7)

| Platform | Auth Method | API Type | Best For |
|----------|------------|----------|----------|
| MoltBook | API Key | REST | AI/tech community |
| Reddit | OAuth | REST (PRAW) | Developer communities |
| Dev.to | API Key | REST | Technical articles |
| Hacker News | Username/Password | Web scraping | Project launches |
| X / Twitter | OAuth 1.0a | REST v2 | Short announcements |
| Product Hunt | Bearer Token | GraphQL v2 | Product launches |
| LinkedIn | OAuth 2.0 | REST | Professional network |

### Chinese Platforms (4)

| Platform | Auth Method | API Type | Best For |
|----------|------------|----------|----------|
| Juejin (掘金) | Cookie | REST | Chinese dev community |
| CSDN | Cookie | REST | Tech blogs (SEO) |
| Zhihu (知乎) | Cookie | REST | In-depth articles |
| CNBlogs (博客园) | Token | MetaWeblog XML-RPC | Traditional blogs |

## Auth Methods Comparison

| Method | Platforms | Lifetime | Auto-Refresh |
|--------|----------|----------|-------------|
| API Key | MoltBook, Dev.to | Long-lived | N/A |
| OAuth 1.0a | Twitter | Long-lived | N/A |
| OAuth 2.0 | LinkedIn | 60 days | Manual |
| OAuth | Reddit | Session | Via PRAW |
| Bearer Token | Product Hunt | Long-lived | N/A |
| Cookie | Juejin, CSDN, Zhihu | ~1 month | Manual re-extract |
| MetaWeblog API | CNBlogs | Long-lived | N/A |
| Username/Password | Hacker News | Session | Per-request |
