"""MoltBook platform — AI Agent Social Network."""

from __future__ import annotations

import re

from core.base_platform import BaseHttpPlatform
from core.content import PromotionContent
from core.registry import register_platform
from core.result import PostResult


@register_platform
class MoltBookPlatform(BaseHttpPlatform):
    PLATFORM_NAME = "moltbook"
    DISPLAY_NAME = "MoltBook"
    REQUIRED_CONFIG_KEYS = ["moltbook_api_key"]

    BASE_URL = "https://www.moltbook.com/api/v1"

    def __init__(self, config):
        self.api_key = getattr(config, "moltbook_api_key", None)
        self._client = None

    def _default_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _client_kwargs(self) -> dict:
        return {"base_url": self.BASE_URL}

    def validate_config(self) -> bool:
        return bool(self.api_key)

    def adapt_content(self, content: PromotionContent) -> dict:
        submolt = content.metadata.get("moltbook_submolt", "general")
        body = content.body
        if content.url:
            body += f"\n\n{content.url}"
        return {
            "submolt": submolt,
            "title": content.title,
            "content": body,
        }

    def _solve_challenge(self, challenge_text: str) -> float:
        """Solve MoltBook verification challenge (velocity + acceleration)."""
        numbers = re.findall(r"[-+]?\d*\.?\d+", challenge_text)
        if len(numbers) >= 2:
            return round(float(numbers[0]) + float(numbers[1]), 2)
        raise ValueError(f"Cannot parse challenge: {challenge_text}")

    async def post(self, content: PromotionContent) -> PostResult:
        try:
            payload = self.adapt_content(content)
            response = await self.client.post("/posts", json=payload)

            # Handle challenge-response verification
            if response.status_code == 202:
                data = response.json()
                challenge = data.get("challenge", "")
                answer = self._solve_challenge(challenge)
                verify_resp = await self.client.post(
                    "/posts/verify",
                    json={**payload, "challenge_answer": answer},
                )
                if verify_resp.is_success:
                    result_data = verify_resp.json()
                    return PostResult(
                        platform=self.PLATFORM_NAME,
                        success=True,
                        url=result_data.get("url"),
                        post_id=str(result_data.get("id", "")),
                    )
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=False,
                    error=f"Challenge verification failed: {verify_resp.text}",
                )

            if response.is_success:
                data = response.json()
                return PostResult(
                    platform=self.PLATFORM_NAME,
                    success=True,
                    url=data.get("url"),
                    post_id=str(data.get("id", "")),
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
            resp = await self.client.get("/posts?limit=1")
            return resp.is_success
        except Exception:
            return False
