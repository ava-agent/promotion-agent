# promotion-agent

Claude Code Plugin for multi-platform social media publishing.

Supports: **知乎** · **小红书** · **X/Twitter** · **微信公众号**

## Installation

```bash
# Clone to Claude Code plugins directory
git clone https://github.com/ava-agent/promotion-agent ~/.claude/plugins/promotion-agent

# Install Python dependencies
cd ~/.claude/plugins/promotion-agent
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

| Platform | Auth Type | Setup |
|----------|-----------|-------|
| 知乎 | Cookie | Browser F12 → Cookie header |
| X/Twitter | OAuth 1.0a | developer.x.com credentials |
| 微信公众号 | AppID+Secret | 微信公众平台 |
| 小红书 | QR Login | Automatic via `auth_qr_login` |

## Usage

In Claude Code, ask naturally:

- "帮我把这篇文章发到知乎"
- "Publish this to X as a thread"
- "发布到所有平台"

Or use the publish skill directly.

## MCP Tools

| Tool | Description |
|------|-------------|
| `publish_zhihu` | 发布到知乎专栏 |
| `publish_x` | 发推文（支持 Thread） |
| `publish_xiaohongshu` | 发布小红书笔记 |
| `publish_wechat` | 发布微信公众号文章 |
| `auth_status` | 查看认证状态 |
| `auth_set_cookie` | 设置 Cookie |
| `auth_qr_login` | 小红书扫码登录 |
| `auth_health_check` | 验证认证有效性 |
| `list_platforms` | 列出平台 |
| `preview_content` | 预览适配结果 |

## License

[MIT](LICENSE)
