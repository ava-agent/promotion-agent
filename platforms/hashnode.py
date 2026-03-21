"""Hashnode platform via GraphQL API.

Authentication: Personal Access Token (header).
API: POST https://gql.hashnode.com
"""

from __future__ import annotations

from typing import Optional

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class HashnodePlatform(BaseHttpPlatform):
    PLATFORM_NAME = "hashnode"
    DISPLAY_NAME = "Hashnode"
    REQUIRED_CONFIG_KEYS = ["hashnode_token"]

    API_URL = "https://gql.hashnode.com"

    def __init__(self, config):
        self.token = getattr(config, "hashnode_token", None)
        self.publication_id = getattr(config, "hashnode_publication_id", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": self.token or "",
            "Content-Type": "application/json",
        }

    def validate_config(self) -> bool:
        return bool(self.token)

    async def _get_publication_id(self) -> Optional[str]:
        if self.publication_id:
            return self.publication_id
        query = """
        query {
            me {
                publications(first: 1) {
                    edges { node { id } }
                }
            }
        }
        """
        resp = await self.client.post(self.API_URL, json={"query": query})
        if resp.is_success:
            edges = (
                resp.json()
                .get("data", {})
                .get("me", {})
                .get("publications", {})
                .get("edges", [])
            )
            if edges:
                return edges[0]["node"]["id"]
        return None

    def adapt_content(self, content: PromotionContent) -> dict:
        tags = [{"slug": t.lower().replace(" ", "-"), "name": t} for t in content.tags[:5]]
        return {
            "title": content.title,
            "contentMarkdown": content.body,
            "tags": tags,
            "originalArticleURL": content.url or "",
        }

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            pub_id = await self._get_publication_id()
            if not pub_id:
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error="No publication found. Set PROMOTE_HASHNODE_PUBLICATION_ID.",
                )

            adapted = self.adapt_content(content)

            mutation = """
            mutation PublishPost($input: PublishPostInput!) {
                publishPost(input: $input) {
                    post {
                        id
                        slug
                        url
                    }
                }
            }
            """

            variables = {
                "input": {
                    "title": adapted["title"],
                    "contentMarkdown": adapted["contentMarkdown"],
                    "publicationId": pub_id,
                    "tags": adapted["tags"],
                }
            }

            if adapted.get("originalArticleURL"):
                variables["input"]["originalArticleURL"] = adapted["originalArticleURL"]

            response = await self.client.post(
                self.API_URL,
                json={"query": mutation, "variables": variables},
            )

            if response.is_success:
                data = response.json()
                errors = data.get("errors")
                if errors:
                    error_msgs = "; ".join(e.get("message", "") for e in errors)
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=False,
                        error=f"GraphQL errors: {error_msgs}",
                    )

                post = data.get("data", {}).get("publishPost", {}).get("post", {})
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
            query = "{ me { id } }"
            resp = await self.client.post(self.API_URL, json={"query": query})
            if resp.is_success:
                return resp.json().get("data", {}).get("me") is not None
            return False
        except Exception:
            return False
