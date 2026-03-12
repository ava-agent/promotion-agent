# International Platforms

Detailed setup and usage guides for each international platform.

## Reddit

| Attribute | Value |
|-----------|-------|
| Auth | OAuth (`PROMOTE_REDDIT_CLIENT_ID`, `PROMOTE_REDDIT_CLIENT_SECRET`) |
| API | REST via PRAW library |
| Limits | Follow subreddit rules, avoid cross-sub spam |

**Recommended Subreddits:**
- r/MachineLearning — AI/ML projects
- r/artificial — AI discussion
- r/Python — Python projects
- r/opensource — Open source projects
- r/SideProject — Side projects

**Tips:**
- Self-posts preferred over link posts
- Engage in comments after posting
- Never cross-post to too many subreddits at once

---

## Dev.to

| Attribute | Value |
|-----------|-------|
| Auth | API Key (`PROMOTE_DEVTO_API_KEY`) |
| API | REST |
| Content | Full markdown support, max 4 tags |

**Tips:**
- Use `--draft` to preview before publishing
- Add description for better SEO
- Tags help discoverability
- Great for long-form technical articles

---

## Hacker News

| Attribute | Value |
|-----------|-------|
| Auth | Username/Password (`PROMOTE_HN_USERNAME`, `PROMOTE_HN_PASSWORD`) |
| API | Web form scraping (no official API) |
| Limits | Title max 80 chars, anti-spam rate limiting |

**Tips:**
- Use "Show HN:" prefix for project launches
- Link posts preferred
- Wait between submissions to avoid spam filters
- Title is crucial — keep it concise and compelling

---

## X / Twitter

| Attribute | Value |
|-----------|-------|
| Auth | OAuth 1.0a (4 keys required) |
| API | Official v2 API via tweepy |
| Limits | 280 chars, 500 posts/month (free tier) |

**Tips:**
- Include project URL
- Use relevant hashtags
- Short, punchy announcements work best
- Thread for longer content

---

## Product Hunt

| Attribute | Value |
|-----------|-------|
| Auth | Bearer Token (`PROMOTE_PRODUCTHUNT_TOKEN`) |
| API | GraphQL v2 |
| Limits | Tagline max 60 chars |

**Tips:**
- Best for launching new products/tools
- Include product URL
- Get token from developer portal
- Time launches for maximum visibility

---

## LinkedIn

| Attribute | Value |
|-----------|-------|
| Auth | OAuth 2.0 (`PROMOTE_LINKEDIN_ACCESS_TOKEN`) |
| API | ugcPosts REST API |
| Limits | Token expires every 60 days |

**Tips:**
- Professional tone
- Good for project milestones and launches
- Manually refresh token every 60 days
- Include relevant hashtags

---

## MoltBook

| Attribute | Value |
|-----------|-------|
| Auth | API Key (`PROMOTE_MOLTBOOK_API_KEY`) |
| API | REST with challenge-response |
| Limits | 1 post per 30 minutes |

**Tips:**
- AI agent network — tech/AI content
- Challenge-response handled automatically by the CLI
- Rate limit: wait 30 min between posts
