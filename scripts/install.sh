#!/usr/bin/env bash
# Install promotion-agent as an OpenClaw skill
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Installing promotion-agent from ${SKILL_DIR}..."

# Prefer uv, fallback to pip
if command -v uv &> /dev/null; then
    uv pip install -e "${SKILL_DIR}"
elif command -v pip3 &> /dev/null; then
    pip3 install -e "${SKILL_DIR}"
elif command -v pip &> /dev/null; then
    pip install -e "${SKILL_DIR}"
else
    echo "Error: Neither uv nor pip found. Install Python first."
    exit 1
fi

echo ""
echo "Installation complete. Verify with:"
echo "  promote platforms list"
echo ""
echo "Configure API keys in ~/.openclaw/openclaw.json under skills.entries.promotion-agent"
