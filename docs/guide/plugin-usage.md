# Plugin Usage Guide

Guide for using the built-in Claude Code plugin features.

## Installation

```bash
# Clone the repository
git clone https://github.com/kevinten10/promotion-agent.git
cd promotion-agent

# Copy environment template
cp .env.example .env
```

## Platform Setup

### 知乎 (Zhihu) - Auto Setup ⭐

The easiest platform to set up — uses automatic cookie extraction:

```bash
# 1. Ensure you're logged in to zhihu.com in Chrome
# 2. Run the auto-extraction script
python3 get_zhihu_cookie.py

# Output:
# 🔍 正在从 Chrome 读取知乎 Cookie...
# ✅ 找到 19 个 cookie 字段
# 📝 更新现有 Cookie...
# ✅ Cookie 已保存到 .env
# 🧪 测试 Cookie 有效性...
# ✅ Cookie 有效! 登录用户: YourName
```

That's it! The script automatically:
- Finds your Chrome profile
- Extracts all zhihu.com cookies
- Saves to `.env` file
- Validates the cookie works

**When cookie expires** (~1 month), just re-run the script.

### 小红书 - QR Code Login

```bash
# In Claude Code, run:
promote auth qr-login xiaohongshu

# Or use MCP tool:
# auth_qr_login(platform="xiaohongshu")
```

Scan the QR code with the Xiaohongshu app to authenticate.

### X/Twitter - OAuth Setup

1. Go to https://developer.x.com
2. Create an app and get credentials
3. Add to `.env`:

```bash
PROMOTE_X_CONSUMER_KEY=your_key
PROMOTE_X_CONSUMER_SECRET=your_secret
PROMOTE_X_ACCESS_TOKEN=your_token
PROMOTE_X_ACCESS_TOKEN_SECRET=your_token_secret
```

## Using in Claude Code

### Natural Language Commands

```
"帮我把这篇文章发到知乎"
"Publish this to X"
"发布到所有已配置的平台"
"帮我写个推广文案然后发到小红书和知乎"
```

### Direct Tool Calls

```python
# Publish to Zhihu
publish_zhihu(
    title="我的文章标题",
    content="<p>文章内容（HTML格式）</p>",
    topics=["人工智能", "编程"]
)

# Publish to X
publish_x(
    text="推文内容",
    thread=True  # 是否以 thread 形式发布
)

# Check auth status
auth_status()

# Health check
auth_health_check(platform="zhihu")
```

## Content Format

### For 知乎 (Zhihu)

```markdown
---
title: 文章标题
zhihu_topics:
  - 人工智能
  - Python
zhihu_column: your-column-slug  # 可选：指定专栏
---

文章内容支持 Markdown，会自动转换为知乎编辑器格式。
```

### For 小红书 (Xiaohongshu)

```markdown
---
title: 笔记标题
images:
  - ./image1.png
  - ./image2.png
---

笔记正文内容...

#标签1 #标签2 #标签3
```

### For X/Twitter

```markdown
---
title: Thread Title
thread: true  # 发布为 thread
---

推文内容（自动分割为多条）
```

## Troubleshooting

### Cookie Expired

**知乎**: Re-run `python3 get_zhihu_cookie.py`

**其他平台**: Manually re-extract cookies from browser DevTools

### Health Check Failed

```bash
# Check specific platform
promote platforms check zhihu

# Check all platforms
promote platforms check
```

### Debug Mode

```bash
# Enable verbose logging
export PROMOTE_DEBUG=1
```

## Platform Support Matrix

| Platform | Auth | Auto-Setup | Status |
|----------|------|------------|--------|
| 知乎 | Cookie | ✅ Yes | Ready |
| 小红书 | QR Login | ✅ Yes | Ready |
| X/Twitter | OAuth 1.0a | ❌ Manual | Ready |
| 微信公众号 | AppID+Secret | ❌ Manual | WIP |

## See Also

- [Chinese Platforms](/platforms/chinese) — Detailed platform info
- [MCP Tools Reference](/reference/cli) — Complete API docs
- [Auto Cookie Script](/platforms/chinese#cookie-extraction-guide) — How the extraction works
