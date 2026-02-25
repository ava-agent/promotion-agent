"""Platform implementations. Importing this module registers all platforms."""

# International
from promotion_agent.platforms.moltbook import MoltBookPlatform  # noqa: F401
from promotion_agent.platforms.reddit import RedditPlatform  # noqa: F401
from promotion_agent.platforms.devto import DevToPlatform  # noqa: F401
from promotion_agent.platforms.hackernews import HackerNewsPlatform  # noqa: F401
from promotion_agent.platforms.x_twitter import XTwitterPlatform  # noqa: F401
from promotion_agent.platforms.producthunt import ProductHuntPlatform  # noqa: F401
from promotion_agent.platforms.linkedin import LinkedInPlatform  # noqa: F401

# China / 国内平台
from promotion_agent.platforms.juejin import JuejinPlatform  # noqa: F401
from promotion_agent.platforms.csdn import CSDNPlatform  # noqa: F401
from promotion_agent.platforms.zhihu import ZhihuPlatform  # noqa: F401
from promotion_agent.platforms.cnblogs import CNBlogsPlatform  # noqa: F401
