"""
掘金 (Juejin) 平台 - 新版API实现

基于GitHub开源代码分析，使用更新的API参数格式
"""

from __future__ import annotations

from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


@register_platform
class JuejinPlatformNew(BasePlatform):
    """
    掘金平台 - 使用新版API参数

    参考开源项目实现的最新API格式
    """
    PLATFORM_NAME = "juejin_new"
    DISPLAY_NAME = "掘金(新版API)"
    REQUIRED_CONFIG_KEYS = ["juejin_cookie"]

    BASE_URL = "https://api.juejin.cn/content_api/v1"

    # 常用标签ID映射
    TAG_MAP = {
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

    def _select_tags(self, content: PromotionContent) -> list:
        """智能选择标签"""
        # 如果用户提供了标签ID，直接使用
        if content.metadata.get("juejin_tag_ids"):
            return content.metadata["juejin_tag_ids"]

        # 根据关键词选择标签
        title_lower = content.title.lower()
        body_lower = content.body.lower()
        text = title_lower + " " + body_lower

        selected_tags = []

        if any(k in text for k in ["vue", "vue.js"]):
            selected_tags.append(self.TAG_MAP["Vue"])
        if any(k in text for k in ["react"]):
            selected_tags.append(self.TAG_MAP["React"])
        if any(k in text for k in ["javascript", "js", "es6"]):
            selected_tags.append(self.TAG_MAP["JavaScript"])
        if any(k in text for k in ["python", "django", "flask"]):
            selected_tags.append(self.TAG_MAP["Python"])
        if any(k in text for k in ["java", "spring"]):
            selected_tags.append(self.TAG_MAP["Java"])
        if any(k in text for k in ["github", "开源", "open source"]):
            selected_tags.append(self.TAG_MAP["GitHub"])
        if any(k in text for k in ["工具", "自动化", "效率"]):
            selected_tags.append(self.TAG_MAP["工具"])

        # 根据内容类型选择主要分类标签
        if any(k in text for k in ["frontend", "css", "html", "ui", "浏览器"]):
            if self.TAG_MAP["前端"] not in selected_tags:
                selected_tags.append(self.TAG_MAP["前端"])
        else:
            if self.TAG_MAP["后端"] not in selected_tags:
                selected_tags.append(self.TAG_MAP["后端"])

        return selected_tags[:3]  # 最多3个标签

    def _select_category(self, content: PromotionContent) -> str:
        """选择分类"""
        if content.metadata.get("juejin_category_id"):
            return content.metadata["juejin_category_id"]

        text = (content.title + " " + content.body).lower()

        if any(k in text for k in ["frontend", "vue", "react", "css", "html", "ui", "javascript"]):
            return self.CATEGORY_MAP["前端"]

        return self.CATEGORY_MAP["后端"]  # 默认后端

    def adapt_content(self, content: PromotionContent) -> dict:
        """转换为掘金API格式"""
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: {content.url}"

        # 生成摘要
        brief = content.description or content.title
        if len(brief) > 100:
            brief = brief[:97] + "..."

        # 转换为HTML（简单转换）
        html_content = self._markdown_to_html(body)

        return {
            "title": content.title,
            "brief_content": brief,
            "mark_content": body,
            "html_content": html_content,
            "category_id": self._select_category(content),
            "tag_ids": self._select_tags(content),
            "edit_type": 14,  # Markdown编辑器
            "cover_image": content.metadata.get("juejin_cover_image", ""),
            "original": 1,  # 原创
        }

    def _markdown_to_html(self, markdown: str) -> str:
        """简单Markdown转HTML"""
        html = markdown

        # 标题
        html = html.replace("# ", "<h1>").replace("\n#", "</h1>\n<h1>")
        html = html.replace("## ", "<h2>").replace("\n##", "</h2>\n<h2>")
        html = html.replace("### ", "<h3>").replace("\n###", "</h3>\n<h3>")

        # 代码块
        import re
        html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)

        # 段落
        paragraphs = html.split('\n\n')
        html = ''.join([f'<p>{p}</p>' for p in paragraphs if p and not p.startswith('<')])

        return html

    def _create_draft(self, adapted: dict) -> Optional[str]:
        """创建草稿"""
        payload = {
            "title": adapted["title"],
            "brief_content": adapted["brief_content"],
            "mark_content": adapted["mark_content"],
            "html_content": adapted["html_content"],
            "category_id": adapted["category_id"],
            "tag_ids": adapted["tag_ids"],
            "edit_type": adapted["edit_type"],
            "cover_image": adapted["cover_image"],
        }

        resp = self.client.post(
            f"{self.BASE_URL}/article_draft/create",
            json=payload
        )

        data = resp.json()
        if data.get("err_no") == 0:
            return data["data"]["id"]
        return None

    def _publish(self, adapted: dict) -> dict:
        """
        直接发布文章（不经过草稿）
        某些API版本支持直接发布
        """
        payload = {
            "title": adapted["title"],
            "brief_content": adapted["brief_content"],
            "mark_content": adapted["mark_content"],
            "html_content": adapted["html_content"],
            "category_id": adapted["category_id"],
            "tag_ids": adapted["tag_ids"],
            "edit_type": adapted["edit_type"],
            "cover_image": adapted["cover_image"],
            "original": adapted["original"],
            "original_url": "",
            "link_url": "",
        }

        resp = self.client.post(
            f"{self.BASE_URL}/article/publish",
            json=payload
        )

        return resp.json()

    def post(self, content: PromotionContent) -> PostResult:
        """发布文章"""
        try:
            adapted = self.adapt_content(content)

            # 方法1: 尝试直接发布
            print("尝试直接发布...")
            result = self._publish(adapted)

            if result.get("err_no") == 0:
                article_id = result["data"].get("article_id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://juejin.cn/post/{article_id}",
                    post_id=str(article_id),
                )

            # 方法2: 创建草稿后发布
            print("直接发布失败，尝试草稿模式...")
            draft_id = self._create_draft(adapted)

            if not draft_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="创建草稿失败",
                )

            # 发布草稿
            resp = self.client.post(
                f"{self.BASE_URL}/article/publish",
                json={"draft_id": draft_id}
            )

            data = resp.json()
            if data.get("err_no") == 0:
                article_id = data["data"].get("article_id", "")
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=f"https://juejin.cn/post/{article_id}",
                    post_id=str(article_id),
                )

            # 如果都失败了，返回草稿ID
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"{data.get('err_msg', '发布失败')}。草稿ID: {draft_id}，请手动发布",
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
