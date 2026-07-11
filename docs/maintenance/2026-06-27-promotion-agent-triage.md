# Promotion Agent Triage - 2026-06-27

## Repository

- GitHub: `ava-agent/promotion-agent`
- Category: Claude Code plugin and MCP server for multi-platform publishing

## Actions Taken

- Added npm `dev`, `build`, `test`, and `lint` aliases for docs, pytest, and Python compile checks.
- Added `node_modules/` to `.gitignore` so local VitePress installs stay out of repository status.
- Replaced a relative VitePress LICENSE link with a stable GitHub URL.
- Aligned the Python requirement with FastMCP (`>=3.10`) and synchronized npm metadata with the v4 plugin package.
- Scoped release secret scans away from the ignored local `.env`, dependency directory, and Python bytecode caches.

## Validation

- Passed: isolated Python 3.12 test environment (208 passed, 4 skipped)
- Passed: `npm run lint`
- Passed with VitePress chunk and `env` highlighter warnings: `npm run build`
- Passed: `gitleaks dir . --no-banner --redact`

## Follow-Up

- `src/promotion_agent/platforms/agentverse.py` remains an untracked v3 draft. Do not publish it until it is ported to the root v4 platform registry with settings, auth/hook wiring, server import, tests, and a verified external API contract.
