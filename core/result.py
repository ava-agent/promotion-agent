"""Result models for platform posting operations."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PostResult:
    """Result of posting to a single platform."""

    platform: str
    success: bool
    url: Optional[str] = None
    post_id: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
