"""Tests for result data models."""

from core.result import PostResult


def test_post_result_defaults():
    result = PostResult(platform="test", success=True)
    assert result.platform == "test"
    assert result.success is True
    assert result.url is None
    assert result.post_id is None
    assert result.error is None
    assert result.error_type is None


def test_post_result_success():
    result = PostResult(
        platform="zhihu",
        success=True,
        url="https://zhihu.com/p/123",
        post_id="123",
    )
    assert result.platform == "zhihu"
    assert result.success is True
    assert result.url == "https://zhihu.com/p/123"
    assert result.post_id == "123"


def test_post_result_failure():
    result = PostResult(
        platform="x",
        success=False,
        error="Rate limited",
        error_type="rate_limit",
    )
    assert result.success is False
    assert result.error == "Rate limited"
    assert result.error_type == "rate_limit"


def test_post_result_error_type_field():
    """The v4 PostResult adds an error_type field not present in v3."""
    result = PostResult(
        platform="wechat",
        success=False,
        error="Auth expired",
        error_type="auth_error",
    )
    assert result.error_type == "auth_error"
