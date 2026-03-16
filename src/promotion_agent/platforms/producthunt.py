"""Product Hunt platform via GraphQL v2 API.

Authentication: OAuth 2.0 Bearer token (obtain from developer portal).
API: POST https://api.producthunt.com/v2/api/graphql
"""

from __future__ import annotations

from typing import Optional

import httpx

from promotion_agent.core.base_platform import BasePlatform
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import register_platform
from promotion_agent.core.result import PostResult


@register_platform
class ProductHuntPlatform(BasePlatform):
    PLATFORM_NAME = "producthunt"
    DISPLAY_NAME = "Product Hunt"
    REQUIRED_CONFIG_KEYS = ["producthunt_token"]

    API_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(self, config):
        self.token = getattr(config, "producthunt_token", None)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={
                    "Authorization": f"Bearer {self.token or ''}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30.0,
                trust_env=False,  # 禁用系统代理避免SSL问题
            )
        return self._client

    def validate_config(self) -> bool:
        return bool(self.token)

    def adapt_content(self, content: PromotionContent) -> dict:
        """Build GraphQL mutation variables.

        Product Hunt createPost requires:
        - name: product name
        - tagline: short description (max 60 chars)
        - url: link to product
        """
        tagline = content.description or content.title
        if len(tagline) > 60:
            tagline = tagline[:57] + "..."

        return {
            "name": content.title,
            "tagline": tagline,
            "url": content.url or "",
            "description": content.body[:260] if content.body else "",
        }

    def post(self, content: PromotionContent) -> PostResult:
        try:
            adapted = self.adapt_content(content)

            mutation = """
            mutation CreatePost($input: CreatePostInput!) {
                createPost(input: $input) {
                    post {
                        id
                        slug
                        url
                    }
                    errors {
                        field
                        message
                    }
                }
            }
            """

            variables = {
                "input": {
                    "name": adapted["name"],
                    "tagline": adapted["tagline"],
                    "url": adapted["url"],
                }
            }

            if adapted.get("description"):
                variables["input"]["description"] = adapted["description"]

            response = self.client.post(
                self.API_URL,
                json={"query": mutation, "variables": variables},
            )

            if response.is_success:
                data = response.json()
                post_data = data.get("data", {}).get("createPost", {})
                errors = post_data.get("errors")

                if errors:
                    error_msgs = "; ".join(
                        f"{e['field']}: {e['message']}" for e in errors
                    )
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=False,
                        error=f"GraphQL errors: {error_msgs}",
                    )

                post = post_data.get("post", {})
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=post.get("url", ""),
                    post_id=str(post.get("id", "")),
                )

            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=f"HTTP {response.status_code}: {response.text}",
            )
        except Exception as e:
            return PostResult(
                platform=self.PLATFORM_NAME,
                success=False,
                error=str(e),
            )

    def health_check(self) -> bool:
        try:
            query = "{ viewer { user { id } } }"
            resp = self.client.post(self.API_URL, json={"query": query})
            if resp.is_success:
                data = resp.json()
                return data.get("data", {}).get("viewer") is not None
            return False
        except Exception:
            return False
