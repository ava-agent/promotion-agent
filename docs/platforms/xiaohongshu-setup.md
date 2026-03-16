# 小红书 (Xiaohongshu) 配置指南

## 概述

小红书平台通过外部 MCP (Model Context Protocol) 服务器实现：
- **认证方式**: QR 码扫码登录
- **依赖**: xiaohongshu-mcp 外部服务器
- **管理**: MCP 服务器自动处理生命周期

## 安装步骤

### 1. 安装 xiaohongshu-mcp

```bash
# 克隆 MCP 服务器仓库
git clone https://github.com/anthropics/xiaohongshu-mcp.git .mcp-servers/xiaohongshu-mcp

# 安装依赖
cd .mcp-servers/xiaohongshu-mcp
pip install -e .
```

### 2. 启动 MCP 服务器

```bash
# 手动启动
python -m xiaohongshu_mcp --port 3001

# 或使用 promotion-agent 自动启动
promote auth qr-login xiaohongshu
```

### 3. QR 码登录

在 Claude Code 中运行：
```
"登录小红书"
"小红书扫码登录"
```

或直接调用：
```python
auth_qr_login(platform="xiaohongshu")
```

步骤：
1. MCP 服务器会生成 QR 码
2. 使用小红书 App 扫码
3. 确认登录
4. 等待认证完成

## 发布内容

### 支持的内容格式

```markdown
---
title: "笔记标题 (最多20字)"
images:
  - ./image1.jpg
  - ./image2.jpg
tags:
  - 标签1
  - 标签2
---

笔记正文内容...

#话题1 #话题2
```

### 发布命令

```
"帮我把这篇笔记发到小红书"
"发布到小红书"
```

或直接调用：
```python
publish_xiaohongshu(
    title="笔记标题",
    body="笔记内容",
    images=["./image1.jpg"],
    tags=["标签1", "标签2"]
)
```

## 注意事项

### 图片要求
- 格式: JPG, PNG
- 建议尺寸: 1080x1440 (3:4 比例)
- 最多 9 张图片

### 标题限制
- 最多 20 个字符
- 超出部分会自动截断

### 内容限制
- 正文字数限制: 1000 字
- 话题标签: 最多 10 个

## 故障排除

### MCP 服务器无法启动
```bash
# 检查端口是否被占用
lsof -i :3001

# 更换端口启动
python -m xiaohongshu_mcp --port 3002
```

### QR 码登录失败
- 确保小红书 App 是最新版本
- 检查网络连接
- 重新生成 QR 码

### 发布失败
- 检查图片路径是否正确
- 确认标题不超过 20 字
- 查看 MCP 服务器日志

## 相关链接

- [xiaohongshu-mcp GitHub](https://github.com/anthropics/xiaohongshu-mcp)
- [小红书创作者中心](https://creator.xiaohongshu.com/)
