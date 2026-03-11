# Promotion Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Archived](https://img.shields.io/badge/status-recommendations-orange.svg)](#recommended-tools)

> **This project is now a curated tool recommendation list.**
>
> After research, we found more mature open-source solutions. Use the tools below instead of reinventing the wheel.

---

## Supported Platforms (Reference)

![11 Supported Platforms](screenshots/platforms-overview.png)

---

## Recommended Tools

### Chinese Platforms (Juejin / CSDN / Zhihu / CNBlogs)

| Tool | Platforms | Features |
|------|----------|------|
| **[blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools)** | Juejin, CSDN, Zhihu, CNBlogs, SegmentFault, InfoQ, 51CTO, Toutiao | Python scripts, one-click publish to 8+ platforms |

```bash
# Install
git clone https://github.com/ddean2009/blog-auto-publishing-tools.git

# Usage
python publish.py --platform juejin,csdn,zhihu --file article.md
```

---

### International Platforms (Twitter / LinkedIn / Reddit)

| Tool | Stars | Platforms | Features |
|------|-------|----------|------|
| **[Postiz](https://github.com/gitroomhq/postiz-app)** | 25,000+ | Twitter, LinkedIn, Reddit, Instagram, TikTok, YouTube, Discord | AI-powered, self-hosted, Buffer alternative |
| **[social-media-agent](https://github.com/langchain-ai/social-media-agent)** | 1,400+ | Twitter, LinkedIn | By LangChain, AI content generation |
| **[Socioboard](https://github.com/socioboard/Socioboard-5.0)** | 1,000+ | Facebook, Twitter, LinkedIn, Instagram | Enterprise-grade, team collaboration |

---

### GitHub Auto-Publishing

| Tool | Purpose |
|------|------|
| **[ethomson/send-tweet-action](https://github.com/ethomson/send-tweet-action)** | Auto-tweet on GitHub Release |
| **[sarisia/actions-status-discord](https://github.com/sarisia/actions-status-discord)** | Release notifications to Discord |

```yaml
# .github/workflows/release.yml
on: release
jobs:
  tweet:
    runs-on: ubuntu-latest
    steps:
      - uses: ethomson/send-tweet-action@v1
        with:
          status: "New release: ${{ github.event.release.name }}"
          consumer_key: ${{ secrets.TWITTER_API_KEY }}
```

---

## Tool Selection Guide

![Tool Selection Guide](screenshots/tool-selection-guide.png)

| Requirement | Recommended Tool |
|------|----------|
| Chinese tech blog publishing | **blog-auto-publishing-tools** |
| International platforms + AI | **Postiz** or **social-media-agent** |
| GitHub Release automation | **GitHub Actions** |
| Enterprise team collaboration | **Socioboard** |
| Video platforms (Douyin/Bilibili) | [social-auto-upload](https://github.com/dreammis/social-auto-upload) |

---

## Architecture: Recommended Workflow

![Social Media Automation Workflow](screenshots/architecture-workflow.png)

---

## Resources

### Tutorials
- [blog-auto-publishing-tools setup guide](https://m.blog.csdn.net/gitblog_00974/article/details/147503658)
- [Postiz self-hosted deployment](https://www.toutiao.com/article/7489041338576208394/)
- [GitHub Actions Twitter integration](https://m.blog.csdn.net/gitblog_01036/article/details/152499233)

### Video Platforms
- [social-auto-upload](https://github.com/dreammis/social-auto-upload) - Douyin, Bilibili, Weishi, TikTok

### AI-Powered
- [social-media-agent](https://github.com/langchain-ai/social-media-agent) - By LangChain

---

## Archive Notes

This project (promotion-agent) was originally a custom social media publishing tool supporting 11 platforms. After research:

1. **Chinese platforms**: [blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools) has broader coverage (8+ platforms)
2. **International platforms**: [Postiz](https://github.com/gitroomhq/postiz-app) is more powerful (AI + self-hosted)
3. **GitHub integration**: GitHub Actions ecosystem is already mature

We recommend using these mature solutions directly. This project's code is preserved as reference and is no longer actively maintained.

---

## License

[MIT](LICENSE)
