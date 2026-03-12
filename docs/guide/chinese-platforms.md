# Chinese Platforms

Publish to Juejin (掘金), CSDN, Zhihu (知乎), and CNBlogs (博客园) using **blog-auto-publishing-tools**.

## Recommended Tool

| Tool | Platforms | Auth Method |
|------|----------|-------------|
| [blog-auto-publishing-tools](https://github.com/ddean2009/blog-auto-publishing-tools) | Juejin, CSDN, Zhihu, CNBlogs, SegmentFault, InfoQ, 51CTO, Toutiao | Browser cookies |

## Setup

### 1. Install

```bash
git clone https://github.com/ddean2009/blog-auto-publishing-tools.git
cd blog-auto-publishing-tools
pip install -r requirements.txt
```

### 2. Configure Cookies

Each Chinese platform uses cookie-based authentication. You need to extract cookies from your browser:

1. Log in to the platform in your browser
2. Open DevTools (F12) → Application → Cookies
3. Copy the full cookie string
4. Add to the tool's configuration file

::: tip Cookie Expiry
Cookies typically expire after ~1 month. If publishing fails with auth errors, re-extract your cookies.
:::

### 3. Publish

```bash
# Publish to all configured platforms
python publish.py --file article.md

# Publish to specific platforms
python publish.py --platform juejin,csdn --file article.md
```

## Platform Details

### Juejin (掘金)

- **URL**: https://juejin.cn
- **Audience**: Chinese developers, tech community
- **Content**: Technical articles, tutorials, project showcases
- **Auth**: Cookie-based (expires ~1 month)
- **Tips**: Set `category_id` for correct channel placement

### CSDN

- **URL**: https://www.csdn.net
- **Audience**: Largest Chinese developer community
- **Content**: Technical blogs, tutorials
- **Auth**: Cookie-based (expires ~1 month)
- **Tips**: Good SEO, content ranks well in Chinese search engines

### Zhihu (知乎)

- **URL**: https://www.zhihu.com
- **Audience**: Knowledge sharing community (Q&A + articles)
- **Content**: In-depth technical content, published to 专栏 (columns)
- **Auth**: Cookie-based (expires ~1 month)
- **Tips**: Best for deep technical content and thought leadership

### CNBlogs (博客园)

- **URL**: https://www.cnblogs.com
- **Audience**: Traditional Chinese developer community
- **Content**: Technical blogs, tutorials
- **Auth**: MetaWeblog API (token-based, long-lived)
- **Tips**: Most stable API among Chinese platforms
