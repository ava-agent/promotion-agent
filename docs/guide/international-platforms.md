# International Platforms

Publish to Twitter/X, LinkedIn, Reddit, and more using **Postiz** or **social-media-agent**.

## Recommended Tools

| Tool | Stars | Platforms | Best For |
|------|-------|----------|----------|
| [Postiz](https://github.com/gitroomhq/postiz-app) | 25,000+ | Twitter, LinkedIn, Reddit, Instagram, TikTok, YouTube, Discord | Full-featured, AI-powered |
| [social-media-agent](https://github.com/langchain-ai/social-media-agent) | 1,400+ | Twitter, LinkedIn | AI content generation |
| [Socioboard](https://github.com/socioboard/Socioboard-5.0) | 1,000+ | Facebook, Twitter, LinkedIn, Instagram | Enterprise teams |

## Postiz Setup (Recommended)

### 1. Self-Host with Docker

```bash
git clone https://github.com/gitroomhq/postiz-app.git
cd postiz-app
docker-compose up -d
```

### 2. Connect Platforms

1. Open `http://localhost:5000` in your browser
2. Connect your social accounts (OAuth flow)
3. Configure posting preferences

### 3. Publish

- Write content once, AI adapts for each platform
- Schedule posts for optimal engagement times
- Track analytics across all platforms

::: tip Why Postiz?
Postiz is a Buffer/Hootsuite alternative that you can self-host. With 25,000+ GitHub stars, it's the most popular open-source social media management tool.
:::

## Platform Details

### Twitter / X

- **Auth**: OAuth 1.0a (API keys from developer portal)
- **Limits**: 280 characters, 500 posts/month (free tier)
- **Tips**: Include URL, use hashtags, keep it punchy

### LinkedIn

- **Auth**: OAuth 2.0 (token expires every 60 days)
- **Content**: Professional tone, project milestones
- **Tips**: Good for project launches and career updates

### Reddit

- **Auth**: OAuth (client ID + secret)
- **Content**: Follow subreddit rules, avoid spam
- **Good subs**: r/MachineLearning, r/Python, r/opensource, r/SideProject
- **Tips**: Self-posts preferred, engage in comments

### Product Hunt

- **Auth**: Bearer token from developer portal
- **Content**: Product launches, tagline max 60 chars
- **Tips**: Best for launching new tools/products

### Dev.to

- **Auth**: API key
- **Content**: Full markdown articles, max 4 tags
- **Tips**: Use `--draft` to preview first, add description for SEO

### Hacker News

- **Auth**: Username/password (no official API)
- **Content**: Title max 80 chars, "Show HN:" prefix for launches
- **Tips**: Link posts preferred, anti-spam rate limiting applies
