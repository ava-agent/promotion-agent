"""Shared test fixtures."""

import pytest

from promotion_agent.core.content import PromotionContent


@pytest.fixture
def sample_content():
    return PromotionContent(
        title="Test Project - AI Tool",
        body="This is a test project for AI automation.",
        tags=["ai", "python", "automation"],
        url="https://github.com/kevinten10/test-project",
        description="A test AI project",
    )


@pytest.fixture
def reddit_content():
    return PromotionContent(
        title="Test Project - AI Tool",
        body="Check out this AI project.",
        tags=["ai"],
        url="https://github.com/kevinten10/test-project",
        metadata={"reddit_subreddit": "test"},
    )


@pytest.fixture
def moltbook_content():
    return PromotionContent(
        title="AI Agent Update",
        body="New AI agent capabilities released.",
        tags=["ai", "agents"],
        url="https://github.com/kevinten10/test-project",
        metadata={"moltbook_submolt": "ai-agents"},
    )


class MockConfig:
    """Mock configuration for testing."""

    moltbook_api_key = "test_mb_key"
    moltbook_default_submolt = "general"
    reddit_client_id = "test_client_id"
    reddit_client_secret = "test_client_secret"
    reddit_username = "test_user"
    reddit_password = "test_pass"
    reddit_user_agent = "test-agent:v0.1"
    reddit_default_subreddit = "test"
    devto_api_key = "test_devto_key"
    github_username = "kevinten10"


@pytest.fixture
def mock_config():
    return MockConfig()
