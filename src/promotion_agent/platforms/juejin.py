"""掘金 (Juejin) platform via unofficial API.

Workflow: create draft -> publish draft (minimal payload).
Authentication: Cookie-based (sessionid from browser).

Fallback: Playwright browser automation if API publish fails.
"""

from __future__ import annotations

import logging
import re
from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult

logger = logging.getLogger(__name__)


@register_platform
class JuejinPlatform(BasePlatform):
    PLATFORM_NAME = "juejin"
    DISPLAY_NAME = "掘金"
    REQUIRED_CONFIG_KEYS = ["juejin_cookie"]

    BASE_URL = "https://api.juejin.cn/content_api/v1"

    # 常用标签ID
    DEFAULT_TAGS = {
        "前端": "6809640407484334093",
        "后端": "6809640404791590916",
        "JavaScript": "6809640350671196174",
        "Python": "6809640354435051533",
        "Java": "6809640354183632910",
        "GitHub": "6809640362321514247",
        "开源": "6809640364677267469",
        "工具": "6809640371035672583",
        "Vue": "6809640369764958215",
        "React": "6809640355264112654",
    }

    # 分类ID
    CATEGORY_MAP = {
        "前端": "6809637767543259144",
        "后端": "6809637769959178254",
        "Android": "6809635626879549454",
        "iOS": "6809635626661445640",
    }

    def __init__(self, config):
        self.cookie = getattr(config, "juejin_cookie", None)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Content-Type": "application/json",
                    "Cookie": self.cookie or "",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36",
                    "Origin": "https://juejin.cn",
                    "Referer": "https://juejin.cn/",
                    "X-Juejin-Src": "web",
                },
                timeout=30.0,
                trust_env=False,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def _select_tags(self, content: PromotionContent) -> list[str]:
        """Smart tag selection based on content keywords."""
        tag_ids = content.metadata.get("juejin_tag_ids", [])
        if tag_ids:
            return tag_ids

        text = (content.title + " " + content.body).lower()
        selected = []

        tag_keywords = {
            "Python": ["python", "django", "flask", "fastapi"],
            "JavaScript": ["javascript", "js", "es6", "typescript", "ts"],
            "Vue": ["vue", "vue.js", "nuxt"],
            "React": ["react", "next.js", "nextjs"],
            "Java": ["java", "spring", "springboot"],
            "GitHub": ["github", "开源", "open source", "git"],
            "工具": ["工具", "自动化", "效率", "tool", "automation"],
        }

        for tag_name, keywords in tag_keywords.items():
            if any(k in text for k in keywords):
                selected.append(self.DEFAULT_TAGS[tag_name])

        if not selected:
            # 根据内容类型选择前端或后端
            if any(k in text for k in ["frontend", "css", "html", "ui", "浏览器"]):
                selected.append(self.DEFAULT_TAGS["前端"])
            else:
                selected.append(self.DEFAULT_TAGS["后端"])

        return selected[:3]

    def _select_category(self, content: PromotionContent) -> str:
        """Smart category selection."""
        if content.metadata.get("juejin_category_id"):
            return content.metadata["juejin_category_id"]

        text = (content.title + " " + content.body).lower()
        if any(k in text for k in ["frontend", "vue", "react", "css", "html", "javascript"]):
            return self.CATEGORY_MAP["前端"]
        return self.CATEGORY_MAP["后端"]

    @staticmethod
    def _markdown_to_html(md: str) -> str:
        """Basic Markdown-to-HTML for Juejin's html_content field."""
        html = md
        # Code blocks first (before other transformations)
        html = re.sub(
            r"```(\w*)\n(.*?)```",
            r'<pre><code class="language-\1">\2</code></pre>',
            html,
            flags=re.DOTALL,
        )
        # Inline code
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
        # Headers (h3 before h2 before h1 to avoid conflicts)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        # Bold / italic
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        # Links
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
        # List items
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        # Blockquotes
        html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)
        # Paragraphs (double newlines)
        paragraphs = html.split("\n\n")
        processed = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith("<"):
                p = f"<p>{p}</p>"
            processed.append(p)
        return "\n".join(processed)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: {content.url}"

        brief = (content.description or content.title)[:100]
        html_content = self._markdown_to_html(body)

        return {
            "title": content.title,
            "mark_content": body,
            "html_content": html_content,
            "brief_content": brief,
            "category_id": self._select_category(content),
            "tag_ids": self._select_tags(content),
            "cover_image": content.metadata.get("juejin_cover_image", ""),
            "edit_type": 10,
        }

    def _create_draft(self, adapted: dict) -> tuple[Optional[str], Optional[str]]:
        """Create draft with full content. Returns (draft_id, error_msg)."""
        payload = {
            "title": adapted["title"],
            "mark_content": adapted["mark_content"],
            "html_content": adapted["html_content"],
            "brief_content": adapted["brief_content"],
            "category_id": adapted["category_id"],
            "tag_ids": adapted["tag_ids"],
            "cover_image": adapted["cover_image"],
            "edit_type": adapted["edit_type"],
        }
        resp = self.client.post(
            f"{self.BASE_URL}/article_draft/create",
            json=payload,
        )
        data = resp.json()
        if data.get("err_no") == 0:
            return data["data"]["id"], None
        return None, data.get("err_msg", "Draft creation failed")

    def _publish_draft(self, draft_id: str) -> dict:
        """Publish an existing draft. Minimal payload — content is already in draft."""
        payload = {
            "draft_id": draft_id,
            "sync_to_org": False,
            "column_ids": [],
            "theme_ids": [],
        }
        resp = self.client.post(
            f"{self.BASE_URL}/article/publish",
            json=payload,
        )
        return resp.json()

    def _publish_via_playwright(self, adapted: dict) -> PostResult:
        """Fallback: publish via Playwright browser automation."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error="Playwright未安装。运行: pip install playwright && playwright install chromium",
            )

        import time

        with sync_playwright() as p:
            try:
                # 尝试连接已运行的Chrome (复用登录态)
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                context = browser.contexts[0] if browser.contexts else browser.new_context()
            except Exception:
                # 启动新浏览器 (需要手动登录)
                browser = p.chromium.launch(
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                context = browser.new_context(viewport={"width": 1280, "height": 800})

            page = context.new_page()
            try:
                page.goto("https://juejin.cn/editor/drafts/new", wait_until="networkidle")
                page.wait_for_timeout(2000)

                # 填写标题
                title_input = page.locator('input[placeholder*="标题"]').first
                title_input.fill(adapted["title"])

                # 填写Markdown内容
                editor = page.locator(".bytemd-body textarea, textarea.CodeMirror-code, textarea").first
                editor.fill(adapted["mark_content"])
                page.wait_for_timeout(1000)

                # 点击发布按钮
                publish_btn = page.locator('button:has-text("发布")').first
                publish_btn.click()
                page.wait_for_timeout(2000)

                # 确认发布 (弹窗中的确认按钮)
                confirm_btn = page.locator('button:has-text("确定并发布"), button:has-text("确认发布")').first
                if confirm_btn.is_visible():
                    confirm_btn.click()

                page.wait_for_timeout(5000)

                url = page.url
                if "/post/" in url:
                    post_id = url.split("/post/")[-1].split("?")[0]
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=True,
                        url=url,
                        post_id=post_id,
                    )
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Playwright发布后URL异常: {url}",
                )
            except Exception as e:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Playwright发布失败: {e}",
                )
            finally:
                page.close()

    def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            # Step 1: Create draft (includes all content)
            draft_id, draft_err = self._create_draft(adapted)
            if not draft_id:
                logger.warning("Juejin draft creation failed: %s", draft_err)
                # 草稿创建失败，尝试Playwright
                logger.info("Falling back to Playwright...")
                return self._publish_via_playwright(adapted)

            # Step 2: Publish draft (minimal payload)
            publish_data = self._publish_draft(draft_id)
            if publish_data.get("err_no") == 0:
                article_id = publish_data["data"].get("article_id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://juejin.cn/post/{article_id}",
                    post_id=str(article_id),
                )

            # API publish failed — try Playwright fallback
            api_error = publish_data.get("err_msg", "Publish failed")
            logger.warning("Juejin API publish failed: %s. Trying Playwright...", api_error)

            pw_result = self._publish_via_playwright(adapted)
            if pw_result.success:
                return pw_result

            # Both failed — return draft ID for manual publishing
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"API: {api_error}; Playwright: {pw_result.error}。草稿已创建(ID: {draft_id})，请手动发布: https://juejin.cn/editor/drafts/{draft_id}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            resp = self.client.post(
                "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed",
                json={"sort_type": 200, "cursor": "0", "limit": 1},
            )
            return resp.is_success
        except Exception:
            return False
