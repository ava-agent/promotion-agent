# Getting Started

Promotion Agent is a curated guide to help developers automatically cross-post their projects to multiple social media platforms.

## Why This Guide?

Promoting your open-source project manually across platforms is time-consuming and repetitive. This guide recommends the best tools for each scenario, so you can automate the entire process.

## Quick Decision

| Your Need | Recommended Tool | Setup Time |
|-----------|-----------------|------------|
| Chinese tech blogs (Juejin, CSDN, Zhihu) | [blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools) | ~30 min |
| International social (Twitter, LinkedIn, Reddit) | [Postiz](https://github.com/gitroomhq/postiz-app) | ~1 hour |
| GitHub Release notifications | GitHub Actions | ~10 min |
| Video platforms (Douyin, Bilibili) | [social-auto-upload](https://github.com/dreammis/social-auto-upload) | ~30 min |

## Recommended Workflow

For full coverage across both Chinese and international platforms, combine multiple tools:

![Architecture Workflow](/images/architecture-workflow.png)

1. **Write your content** in Markdown
2. **Chinese platforms** → Use `blog-auto-publishing-tools` to publish to 8+ platforms
3. **International platforms** → Use `Postiz` (self-hosted) for AI-powered cross-posting
4. **GitHub releases** → Set up `GitHub Actions` for automatic notifications

## Next Steps

- [Tool Selection Guide](/guide/tool-selection) — Compare all options in detail
- [Chinese Platforms](/guide/chinese-platforms) — Setup guide for Chinese platforms
- [International Platforms](/guide/international-platforms) — Setup guide for international platforms
- [GitHub Automation](/guide/github-automation) — Automate release notifications
