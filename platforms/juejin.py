"""掘金 (Juejin) platform via unofficial API.

Workflow: create draft → publish draft (minimal payload).
Authentication: Cookie-based (sessionid from browser).

Note: Playwright fallback removed in v4. If API publish fails,
returns the draft link for manual publishing.
"""

from __future__ import annotations

import logging
import re

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult

logger = logging.getLogger(__name__)


@register_platform
class JuejinPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "juejin"
    DISPLAY_NAME = "掘金"
    REQUIRED_CONFIG_KEYS = ["juejin_cookie"]

    BASE_URL = "https://api.juejin.cn/content_api/v1"

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

    CATEGORY_MAP = {
        "前端": "6809637767543259144",
        "后端": "6809637769959178254",
        "Android": "6809635626879549454",
        "iOS": "6809635626661445640",
    }

    def __init__(self, config):
        self.cookie = getattr(config, "juejin_cookie", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Cookie": self.cookie or "",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://juejin.cn",
            "Referer": "https://juejin.cn/",
            "X-Juejin-Src": "web",
        }

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def _select_tags(self, content: PromotionContent) -> list[str]:
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
            if any(k in text for k in ["frontend", "css", "html", "ui", "浏览器"]):
                selected.append(self.DEFAULT_TAGS["前端"])
            else:
                selected.append(self.DEFAULT_TAGS["后端"])

        return selected[:3]

    def _select_category(self, content: PromotionContent) -> str:
        if content.metadata.get("juejin_category_id"):
            return content.metadata["juejin_category_id"]

        text = (content.title + " " + content.body).lower()
        if any(k in text for k in ["frontend", "vue", "react", "css", "html", "javascript"]):
            return self.CATEGORY_MAP["前端"]
        return self.CATEGORY_MAP["后端"]

    @staticmethod
    def _markdown_to_html(md: str) -> str:
        html = md
        html = re.sub(
            r"```(\w*)\n(.*?)```",
            r'<pre><code class="language-\1">\2</code></pre>',
            html,
            flags=re.DOTALL,
        )
        html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
        html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"^> (.+)$", r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)
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

    async def _create_draft(self, adapted: dict) -> tuple[str | None, str | None]:
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
        resp = await self.client.post(
            f"{self.BASE_URL}/article_draft/create",
            json=payload,
        )
        data = resp.json()
        if data.get("err_no") == 0:
            return data["data"]["id"], None
        return None, data.get("err_msg", "Draft creation failed")

    async def _publish_draft(self, draft_id: str) -> dict:
        payload = {
            "draft_id": draft_id,
            "sync_to_org": False,
            "column_ids": [],
            "theme_ids": [],
        }
        resp = await self.client.post(
            f"{self.BASE_URL}/article/publish",
            json=payload,
        )
        return resp.json()

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            draft_id, draft_err = await self._create_draft(adapted)
            if not draft_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Draft creation failed: {draft_err}",
                )

            publish_data = await self._publish_draft(draft_id)
            if publish_data.get("err_no") == 0:
                article_id = publish_data["data"].get("article_id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://juejin.cn/post/{article_id}",
                    post_id=str(article_id),
                )

            api_error = publish_data.get("err_msg", "Publish failed")
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                post_id=draft_id,
                error=f"{api_error}。草稿已创建，请手动发布: https://juejin.cn/editor/drafts/{draft_id}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    async def health_check(self) -> bool:
        try:
            resp = await self.client.post(
                "https://api.juejin.cn/recommend_api/v1/article/recommend_all_feed",
                json={"sort_type": 200, "cursor": "0", "limit": 1},
            )
            return resp.is_success
        except Exception:
            return False
