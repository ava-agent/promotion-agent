---
name: promotion-agent
description: Publish content to 21 social platforms and AI directories via MCP. Supports 知乎, 掘金, CSDN, 小红书, 微信, X/Twitter, Medium, Hashnode, Dev.to, Reddit, LinkedIn, Product Hunt, 博客园, Hacker News, MoltBook, 微博, V2EX, SegmentFault, OSCHINA + AI directories (TAAFT, Futurepedia, Toolify).
version: 4.0.0
author: kevinten10
homepage: https://github.com/ava-agent/promotion-agent
tags:
  - social
  - promotion
  - marketing
  - developer
  - cross-post
  - mcp
---

# Promotion Agent

Claude Code Plugin for multi-platform content publishing. Publishes to 21 platforms with a single interaction.

## How It Works

This plugin provides an MCP Server with 12 tools. Claude calls these tools automatically when you ask to publish content.

### Quick Start

```
> Publish this article to Zhihu and Dev.to
> /publish
> Batch publish to all configured platforms
```

### Platforms

**Chinese**: 知乎, 掘金, CSDN, 小红书, 微信公众号, 微博, V2EX, SegmentFault, OSCHINA, 博客园
**International**: X/Twitter, Medium, Hashnode, Dev.to, Reddit, LinkedIn, Product Hunt, Hacker News, MoltBook
**AI Directories**: TAAFT, Futurepedia, Toolify

### Key Tools

| Tool | Usage |
|------|-------|
| `publish` | Generic publish to any platform |
| `publish_zhihu` / `publish_x` / `publish_xiaohongshu` / `publish_wechat` | Dedicated tools for original 4 |
| `submit_directory` | Submit to AI directory sites |
| `auth_status` | Check credential status |
| `list_platforms` | List all platforms |
| `preview_content` | Preview adapted content |

### Configuration

Copy `.env.example` to `.env` and fill in platform credentials. See README.md for per-platform setup guides.

### Workflow

1. Identify content source (file or conversation)
2. Select target platforms
3. Check auth status
4. Preview adapted content (dry_run)
5. Confirm and publish
6. Report results with URLs

## Rules

1. **Always dry-run first** — preview before publishing
2. **Adapt per platform** — different language, tone, format
3. **Include project URL** — every post links to the source
4. **Respect rate limits** — don't spam multiple subreddits
5. **Cookie expiry** — warn if auth fails (cookies expire monthly)
