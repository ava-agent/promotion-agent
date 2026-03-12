# Architecture

## Recommended Workflow

The recommended approach combines multiple specialized tools for complete platform coverage.

![Social Media Automation Workflow](/images/architecture-workflow.png)

### Content Paths

| Path | Flow | Use Case |
|------|------|----------|
| Chinese Platforms | Content → blog-auto-publishing-tools → Juejin, CSDN, Zhihu, CNBlogs | Tech blog cross-posting |
| International | Content → Postiz → Twitter, LinkedIn, Reddit, Instagram | Social media management |
| Release Automation | GitHub Release → Actions → Twitter + Discord | Automated notifications |

---

## Tech Stack Architecture

The promotion-agent reference implementation uses a three-layer architecture:

![Tech Stack Architecture](/images/tech-stack-architecture.png)

| Layer | Components | Purpose |
|-------|-----------|---------|
| **CLI Layer** | Typer, Rich, Jinja2 | User interface, formatting, templates |
| **Core Engine** | Orchestrator Agent, Plugin Registry, Content Adapter, Pydantic Settings | Coordination, discovery, transformation, config |
| **Platform Agents** | 11 specialized agents (httpx, praw, tweepy) | Platform-specific execution |

---

## Agent Execution Flow — ReAct Pattern

Each platform agent follows a **ReAct (Reason + Act)** loop:

![Agent Execution Flow — ReAct Pattern](/images/agent-react-flow.png)

### The Four Phases

| Phase | Action | Example |
|-------|--------|---------|
| **Observe** | Validate config, check platform health | `validate_config()` verifies API keys exist |
| **Think** | Adapt content to platform-specific format | `adapt_content()` truncates Twitter to 280 chars |
| **Act** | Execute API call | POST to platform API, handle OAuth, submit forms |
| **Reflect** | Check result, handle errors | Parse response, capture URL/error in `PostResult` |

### Complex Agent Workflows

**MoltBook** — Challenge-Response (ReAct with reasoning):
```
Submit content → Receive 202 + math challenge → Solve (X + Y) → Verify with answer
```

**Hacker News** — Stateful Web Agent:
```
Login (session cookie) → GET /submit (extract CSRF token) → POST /r (form submit)
```

Both demonstrate multi-step reasoning where the agent must observe intermediate states, make decisions, and adapt its actions accordingly.

---

## Design Patterns

The codebase implements six key patterns:

![Design Patterns & Agent Architecture](/images/design-patterns.png)

### Plugin Registry
```python
@register_platform
class RedditPlatform(BasePlatform):
    PLATFORM_NAME = "reddit"
    # Auto-registered, zero config
```
New platforms are added by creating a single file with the `@register_platform` decorator. No modifications to existing code required.

### Strategy Pattern
Each platform implements `adapt_content()` differently — Reddit truncates titles to 300 chars, Twitter limits to 280, Dev.to lowercases tags. The orchestrator doesn't know the details.

### Template Method
`BasePlatform` defines the contract (`validate_config`, `adapt_content`, `post`, `health_check`). Each platform fills in the implementation.

### Error Isolation
```python
for platform in targets:
    try:
        result = platform.post(content)
    except Exception as e:
        result = PostResult(success=False, error=str(e))
    results.append(result)
```
One platform failure never blocks others.

---

## Content Adaptation Pipeline

Generic content flows through platform-specific adapters:

![Content Adaptation Pipeline](/images/content-adaptation-pipeline.png)

| Platform | Title Limit | Body Limit | Special Handling |
|----------|------------|------------|-----------------|
| Reddit | 300 chars | Full markdown | Subreddit routing, URL footer |
| Twitter/X | — | 280 chars total | Hashtags from tags, URL appended |
| Dev.to | — | Full markdown | Max 4 lowercase tags, draft support |
| Hacker News | 80 chars | — (link post) | "Show HN:" prefix |
| Product Hunt | — | Tagline: 60 chars | GraphQL mutation |
| Chinese Platforms | — | Full content | Cookie auth, platform-specific JSON |

The adapter pattern ensures the orchestrator works with a single `PromotionContent` interface while each platform receives exactly the payload format it expects.
