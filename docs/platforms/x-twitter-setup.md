# X (Twitter) OAuth 配置指南

## 前提条件

需要 X (Twitter) 开发者账号和已创建的 App。

## 获取 OAuth 凭证步骤

### 1. 创建开发者账号

1. 访问 https://developer.x.com
2. 登录你的 X 账号
3. 申请开发者账号（选择 Free 免费套餐即可）

### 2. 创建 App

1. 进入 Developer Portal
2. 点击 "Projects & Apps" → "Create App"
3. 填写 App 名称和描述
4. 选择应用类型（选择 "Web App"）

### 3. 获取 OAuth 凭证

在 App 设置页面，找到 "Keys and Tokens" 标签：

#### Consumer Keys (API Key)
- **API Key** → `PROMOTE_X_CONSUMER_KEY`
- **API Secret Key** → `PROMOTE_X_CONSUMER_SECRET`

#### Access Tokens
- 点击 "Generate" 生成 Access Token
- **Access Token** → `PROMOTE_X_ACCESS_TOKEN`
- **Access Token Secret** → `PROMOTE_X_ACCESS_TOKEN_SECRET`

### 4. 配置权限

确保 App 有以下权限：
- Read and Write (读写权限)

在 "User authentication settings" 中：
- 开启 OAuth 1.0a
- 设置 Callback URL（可以是 localhost）

### 5. 配置 .env 文件

```bash
PROMOTE_X_CONSUMER_KEY=your_api_key_here
PROMOTE_X_CONSUMER_SECRET=your_api_secret_here
PROMOTE_X_ACCESS_TOKEN=your_access_token_here
PROMOTE_X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 6. 测试

```python
from promotion_agent.platforms.x_twitter import XTwitterPlatform
from promotion_agent.config.settings import PromotionSettings

settings = PromotionSettings()
platform = XTwitterPlatform(settings)

# 测试健康检查
print(platform.health_check())

# 测试发布
from promotion_agent.core.content import PromotionContent

content = PromotionContent(
    title="Test tweet from promotion-agent",
    body="",
    tags=["test", "automation"],
    url="https://github.com/kevinten10/promotion-agent"
)

result = platform.post(content)
print(result)
```

## 注意事项

### Free 套餐限制
- 每月 500 条推文
- 每天 20 条推文（硬限制）
- 只能访问自己的推文

### 常见问题

**401 Unauthorized**
- 检查 Access Token 是否正确生成
- 确保 Token 有 Write 权限
- 重新生成 Token

**403 Forbidden**
- 账号可能被限制
- 检查开发者账号状态

**429 Too Many Requests**
- 超过了速率限制
- Free 套餐每天限制 20 条

## 升级套餐

如果需要更多配额：
- **Basic**: $100/月, 3000 条/月
- **Pro**: $5000/月, 10000 条/月

访问 https://developer.x.com/en/portal/products 查看详情
