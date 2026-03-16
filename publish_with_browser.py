#!/usr/bin/env python3
"""
使用浏览器自动化发布到掘金和CSDN
这是目前最可靠的方案，因为平台加强了API安全验证
"""

import os
import sys
import time
from typing import Optional

def publish_juejin_with_playwright(title: str, content: str, tags: list = None):
    """
    使用Playwright自动发布到掘金

    需要安装:
    pip install playwright
    playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("请先安装Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

    tags = tags or ["后端"]

    with sync_playwright() as p:
        # 启动浏览器（使用已登录的Chrome）
        browser = p.chromium.launch(
            headless=False,  # 设置为True可以无头运行
            args=['--disable-blink-features=AutomationControlled']
        )

        # 尝试使用已有的Cookie
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )

        page = context.new_page()

        try:
            # 1. 访问掘金编辑器
            print("📝 打开掘金编辑器...")
            page.goto("https://juejin.cn/editor/drafts/new")
            time.sleep(3)

            # 2. 填写标题
            print("📝 填写标题...")
            title_input = page.locator('input[placeholder="输入文章标题..."]').first
            title_input.fill(title)
            time.sleep(1)

            # 3. 填写内容（使用Markdown编辑器）
            print("📝 填写内容...")
            # 切换到Markdown编辑器（如果需要）
            markdown_btn = page.locator('text=Markdown').first
            if markdown_btn.is_visible():
                markdown_btn.click()
                time.sleep(1)

            # 填写内容
            editor = page.locator('textarea').first
            editor.fill(content)
            time.sleep(1)

            # 4. 添加标签
            print("🏷️ 添加标签...")
            tag_input = page.locator('input[placeholder="搜索标签"]').first
            for tag in tags[:3]:  # 最多3个标签
                tag_input.fill(tag)
                time.sleep(1)
                # 选择第一个建议
                suggestion = page.locator('.tag-suggestion-item').first
                if suggestion.is_visible():
                    suggestion.click()
                time.sleep(0.5)

            # 5. 发布文章
            print("🚀 准备发布...")
            publish_btn = page.locator('button:has-text("发布")').first
            publish_btn.click()
            time.sleep(2)

            # 确认发布
            confirm_btn = page.locator('button:has-text("确认发布")').first
            if confirm_btn.is_visible():
                confirm_btn.click()

            # 等待发布完成
            time.sleep(5)

            # 获取文章URL
            current_url = page.url
            if "/post/" in current_url:
                print(f"✅ 发布成功! URL: {current_url}")
                return True
            else:
                print(f"⚠️ 请检查发布状态，当前URL: {current_url}")
                return False

        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False
        finally:
            browser.close()


def publish_csdn_with_playwright(title: str, content: str, tags: list = None):
    """
    使用Playwright自动发布到CSDN
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("请先安装Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False

    tags = tags or ["Python"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()

        try:
            # 1. 访问CSDN编辑器
            print("📝 打开CSDN编辑器...")
            page.goto("https://editor.csdn.net/md/")
            time.sleep(5)

            # 2. 填写标题
            print("📝 填写标题...")
            title_input = page.locator('input[placeholder="输入文章标题"]').first
            title_input.fill(title)
            time.sleep(1)

            # 3. 填写内容
            print("📝 填写内容...")
            # CSDN使用CodeMirror编辑器
            editor = page.locator('.CodeMirror textarea').first
            editor.fill(content)
            time.sleep(1)

            # 4. 添加标签
            print("🏷️ 添加标签...")
            tag_input = page.locator('input[placeholder="添加文章标签"]').first
            for tag in tags[:5]:
                tag_input.fill(tag)
                time.sleep(1)
                # 按回车确认
                tag_input.press('Enter')
                time.sleep(0.5)

            # 5. 发布文章
            print("🚀 发布文章...")
            publish_btn = page.locator('button:has-text("发布文章")').first
            publish_btn.click()
            time.sleep(5)

            # 获取文章URL
            current_url = page.url
            if "article/details" in current_url:
                print(f"✅ 发布成功! URL: {current_url}")
                return True
            else:
                print(f"⚠️ 请检查发布状态，当前URL: {current_url}")
                return False

        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False
        finally:
            browser.close()


def publish_with_existing_browser(platform: str, title: str, content: str, tags: list = None):
    """
    连接到已运行的Chrome浏览器进行发布
    这样可以复用已登录的会话

    使用方式:
    1. 先启动Chrome（使用远程调试端口）:
       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
    2. 然后运行此函数
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("请先安装Playwright: pip install playwright")
        return False

    with sync_playwright() as p:
        try:
            # 连接到已运行的Chrome
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()

            if platform == "juejin":
                # 掘金发布流程
                page.goto("https://juejin.cn/editor/drafts/new")
                time.sleep(3)

                page.locator('input[placeholder="输入文章标题..."]').fill(title)
                page.locator('textarea').fill(content)

                # 添加标签
                if tags:
                    tag_input = page.locator('input[placeholder="搜索标签"]').first
                    for tag in tags[:3]:
                        tag_input.fill(tag)
                        time.sleep(1)
                        page.locator('.tag-suggestion-item').first.click()

                page.locator('button:has-text("发布")').click()
                time.sleep(5)

            elif platform == "csdn":
                # CSDN发布流程
                page.goto("https://editor.csdn.net/md/")
                time.sleep(5)

                page.locator('input[placeholder="输入文章标题"]').fill(title)
                page.locator('.CodeMirror textarea').fill(content)

                if tags:
                    tag_input = page.locator('input[placeholder="添加文章标签"]').first
                    for tag in tags[:5]:
                        tag_input.fill(tag)
                        tag_input.press('Enter')

                page.locator('button:has-text("发布文章")').click()
                time.sleep(5)

            current_url = page.url
            print(f"✅ 发布完成! URL: {current_url}")
            return True

        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False


if __name__ == "__main__":
    # 示例用法
    title = "测试文章：浏览器自动化发布"
    content = """# 测试文章

这是一篇通过浏览器自动化发布的测试文章。

## 内容说明

- 使用Playwright模拟浏览器操作
- 自动填写标题、内容、标签
- 自动点击发布按钮

## 代码示例

```python
print("Hello, World!")
```

感谢阅读！
"""
    tags = ["Python", "自动化", "测试"]

    print("="*60)
    print("浏览器自动化发布测试")
    print("="*60)

    # 测试掘金
    print("\n【掘金】")
    # publish_juejin_with_playwright(title, content, tags)

    # 测试CSDN
    print("\n【CSDN】")
    # publish_csdn_with_playwright(title, content, tags)

    print("\n" + "="*60)
    print("使用说明:")
    print("="*60)
    print("1. 确保已安装Playwright: pip install playwright")
    print("2. 安装浏览器: playwright install chromium")
    print("3. 取消注释上面的函数调用进行测试")
    print("4. 首次运行需要在浏览器中登录对应平台")
    print("\n或者使用已运行的Chrome:")
    print("  1. 启动Chrome: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222")
    print("  2. 在Chrome中登录掘金/CSDN")
    print("  3. 调用 publish_with_existing_browser()")
