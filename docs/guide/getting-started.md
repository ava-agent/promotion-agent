# Getting Started

Promotion Agent is a **Claude Code Plugin** for automated multi-platform publishing, plus a curated guide for additional tools.

## Two Components

### 1. Claude Code Plugin (This Project)

Native integration with Claude Code for seamless publishing:

| Platform | Status | Auth Method |
|----------|--------|-------------|
| **知乎 (Zhihu)** | ✅ Ready | Cookie (auto-extract) |
| **小红书** | ✅ Ready | QR Code Login |
| **X/Twitter** | ✅ Ready | OAuth 1.0a |
| **微信公众号** | 🚧 WIP | AppID + Secret |

**Features:**
- Natural language commands: "帮我把这篇文章发到知乎"
- Content adaptation per platform
- Health checks and validation
- Auto cookie extraction (Zhihu)

### 2. External Tools Guide

For platforms not yet integrated, this guide recommends the best tools:

| Need | Recommended Tool |
|------|-----------------|
| Chinese tech blogs (掘金, CSDN, etc.) | [blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools) |
| International social (LinkedIn, Reddit) | [Postiz](https://github.com/gitroomhq/postiz-app) |
| GitHub Release notifications | GitHub Actions |
| Video platforms (抖音, Bilibili) | [social-auto-upload](https://github.com/dreammis/social-auto-upload) |

## Why This Guide?

Promoting your open-source project manually across platforms is time-consuming and repetitive. This guide and plugin help you automate the entire process.

## Quick Decision

### Option 1: Built-in Plugin (Recommended)

For supported platforms, use the Claude Code plugin directly:

```bash
# Install
git clone https://github.com/kevinten10/promotion-agent.git
cd promotion-agent
python3 get_zhihu_cookie.py  # Auto-setup for Zhihu

# Use in Claude Code
"帮我把这篇文章发到知乎"
"发布到小红书"
```

### Option 2: External Tools

For additional platforms, use these recommended tools:

| Your Need | Recommended Tool | Setup Time |
|-----------|-----------------|------------|
| More Chinese platforms (掘金, CSDN, etc.) | [blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools) | ~30 min |
| International social (LinkedIn, Reddit) | [Postiz](https://github.com/gitroomhq/postiz-app) | ~1 hour |
| GitHub Release notifications | GitHub Actions | ~10 min |
| Video platforms (抖音, Bilibili) | [social-auto-upload](https://github.com/dreammis/social-auto-upload) | ~30 min |

## Recommended Workflow

For full coverage across both Chinese and international platforms, combine multiple tools:

![Architecture Workflow](/images/architecture-workflow.png)

1. **Write your content** in Markdown
2. **Chinese platforms** → Use `blog-auto-publishing-tools` to publish to 8+ platforms
3. **International platforms** → Use `Postiz` (self-hosted) for AI-powered cross-posting
4. **GitHub releases** → Set up `GitHub Actions` for automatic notifications

## Next Steps

### Using This Plugin
- [Chinese Platforms](/platforms/chinese) — Built-in platform setup (知乎, 小红书)
- [MCP Tools](/reference/cli) — Available commands and tools

### External Tools
- [Tool Selection Guide](/guide/tool-selection) — Compare all options in detail
- [Chinese Platforms (External)](/guide/chinese-platforms) — Additional Chinese platforms
- [International Platforms](/guide/international-platforms) — International platforms
- [GitHub Automation](/guide/github-automation) — Automate release notifications
