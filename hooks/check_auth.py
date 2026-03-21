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

    # Directory submissions don't need auth
    if "submit_directory" in tool_name:
        sys.exit(0)

    # Extract platform name from tool name
    # Case 1: publish_zhihu, publish_x, etc. (dedicated tools)
    # Case 2: publish (generic tool) — read platform from input
    if "publish_" in tool_name:
        platform = tool_name.split("publish_")[-1]
    elif tool_name.endswith("__publish"):
        platform = data.get("input", {}).get("platform", "")
        if not platform:
            sys.exit(0)  # Can't determine platform — don't block
    else:
        sys.exit(0)

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
        # Legacy migrated
        "juejin": [("PROMOTE_JUEJIN_COOKIE", "掘金 Cookie")],
        "csdn": [("PROMOTE_CSDN_COOKIE", "CSDN Cookie")],
        "devto": [("PROMOTE_DEVTO_API_KEY", "Dev.to API Key")],
        "reddit": [
            ("PROMOTE_REDDIT_CLIENT_ID", "Reddit Client ID"),
            ("PROMOTE_REDDIT_CLIENT_SECRET", "Reddit Client Secret"),
            ("PROMOTE_REDDIT_USERNAME", "Reddit Username"),
            ("PROMOTE_REDDIT_PASSWORD", "Reddit Password"),
        ],
        "linkedin": [("PROMOTE_LINKEDIN_ACCESS_TOKEN", "LinkedIn Access Token")],
        "producthunt": [("PROMOTE_PRODUCTHUNT_TOKEN", "Product Hunt Token")],
        "cnblogs": [
            ("PROMOTE_CNBLOGS_BLOG_URL", "CNBlogs Blog URL"),
            ("PROMOTE_CNBLOGS_USERNAME", "CNBlogs Username"),
            ("PROMOTE_CNBLOGS_TOKEN", "CNBlogs Token"),
        ],
        "hackernews": [
            ("PROMOTE_HN_USERNAME", "HN Username"),
            ("PROMOTE_HN_PASSWORD", "HN Password"),
        ],
        "moltbook": [("PROMOTE_MOLTBOOK_API_KEY", "MoltBook API Key")],
        # New platforms
        "medium": [("PROMOTE_MEDIUM_INTEGRATION_TOKEN", "Medium Integration Token")],
        "hashnode": [("PROMOTE_HASHNODE_TOKEN", "Hashnode Token")],
        "weibo": [("PROMOTE_WEIBO_ACCESS_TOKEN", "Weibo Access Token")],
        "v2ex": [("PROMOTE_V2EX_TOKEN", "V2EX Token")],
        "segmentfault": [("PROMOTE_SEGMENTFAULT_COOKIE", "SegmentFault Cookie")],
        "oschina": [("PROMOTE_OSCHINA_COOKIE", "OSCHINA Cookie")],
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
