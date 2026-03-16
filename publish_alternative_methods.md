# 掘金和CSDN自动发布替代方案

## 方案一：浏览器自动化（推荐）

使用Playwright或Selenium模拟浏览器操作，这是目前最可靠的方案。

### 安装依赖

```bash
pip install playwright
playwright install chromium
```

### 使用方法

```python
from publish_with_browser import publish_juejin_with_playwright, publish_csdn_with_playwright

# 发布到掘金
publish_juejin_with_playwright(
    title="文章标题",
    content="文章内容（支持Markdown）",
    tags=["Python", "后端"]
)

# 发布到CSDN
publish_csdn_with_playwright(
    title="文章标题",
    content="文章内容",
    tags=["Python", "自动化"]
)
```

### 连接到已运行的Chrome（更高效）

1. 先启动Chrome（带远程调试端口）：
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_dev"
```

2. 在Chrome中登录掘金和CSDN

3. 使用以下代码发布：
```python
from publish_with_browser import publish_with_existing_browser

publish_with_existing_browser("juejin", title, content, tags)
publish_with_existing_browser("csdn", title, content, tags)
```

---

## 方案二：使用DrissionPage（国产方案）

DrissionPage是一个更高效的浏览器自动化工具，对中文网站支持更好。

### 安装

```bash
pip install DrissionPage
```

### 示例代码

```python
from DrissionPage import ChromiumPage

def publish_juejin_drission(title, content, tags):
    page = ChromiumPage()
    page.get('https://juejin.cn/editor/drafts/new')

    # 填写标题
    page.ele('css:input[placeholder="输入文章标题..."]').input(title)

    # 填写内容
    page.ele('css:textarea').input(content)

    # 添加标签
    for tag in tags[:3]:
        tag_input = page.ele('css:input[placeholder="搜索标签"]')
        tag_input.input(tag)
        time.sleep(1)
        page.ele('css:.tag-suggestion-item').click()

    # 发布
    page.ele('css:button:contains("发布")').click()
    time.sleep(5)

    return page.url
```

---

## 方案三：使用已开源的工具

有一些开源项目已经实现了这些功能：

### 1. 多平台发布工具

| 项目 | 地址 | 说明 |
|------|------|------|
| blog-auto-publishing-tools | https://github.com/ddean2009/blog-auto-publishing-tools | 支持掘金、CSDN等多个平台 |
| easy-publish | https://github.com/ystcode/easy-publish | 简化的多平台发布工具 |
| artipub | https://github.com/crawlab-team/artipub | 文章发布平台，支持多平台 |

### 2. 安装 blog-auto-publishing-tools

```bash
git clone https://github.com/ddean2009/blog-auto-publishing-tools.git
cd blog-auto-publishing-tools
pip install -r requirements.txt
```

配置`config.yaml`：
```yaml
juejin:
  enabled: true
  cookie: "your_cookie_here"

csdn:
  enabled: true
  cookie: "your_cookie_here"
```

运行：
```bash
python main.py --file article.md
```

---

## 方案四：使用Claude Code + MCP

如果你使用Claude Code，可以配合浏览器MCP服务器实现自动化。

### 配置Playwright MCP

在Claude Code的settings.json中添加：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic/playwright-mcp@latest"]
    }
  }
}
```

然后可以直接让Claude帮你操作浏览器发布文章。

---

## 各方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| Playwright | 稳定、文档完善 | 需要安装浏览器 | ⭐⭐⭐⭐⭐ |
| DrissionPage | 对中文站支持好 | 相对小众 | ⭐⭐⭐⭐ |
| 开源工具 | 即用即走 | 可能过时 | ⭐⭐⭐ |
| Selenium | 老牌工具 | 较重、慢 | ⭐⭐⭐ |

---

## 当前项目建议

对于`promotion-agent`项目，建议：

1. **保留现有API方案**用于知乎和其他国际平台
2. **添加浏览器自动化方案**作为掘金和CSDN的备选
3. **提供清晰的错误提示**，引导用户使用合适的发布方式

### 快速测试

```bash
# 安装依赖
pip install playwright
playwright install chromium

# 运行测试
python publish_with_browser.py
```

第一次运行需要：
1. 浏览器会自动打开
2. 手动登录掘金/CSDN
3. 之后就可以自动发布了
