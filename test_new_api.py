#!/usr/bin/env python3
"""测试新版掘金API"""

import sys
sys.path.insert(0, '/Users/kevinten/projects/promotion-agent/src')

from promotion_agent.config.settings import PromotionSettings
from promotion_agent.core.content import PromotionContent
from promotion_agent.platforms.juejin_new import JuejinPlatformNew

def test_new_juejin_api():
    print("="*60)
    print("测试掘金新版API")
    print("="*60)

    # 创建测试内容
    test_content = PromotionContent(
        title="测试文章：新版API发布验证",
        body="""这是一篇测试文章，用于验证新版API的功能。

## 测试内容

- 智能标签选择
- 自动分类
- 直接发布

如果看到这篇文章，说明新版API正常工作！

---

*本文用于测试自动化发布*""",
        description="测试新版API",
        tags=["测试", "API"],
        url="https://github.com/kevinten10/promotion-agent",
    )

    settings = PromotionSettings()
    platform = JuejinPlatformNew(settings)

    # 检查配置
    if not platform.validate_config():
        print("❌ Cookie未配置")
        return False

    print("✅ Cookie已配置")
    print(f"📝 选择的标签: {platform._select_tags(test_content)}")
    print(f"📝 选择的分类: {platform._select_category(test_content)}")

    # 测试发布
    print("\n🚀 开始发布...")
    result = platform.post(test_content)

    if result.success:
        print(f"✅ 发布成功!")
        print(f"   URL: {result.url}")
        print(f"   Post ID: {result.post_id}")
        return True
    else:
        print(f"❌ 发布失败: {result.error}")
        return False

if __name__ == "__main__":
    success = test_new_juejin_api()
    sys.exit(0 if success else 1)
