"""CSDN platform via unofficial saveArticle API.

Authentication: Cookie-based (from browser login session).
CSDN has WAF protection on blog-console-api.csdn.net — if the API returns 403,
we fall back to Playwright browser automation.
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
class CSDNPlatform(BasePlatform):
    PLATFORM_NAME = "csdn"
    DISPLAY_NAME = "CSDN"
    REQUIRED_CONFIG_KEYS = ["csdn_cookie"]

    API_URL = "https://blog-console-api.csdn.net/v3/mdeditor/saveArticle"

    def __init__(self, config):
        self.cookie = getattr(config, "csdn_cookie", None)
        self._client: Optional[httpx.Client] = None

    def _extract_csrf_token(self) -> Optional[str]:
        """Extract x-csrf-token from cookie string if present."""
        if not self.cookie:
            return None
        for part in self.cookie.split(";"):
            part = part.strip()
            if part.lower().startswith("csrf_token=") or part.lower().startswith("x-csrf-token="):
                return part.split("=", 1)[1]
        # Also try extracting from a meta tag via a quick page fetch
        return None

    def _extract_username(self) -> Optional[str]:
        """Extract username from cookie for URL construction."""
        if not self.cookie:
            return None
        for part in self.cookie.split(";"):
            part = part.strip()
            if part.startswith("UserName="):
                return part.split("=", 1)[1]
        return None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            headers = {
                "Content-Type": "application/json",
                "Cookie": self.cookie or "",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36",
                "Origin": "https://editor.csdn.net",
                "Referer": "https://editor.csdn.net/md/",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "X-Requested-With": "XMLHttpRequest",
            }
            # Add CSRF token if available
            csrf = self._extract_csrf_token()
            if csrf:
                headers["x-csrf-token"] = csrf

            self._client = httpx.Client(
                headers=headers,
                timeout=30.0,
                trust_env=False,
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.cookie)

    def adapt_content(self, content: PromotionContent) -> dict:
        body = content.body
        if content.url:
            body += f"\n\n> 项目地址: [{content.url}]({content.url})"

        tags = ",".join(content.tags) if content.tags else ""

        return {
            "title": content.title,
            "markdowncontent": body,
            "content": body,
            "tags": tags,
            "categories": content.metadata.get("csdn_categories", ""),
            "type": content.metadata.get("csdn_type", "original"),
            "status": 0,  # 0=publish, 2=draft
            "readType": "public",
            "Description": (content.description or content.title)[:200],
            "source": "pc_mdeditor",
            "not_auto_saved": "1",
            "authorized_status": False,
            "articleedittype": "1",
        }

    def _post_via_api(self, payload: dict) -> PostResult:
        """Try publishing via the CSDN API."""
        response = self.client.post(self.API_URL, json=payload)

        if response.status_code in (401, 403):
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"CSDN API WAF拦截 (HTTP {response.status_code})",
            )

        if response.is_success:
            data = response.json()
            article_id = data.get("data", {}).get("id") or data.get("id")
            if article_id:
                username = self._extract_username() or ""
                url = data.get("data", {}).get("url", "")
                if not url and username:
                    url = f"https://blog.csdn.net/{username}/article/details/{article_id}"
                elif not url:
                    url = f"https://blog.csdn.net/article/details/{article_id}"
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=url,
                    post_id=str(article_id),
                )
            if data.get("code") == 200 or data.get("msg") == "success":
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=data.get("data", {}).get("url", ""),
                    post_id=str(data.get("data", {}).get("id", "")),
                )
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"Unexpected response: {data}",
            )

        return PostResult(
            platform=self.PLATFORM_NAME,
            success=False,
            error=f"HTTP {response.status_code}: {response.text[:200]}",
        )

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

        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp("http://localhost:9222")
                context = browser.contexts[0] if browser.contexts else browser.new_context()
            except Exception:
                browser = p.chromium.launch(
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                )
                context = browser.new_context(viewport={"width": 1280, "height": 800})

            page = context.new_page()
            try:
                page.goto("https://editor.csdn.net/md/", wait_until="networkidle")
                page.wait_for_timeout(3000)

                # 填写标题
                title_input = page.locator('input[placeholder*="标题"]').first
                title_input.fill(adapted["title"])
                page.wait_for_timeout(500)

                # 填写Markdown内容 (CSDN uses CodeMirror)
                # 尝试多种编辑器选择器
                editor_filled = False
                for selector in [
                    ".editor__inner .CodeMirror textarea",
                    ".CodeMirror textarea",
                    "textarea.CodeMirror-code",
                    ".editor textarea",
                ]:
                    try:
                        editor = page.locator(selector).first
                        if editor.is_visible():
                            editor.fill(adapted["markdowncontent"])
                            editor_filled = True
                            break
                    except Exception:
                        continue

                if not editor_filled:
                    # 使用keyboard直接输入
                    page.locator(".CodeMirror").first.click()
                    page.keyboard.insert_text(adapted["markdowncontent"])

                page.wait_for_timeout(1000)

                # 点击发布按钮
                publish_btn = page.locator('button:has-text("发布文章"), button:has-text("发布")').first
                publish_btn.click()
                page.wait_for_timeout(5000)

                url = page.url
                if "article/details" in url:
                    post_id = url.split("article/details/")[-1].split("?")[0]
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
            payload = self.adapt_content(content)
            if content.metadata.get("csdn_draft", False):
                payload["status"] = 2

            # Step 1: Try API
            result = self._post_via_api(payload)
            if result.success:
                return result

            # Step 2: If API failed (likely WAF 403), try Playwright
            api_error = result.error
            logger.warning("CSDN API failed: %s. Trying Playwright...", api_error)
            pw_result = self._publish_via_playwright(payload)
            if pw_result.success:
                return pw_result

            # Both failed
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"API: {api_error}; Playwright: {pw_result.error}",
            )
        except httpx.NetworkError as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"网络错误: {e}。如果您使用了代理，请检查代理设置。",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            resp = self.client.get(
                "https://blog-console-api.csdn.net/v1/user/info",
            )
            return resp.is_success
        except Exception:
            return False
