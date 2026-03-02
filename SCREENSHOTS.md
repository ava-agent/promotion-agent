# Screenshot Generation Guide

This document provides the exact commands and setup needed to capture screenshots for the README.

## Prerequisites

```bash
# Install the project
pip install -e .

# Set up minimal config for screenshots (use fake keys)
export PROMOTE_MOLTBOOK_API_KEY="mb_demo_key"
export PROMOTE_DEVTO_API_KEY="demo_devto_key"
export PROMOTE_HN_USERNAME="demo_user"
export PROMOTE_HN_PASSWORD="demo_pass"
```

## Screenshot List

### 1. Platform List (`promote platforms list`)

**Command:**
```bash
promote platforms list
```

**Expected Output:**
- A Rich table showing all 11 platforms
- Columns: Name, Display Name, Required Config
- Platforms: moltbook, reddit, devto, hackernews, x, producthunt, linkedin, juejin, csdn, zhihu, cnblogs

**Filename:** `screenshots/platforms-list.png`

---

### 2. Config Show (`promote config show`)

**Command:**
```bash
promote config show
```

**Expected Output:**
- Rich panel showing configuration
- Sensitive values masked (e.g., `mb_d****_key`)
- Shows which keys are set

**Filename:** `screenshots/config-show.png`

---

### 3. Health Check (`promote platforms check`)

**Command:**
```bash
promote platforms check
```

**Expected Output:**
- Table with platform names and status (✓ or ✗)
- Shows which platforms have valid credentials

**Filename:** `screenshots/health-check.png`

---

### 4. Templates List (`promote templates list`)

**Command:**
```bash
promote templates list
```

**Expected Output:**
- List of 3 templates: github_project_announce, project_update, tutorial_share
- Brief description of each

**Filename:** `screenshots/templates-list.png`

---

### 5. Dry Run Preview (`promote post --dry-run`)

**Command:**
```bash
promote post --all --dry-run \
  --title "Promotion Agent - Cross-Post to 11 Platforms" \
  --body "A CLI tool to automate posting your GitHub projects to social media." \
  --url "https://github.com/ava-agent/promotion-agent" \
  --tag ai --tag automation --tag opensource
```

**Expected Output:**
- Shows "DRY RUN - No posts will be created"
- Lists each platform with adapted content preview
- Shows title, body, tags for each platform

**Filename:** `screenshots/dry-run-preview.png`

---

### 6. Template Render (`promote templates render`)

**Command:**
```bash
promote templates render github_project_announce \
  --var project_name="Promotion Agent" \
  --var description="Cross-post your projects to 11 platforms" \
  --var github_url="https://github.com/ava-agent/promotion-agent" \
  --var features="11 platforms, OpenClaw integration, Content templates"
```

**Expected Output:**
- Rendered markdown content
- Shows title and formatted body

**Filename:** `screenshots/template-render.png`

---

### 7. Auth Status (`promote auth status`)

**Command:**
```bash
promote auth status
```

**Expected Output:**
- Shows cookie status for juejin, csdn, zhihu
- Indicates if cookies are set or not

**Filename:** `screenshots/auth-status.png`

---

### 8. Post Results (Mock)

**Setup:** This requires mocking since we don't want to post real content.

**Command (with valid API keys):**
```bash
promote post -p devto --title "Test Post" --body "Test content" --dry-run
```

Or create a mock screenshot showing:
- Success table with platform names
- URLs for each successful post
- Green checkmarks

**Filename:** `screenshots/post-results.png`

---

## Screenshot Tips

### Terminal Setup
```bash
# Use a dark theme for better visibility
# Recommended font: JetBrains Mono, Fira Code, or SF Mono
# Font size: 14-16px

# Clear terminal before each screenshot
clear

# Use a terminal with good color support (iTerm2, Windows Terminal, etc.)
```

### Image Guidelines
- **Format:** PNG (for clarity)
- **Size:** Crop to content, leave some padding
- **Resolution:** 2x for retina displays
- **Max width:** 800px for README

### Creating the screenshots directory
```bash
mkdir -p screenshots
```

## AI Image Generation Prompts

If you want to generate promotional images (not screenshots), here are prompts:

### Hero Image
```
A modern, minimalist 3D illustration of a rocket launching from a laptop screen,
surrounded by floating social media icons (Twitter/X, Reddit, LinkedIn, Dev.to,
Hacker News, Product Hunt). Dark background with neon accent colors.
Professional tech aesthetic, isometric view, soft lighting.
```

### Architecture Diagram
```
A clean flowchart diagram showing: "Content Input" box flowing to a central
"Promotion Agent" hub, which then branches out to 11 platform icons arranged
in a semi-circle. Use a modern flat design style with a dark theme and
blue/purple accent colors. Include labels for each platform.
```

### CLI Demo Mockup
```
A split-screen mockup showing: left side is a code editor with markdown content,
right side is a terminal showing the "promote post" command and success output.
Modern dark theme, syntax highlighting, professional developer tool aesthetic.
```
