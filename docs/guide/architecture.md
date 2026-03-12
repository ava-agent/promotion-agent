# Architecture

The recommended approach combines multiple specialized tools for complete platform coverage.

## Workflow Diagram

![Social Media Automation Workflow](/images/architecture-workflow.png)

## How It Works

### Content Path 1: Chinese Platforms

```
Content (Markdown) → blog-auto-publishing-tools → Juejin, CSDN, Zhihu, CNBlogs
```

- Write content in Markdown
- Tool handles cookie auth and platform-specific formatting
- Publishes to 8+ Chinese tech platforms simultaneously

### Content Path 2: International Platforms

```
Content → Postiz (self-hosted) → Twitter, LinkedIn, Reddit, Instagram
```

- Postiz provides AI-assisted content adaptation
- Schedule posts for optimal timing
- Built-in analytics for engagement tracking

### Content Path 3: Release Automation

```
GitHub Release → GitHub Actions → Twitter notification + Discord notification
```

- Triggers automatically on every release
- Zero manual intervention required
- Customizable notification templates

## Why Multiple Tools?

No single tool covers all platforms well. The recommended architecture uses each tool for what it does best:

| Tool | Strength | Weakness |
|------|----------|----------|
| blog-auto-publishing-tools | Best CN platform coverage | No international platforms |
| Postiz | Best international + AI | No CN platform support |
| GitHub Actions | Best automation trigger | Limited to notifications |

By combining all three, you achieve full coverage with minimal manual effort.
