# Promotion Agent

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Archived](https://img.shields.io/badge/status-recommendations-orange.svg)](#recommended-tools)

> **📋 这个项目现在是一份工具推荐清单。**
>
> 经过调研，发现已有更成熟的开源方案。建议直接使用以下工具，无需重复造轮子。

---

## 🏆 推荐工具

### 国内平台 (掘金/CSDN/知乎/博客园)

| 工具 | 支持平台 | 特点 |
|------|----------|------|
| **[blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools)** | 掘金, CSDN, 知乎, 博客园, SegmentFault, InfoQ, 51CTO, 今日头条 | Python 脚本，一键发布到 8+ 平台 |

```bash
# 安装
git clone https://github.com/ddean2009/blog-auto-publishing-tools.git

# 使用
python publish.py --platform juejin,csdn,zhihu --file article.md
```

---

### 国际平台 (Twitter/LinkedIn/Reddit)

| 工具 | Stars | 支持平台 | 特点 |
|------|-------|----------|------|
| **[Postiz](https://github.com/gitroomhq/postiz-app)** | 25,000+ | Twitter, LinkedIn, Reddit, Instagram, TikTok, YouTube, Discord | AI 驱动，自托管，替代 Buffer |
| **[social-media-agent](https://github.com/langchain-ai/social-media-agent)** | 1,400+ | Twitter, LinkedIn | LangChain 出品，AI 内容生成 |
| **[Socioboard](https://github.com/socioboard/Socioboard-5.0)** | 1,000+ | Facebook, Twitter, LinkedIn, Instagram | 企业级，团队协作 |

---

### GitHub 自动发布

| 工具 | 用途 |
|------|------|
| **[ethomson/send-tweet-action](https://github.com/ethomson/send-tweet-action)** | GitHub Release 自动发推 |
| **[sarisia/actions-status-discord](https://github.com/sarisia/actions-status-discord)** | 发布通知到 Discord |

```yaml
# .github/workflows/release.yml
on: release
jobs:
  tweet:
    runs-on: ubuntu-latest
    steps:
      - uses: ethomson/send-tweet-action@v1
        with:
          status: "🚀 New release: ${{ github.event.release.name }}"
          consumer_key: ${{ secrets.TWITTER_API_KEY }}
```

---

## 📊 工具对比

| 需求 | 推荐工具 |
|------|----------|
| 国内技术博客发布 | **blog-auto-publishing-tools** |
| 国际平台 + AI | **Postiz** 或 **social-media-agent** |
| GitHub Release 自动化 | **GitHub Actions** |
| 企业团队协作 | **Socioboard** |
| 视频平台 (抖音/B站) | [social-auto-upload](https://github.com/dreammis/social-auto-upload) |

---

## 🔧 组合方案

```
┌─────────────────────────────────────────────────────────────────┐
│                    推荐的社交媒体自动化架构                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📝 内容创作                                                    │
│      │                                                          │
│      ├──────────▶ blog-auto-publishing-tools                   │
│      │           ──▶ 掘金, CSDN, 知乎, 博客园                    │
│      │                                                          │
│      └──────────▶ Postiz (自托管)                               │
│                  ──▶ Twitter, LinkedIn, Reddit, Instagram       │
│                                                                 │
│   🚀 GitHub Release                                             │
│      │                                                          │
│      └──────────▶ GitHub Actions                                │
│                  ──▶ Twitter, Discord 通知                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 相关资源

### 教程文档
- [blog-auto-publishing-tools 安装配置教程](https://m.blog.csdn.net/gitblog_00974/article/details/147503658)
- [Postiz 自托管部署指南](https://www.toutiao.com/article/7489041338576208394/)
- [GitHub Actions Twitter 集成](https://m.blog.csdn.net/gitblog_01036/article/details/152499233)

### 视频平台
- [social-auto-upload](https://github.com/dreammis/social-auto-upload) - 抖音, B站, 视频号, TikTok

### AI 驱动
- [social-media-agent](https://github.com/langchain-ai/social-media-agent) - LangChain 出品

---

## 📁 本项目存档说明

本项目 (promotion-agent) 最初是一个自建的社交媒体发布工具，支持 11 个平台。但经过调研发现：

1. **国内平台**: [blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools) 支持更全面 (8+ 平台)
2. **国际平台**: [Postiz](https://github.com/gitroomhq/postiz-app) 功能更强大 (AI + 自托管)
3. **GitHub 集成**: GitHub Actions 生态已经很成熟

因此，建议直接使用上述成熟方案。本项目代码保留作为参考，不再主动维护。

---

## License

[MIT](LICENSE)
