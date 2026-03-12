#!/usr/bin/env python3
"""PreToolUse hook: check auth before publishing.

Exit 0: proceed (with optional stdout warning)
Exit 2: block tool call
"""

import json
import os
import sys


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Can't parse — don't block

    tool_name = data.get("tool_name", "")

    # Extract platform from tool name: mcp__promotion-agent__publish_zhihu → zhihu
    if "publish_" not in tool_name:
        sys.exit(0)
    platform = tool_name.split("publish_")[-1]

    checks = {
        "zhihu": [("PROMOTE_ZHIHU_COOKIE", "知乎 Cookie")],
        "x": [
            ("PROMOTE_X_CONSUMER_KEY", "X Consumer Key"),
            ("PROMOTE_X_CONSUMER_SECRET", "X Consumer Secret"),
            ("PROMOTE_X_ACCESS_TOKEN", "X Access Token"),
            ("PROMOTE_X_ACCESS_TOKEN_SECRET", "X Access Token Secret"),
        ],
        "wechat": [
            ("PROMOTE_WECHAT_APP_ID", "WeChat App ID"),
            ("PROMOTE_WECHAT_APP_SECRET", "WeChat App Secret"),
        ],
        "xiaohongshu": [],  # Auth managed by external MCP
    }

    required = checks.get(platform, [])
    missing = [name for env_key, name in required if not os.environ.get(env_key)]

    if not missing:
        sys.exit(0)  # All auth present — proceed

    # Check if this is a dry_run — warn but don't block
    tool_input = data.get("input", {})
    if tool_input.get("dry_run"):
        print(f"⚠️  Missing auth for {platform}: {', '.join(missing)} (dry_run allowed)")
        sys.exit(0)

    # Non-dry-run with missing auth — block the tool call
    print(f"❌ Missing auth for {platform}: {', '.join(missing)}", file=sys.stderr)
    print(f"Run auth_status for setup instructions.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
