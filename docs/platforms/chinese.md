# Chinese Platforms

Detailed setup and usage guides for each Chinese platform.

## Juejin (掘金)

| Attribute | Value |
|-----------|-------|
| URL | https://juejin.cn |
| Auth | Cookie (`PROMOTE_JUEJIN_COOKIE`) |
| API | REST — draft → publish flow |
| Expiry | ~1 month |

**Features:**
- Largest Chinese tech content platform
- Category-based content organization
- Rich markdown support
- Strong community engagement

**Tips:**
- Set `category_id` in metadata for correct channel
- Draft → publish flow ensures content quality
- Good for tutorials, project showcases, and tech deep-dives

---

## CSDN

| Attribute | Value |
|-----------|-------|
| URL | https://www.csdn.net |
| Auth | Cookie (`PROMOTE_CSDN_COOKIE`) |
| API | REST — direct publish |
| Expiry | ~1 month |

**Features:**
- Largest Chinese developer community overall
- Excellent SEO — content ranks well in Baidu
- Direct publish flow (no draft step)

**Tips:**
- Great for discoverability through search engines
- Content stays indexed long-term
- Good for documentation-style articles

---

## Zhihu (知乎)

| Attribute | Value |
|-----------|-------|
| URL | https://www.zhihu.com |
| Auth | Cookie (`PROMOTE_ZHIHU_COOKIE`) |
| API | REST — publishes to 专栏 (columns) |
| Expiry | ~1 month |

**Features:**
- Knowledge-sharing platform (Q&A + articles)
- High-quality audience
- Column (专栏) articles for long-form content

**Tips:**
- Best for deep technical content and thought leadership
- Engage with Q&A for additional visibility
- Professional tone works best

---

## CNBlogs (博客园)

| Attribute | Value |
|-----------|-------|
| URL | https://www.cnblogs.com |
| Auth | MetaWeblog API (`PROMOTE_CNBLOGS_TOKEN`) |
| API | XML-RPC (MetaWeblog standard) |
| Expiry | Long-lived |

**Features:**
- Official API — most stable among CN platforms
- Token-based auth (no cookie expiry issues)
- MetaWeblog standard compatibility

**Tips:**
- Most reliable API for automation
- No cookie re-extraction needed
- Good for traditional tech blogging

---

## Cookie Extraction Guide

For Juejin, CSDN, and Zhihu, you need to extract browser cookies:

### Manual Method

1. Log in to the platform in your browser
2. Open DevTools (`F12`) → **Application** → **Cookies**
3. Copy the full cookie string
4. Set as environment variable:

```bash
export PROMOTE_JUEJIN_COOKIE="your_cookie_here"
export PROMOTE_CSDN_COOKIE="your_cookie_here"
export PROMOTE_ZHIHU_COOKIE="your_cookie_here"
```

### Auto-Extraction (with OpenClaw)

```bash
# Using browser tool to auto-extract
promote auth set-cookie juejin "extracted_cookie"
promote auth set-cookie csdn "extracted_cookie"
promote auth set-cookie zhihu "extracted_cookie"

# Verify
promote auth status
promote platforms check
```

::: warning Cookie Expiry
Cookies expire approximately every 1 month. If posting fails with authentication errors, re-extract your cookies using the steps above.
:::
