# Tool Selection Guide

Choose the right tool based on your target platforms and requirements.

![Tool Selection Guide](/images/tool-selection-guide.png)

## Comparison Table

| Requirement | Recommended Tool | Stars | Key Feature |
|-------------|-----------------|-------|-------------|
| Chinese tech blog publishing | **[blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools)** | 1,000+ | One-click to 8+ CN platforms |
| International platforms + AI | **[Postiz](https://github.com/gitroomhq/postiz-app)** | 25,000+ | AI-powered, self-hosted |
| AI content generation | **[social-media-agent](https://github.com/langchain-ai/social-media-agent)** | 1,400+ | LangChain-based |
| Enterprise team collaboration | **[Socioboard](https://github.com/socioboard/Socioboard-5.0)** | 1,000+ | Team management |
| GitHub Release automation | **GitHub Actions** | — | Native CI/CD |
| Video platforms (Douyin/Bilibili) | **[social-auto-upload](https://github.com/dreammis/social-auto-upload)** | — | Video auto-upload |

## Detailed Comparison

### blog-auto-publishing-tools

**Best for**: Chinese tech blogs

| Aspect | Details |
|--------|---------|
| Platforms | Juejin, CSDN, Zhihu, CNBlogs, SegmentFault, InfoQ, 51CTO, Toutiao |
| Language | Python |
| Auth | Browser cookies (auto-extraction supported) |
| Input | Markdown files |

```bash
# Quick start
git clone https://github.com/ddean2009/blog-auto-publishing-tools.git
python publish.py --platform juejin,csdn,zhihu --file article.md
```

### Postiz

**Best for**: International social media with AI assistance

| Aspect | Details |
|--------|---------|
| Platforms | Twitter, LinkedIn, Reddit, Instagram, TikTok, YouTube, Discord |
| Deployment | Self-hosted (Docker) |
| Features | AI content generation, scheduling, analytics |
| Alternative to | Buffer, Hootsuite |

### social-media-agent

**Best for**: AI-driven content creation for developers

| Aspect | Details |
|--------|---------|
| Platforms | Twitter, LinkedIn |
| Built with | LangChain |
| Features | AI generates platform-specific content |

### GitHub Actions

**Best for**: Automated notifications on releases

| Aspect | Details |
|--------|---------|
| Platforms | Twitter, Discord (via actions) |
| Trigger | GitHub Release events |
| Setup | YAML workflow file |

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
