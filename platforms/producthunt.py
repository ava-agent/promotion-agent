"""Product Hunt platform via GraphQL v2 API.

Authentication: OAuth 2.0 Bearer token (obtain from developer portal).
API: POST https://api.producthunt.com/v2/api/graphql
"""

from __future__ import annotations

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class ProductHuntPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "producthunt"
    DISPLAY_NAME = "Product Hunt"
    REQUIRED_CONFIG_KEYS = ["producthunt_token"]

    API_URL = "https://api.producthunt.com/v2/api/graphql"

    def __init__(self, config):
        self.token = getattr(config, "producthunt_token", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token or ''}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def validate_config(self) -> bool:
        return bool(self.token)

    def adapt_content(self, content: PromotionContent) -> dict:
        tagline = content.description or content.title
        if len(tagline) > 60:
            tagline = tagline[:57] + "..."
        return {
            "name": content.title,
            "tagline": tagline,
            "url": content.url or "",
            "description": content.body[:260] if content.body else "",
        }

    async def post(self, content: PromotionContent) -> PostResult:
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

            response = await self.client.post(
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

    async def health_check(self) -> bool:
        try:
            query = "{ viewer { user { id } } }"
            resp = await self.client.post(self.API_URL, json={"query": query})
            if resp.is_success:
                data = resp.json()
                return data.get("data", {}).get("viewer") is not None
            return False
        except Exception:
            return False
