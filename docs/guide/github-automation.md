# GitHub Automation

Automatically notify social media platforms when you publish a GitHub Release.

## Recommended Tools

| Tool | Purpose |
|------|---------|
| [ethomson/send-tweet-action](https://github.com/ethomson/send-tweet-action) | Auto-tweet on GitHub Release |
| [sarisia/actions-status-discord](https://github.com/sarisia/actions-status-discord) | Release notifications to Discord |

## Setup

### Twitter Notifications

Create `.github/workflows/release-tweet.yml`:

```yaml
name: Tweet on Release
on:
  release:
    types: [published]

jobs:
  tweet:
    runs-on: ubuntu-latest
    steps:
      - uses: ethomson/send-tweet-action@v1
        with:
          status: |
            🚀 New release: ${{ github.event.release.name }}

            ${{ github.event.release.body }}

            Check it out: ${{ github.event.release.html_url }}
          consumer_key: ${{ secrets.TWITTER_CONSUMER_KEY }}
          consumer_secret: ${{ secrets.TWITTER_CONSUMER_SECRET }}
          access_token: ${{ secrets.TWITTER_ACCESS_TOKEN }}
          access_token_secret: ${{ secrets.TWITTER_ACCESS_TOKEN_SECRET }}
```

### Discord Notifications

Create `.github/workflows/release-discord.yml`:

```yaml
name: Discord Release Notification
on:
  release:
    types: [published]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - uses: sarisia/actions-status-discord@v1
        with:
          webhook: ${{ secrets.DISCORD_WEBHOOK }}
          title: "New Release: ${{ github.event.release.name }}"
          description: ${{ github.event.release.body }}
          url: ${{ github.event.release.html_url }}
          color: 0x00ff00
```

## Required Secrets

Set these in your GitHub repository settings (Settings → Secrets → Actions):

### For Twitter
| Secret | Description |
|--------|-------------|
| `TWITTER_CONSUMER_KEY` | Twitter API consumer key |
| `TWITTER_CONSUMER_SECRET` | Twitter API consumer secret |
| `TWITTER_ACCESS_TOKEN` | Twitter access token |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret |

### For Discord
| Secret | Description |
|--------|-------------|
| `DISCORD_WEBHOOK` | Discord channel webhook URL |

::: tip Getting Twitter API Keys
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create a project and app
3. Generate consumer keys and access tokens
4. Add them as GitHub repository secrets
:::
