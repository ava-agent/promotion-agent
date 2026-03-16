#!/usr/bin/env python3
"""自动从浏览器获取各平台 Cookie 并更新 .env 文件.

支持平台: 知乎(Zhihu), 掘金(Juejin), CSDN
支持浏览器: Chrome, Edge, Firefox, Safari (macOS)
"""

import os
import sys
import re
import glob
import platform
from typing import Optional, Dict, List, Tuple


def get_browser_cookie_paths(browser: str) -> List[str]:
    """获取指定浏览器的所有 Cookie 文件路径."""
    cookie_paths = []
    system = platform.system()

    if browser == "chrome":
        if system == "Darwin":  # macOS
            patterns = [
                '~/Library/Application Support/Google/Chrome/**/Cookies',
                '~/Library/Application Support/Google/Chrome Canary/**/Cookies',
            ]
        elif system == "Windows":
            patterns = [
                '~/AppData/Local/Google/Chrome/User Data/**/Cookies',
                '~/AppData/Local/Google/Chrome SxS/User Data/**/Cookies',
            ]
        else:  # Linux
            patterns = [
                '~/.config/google-chrome/**/Cookies',
                '~/.config/chromium/**/Cookies',
            ]

    elif browser == "edge":
        if system == "Darwin":
            patterns = [
                '~/Library/Application Support/Microsoft Edge/**/Cookies',
            ]
        elif system == "Windows":
            patterns = [
                '~/AppData/Local/Microsoft/Edge/User Data/**/Cookies',
            ]
        else:
            patterns = [
                '~/.config/microsoft-edge/**/Cookies',
            ]

    elif browser == "firefox":
        if system == "Darwin":
            patterns = [
                '~/Library/Application Support/Firefox/Profiles/**/cookies.sqlite',
            ]
        elif system == "Windows":
            patterns = [
                '~/AppData/Roaming/Mozilla/Firefox/Profiles/**/cookies.sqlite',
            ]
        else:
            patterns = [
                '~/.mozilla/firefox/**/cookies.sqlite',
            ]

    else:
        return []

    for pattern in patterns:
        paths = glob.glob(os.path.expanduser(pattern), recursive=True)
        cookie_paths.extend(paths)

    # 按修改时间排序，获取最新的
    try:
        cookie_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    except OSError:
        pass

    return cookie_paths


def extract_cookies_from_browser(browser: str, domain: str) -> Dict[str, str]:
    """从指定浏览器提取指定域名的 cookies."""
    try:
        import browser_cookie3
    except ImportError:
        print("❌ 需要先安装 browser_cookie3: python3 -m pip install browser-cookie3")
        sys.exit(1)

    cookie_paths = get_browser_cookie_paths(browser)

    for cookie_path in cookie_paths:
        try:
            if browser == "chrome":
                cj = browser_cookie3.chrome(cookie_file=cookie_path, domain_name=domain)
            elif browser == "edge":
                cj = browser_cookie3.edge(cookie_file=cookie_path, domain_name=domain)
            elif browser == "firefox":
                cj = browser_cookie3.firefox(cookie_file=cookie_path, domain_name=domain)
            else:
                continue

            cookies = {cookie.name: cookie.value for cookie in cj}
            if cookies:
                return cookies
        except Exception as e:
            # 忽略单个文件的错误，尝试下一个
            continue

    return {}


def extract_cookies_with_fallback(domain: str, browsers: List[str] = None) -> Tuple[Dict[str, str], str]:
    """尝试从多个浏览器提取 cookies，返回第一个成功的结果."""
    if browsers is None:
        browsers = ["chrome", "edge", "firefox"]

    for browser in browsers:
        cookies = extract_cookies_from_browser(browser, domain)
        if cookies:
            return cookies, browser

    return {}, ""


def format_cookie_string(cookies: Dict[str, str], platform: str) -> str:
    """根据平台格式化 cookie 字符串."""
    if platform == "zhihu":
        # 知乎需要的核心字段
        essential = ['_xsrf', '_zap', 'd_c0', 'z_c0', 'SESSIONID', '__snaker__id', 'captcha_ticket_v2']
    elif platform == "juejin":
        # 掘金需要的核心字段
        essential = ['sessionid', 'sessionid_ss', 'nuxt_cookie']
    elif platform == "csdn":
        # CSDN 需要的核心字段
        essential = ['UserName', 'UserInfo', 'uuid', 'dc_session_id', 'c_hasSubscibeTower']
    else:
        essential = []

    # 先添加核心字段
    parts = []
    for key in essential:
        if key in cookies:
            parts.append(f"{key}={cookies[key]}")

    # 添加其他字段
    for key, value in cookies.items():
        if key not in essential:
            parts.append(f"{key}={value}")

    return '; '.join(parts)


def update_env_file(platform: str, cookie_str: str, env_file: str = '.env') -> bool:
    """更新 .env 文件中的指定平台 Cookie."""
    var_name = f"PROMOTE_{platform.upper()}_COOKIE"

    try:
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = ""

        new_line = f"{var_name}={cookie_str}\n"
        pattern = rf'^{re.escape(var_name)}=.*$'

        if re.search(pattern, content, re.MULTILINE):
            new_content = re.sub(pattern, new_line.strip(), content, flags=re.MULTILINE)
            print(f"  📝 更新现有 {platform} Cookie...")
        else:
            new_content = content + new_line
            print(f"  📝 添加新 {platform} Cookie...")

        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"  ❌ 更新 .env 文件失败: {e}")
        return False


def test_zhihu_cookie(cookie_str: str) -> bool:
    """测试知乎 Cookie 是否有效."""
    import urllib.request
    import json

    req = urllib.request.Request(
        'https://www.zhihu.com/api/v4/me',
        headers={
            'Cookie': cookie_str,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if 'name' in data:
                print(f"  ✅ Cookie 有效! 登录用户: {data.get('name')}")
                return True
            elif 'error' in data:
                print(f"  ⚠️  Cookie 可能无效: {data['error'].get('message', 'Unknown')}")
                return False
    except urllib.error.HTTPError as e:
        print(f"  ⚠️  HTTP 错误 {e.code}: {e.reason}")
    except Exception as e:
        print(f"  ⚠️  测试请求失败: {e}")
    return False


def test_juejin_cookie(cookie_str: str) -> bool:
    """测试掘金 Cookie 是否有效."""
    import urllib.request
    import json

    req = urllib.request.Request(
        'https://api.juejin.cn/user_api/v1/user/get',
        headers={
            'Cookie': cookie_str,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('err_no') == 0:
                user_name = data.get('data', {}).get('user_name', 'Unknown')
                print(f"  ✅ Cookie 有效! 登录用户: {user_name}")
                return True
            else:
                print(f"  ⚠️  Cookie 可能无效: {data.get('err_msg', 'Unknown')}")
    except urllib.error.HTTPError as e:
        print(f"  ⚠️  HTTP 错误 {e.code}: {e.reason}")
    except Exception as e:
        print(f"  ⚠️  测试请求失败: {e}")
    return False


def test_csdn_cookie(cookie_str: str) -> bool:
    """测试 CSDN Cookie 是否有效."""
    import urllib.request
    import json

    req = urllib.request.Request(
        'https://blog-console-api.csdn.net/v1/user/info',
        headers={
            'Cookie': cookie_str,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('code') == 200:
                username = data.get('data', {}).get('username', '')
                print(f"  ✅ Cookie 有效! 登录用户: {username or 'Unknown'}")
                return True
            elif 'username' in str(data).lower():
                print(f"  ✅ Cookie 看起来有效")
                return True
            else:
                print(f"  ⚠️  Cookie 可能无效: {data.get('message', 'Unknown')}")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print(f"  ⚠️  Cookie 已过期或无效 (401 Unauthorized)")
        elif e.code == 403:
            print(f"  ⚠️  访问被拒绝 (403 Forbidden)，Cookie 可能已过期")
        else:
            print(f"  ⚠️  HTTP 错误 {e.code}: {e.reason}")
    except Exception as e:
        print(f"  ⚠️  测试请求失败: {e}")
    return False


def extract_platform(platform: str, domain: str, browsers: List[str] = None) -> bool:
    """提取单个平台的 Cookie."""
    platform_names = {
        'zhihu': '知乎',
        'juejin': '掘金',
        'csdn': 'CSDN'
    }

    name = platform_names.get(platform, platform)
    print(f"\n🔍 正在获取 {name} ({platform}) Cookie...")

    cookies, browser_used = extract_cookies_with_fallback(domain, browsers)

    if not cookies:
        print(f"  ❌ 未找到 {name} Cookie，请确认已登录")
        print(f"     支持的浏览器: {', '.join(browsers or ['chrome', 'edge', 'firefox'])}")
        return False

    cookie_str = format_cookie_string(cookies, platform)
    print(f"  ✅ 从 {browser_used.title()} 找到 {len(cookies)} 个 cookie 字段")

    if update_env_file(platform, cookie_str):
        print(f"  🧪 测试 Cookie 有效性...")

        if platform == 'zhihu':
            return test_zhihu_cookie(cookie_str)
        elif platform == 'juejin':
            return test_juejin_cookie(cookie_str)
        elif platform == 'csdn':
            return test_csdn_cookie(cookie_str)

    return False


def refresh_single_platform(platform: str) -> bool:
    """刷新单个平台的 Cookie."""
    platforms_config = {
        'zhihu': ('zhihu', 'zhihu.com'),
        'juejin': ('juejin', 'juejin.cn'),
        'csdn': ('csdn', 'csdn.net'),
    }

    if platform not in platforms_config:
        print(f"❌ 不支持的平台: {platform}")
        print(f"   支持的平台: {', '.join(platforms_config.keys())}")
        return False

    name, domain = platforms_config[platform]
    return extract_platform(name, domain)


def main():
    """主函数."""
    import argparse

    parser = argparse.ArgumentParser(
        description='自动从浏览器获取各平台 Cookie 并更新 .env 文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 get_cookies.py                    # 获取所有平台
  python3 get_cookies.py -p zhihu           # 仅获取知乎
  python3 get_cookies.py -p juejin,csdn     # 获取掘金和CSDN
  python3 get_cookies.py --browser edge     # 优先使用 Edge 浏览器
        """
    )
    parser.add_argument(
        '-p', '--platform',
        help='指定平台 (zhihu, juejin, csdn)，多个用逗号分隔',
        default='all'
    )
    parser.add_argument(
        '--browser',
        help='优先使用的浏览器 (chrome, edge, firefox)',
        default=None
    )
    parser.add_argument(
        '--env-file',
        help='环境文件路径 (默认: .env)',
        default='.env'
    )

    args = parser.parse_args()

    # 确定浏览器优先级
    browsers = None
    if args.browser:
        browsers = [args.browser.lower()]

    print("=" * 60)
    print("多平台 Cookie 自动获取工具")
    print("支持: 知乎(Zhihu), 掘金(Juejin), CSDN")
    print("=" * 60)

    if args.platform == 'all':
        platforms = [
            ('zhihu', 'zhihu.com'),
            ('juejin', 'juejin.cn'),
            ('csdn', 'csdn.net'),
        ]
    else:
        platform_map = {
            'zhihu': ('zhihu', 'zhihu.com'),
            'juejin': ('juejin', 'juejin.cn'),
            'csdn': ('csdn', 'csdn.net'),
        }
        platforms = []
        for p in args.platform.split(','):
            p = p.strip().lower()
            if p in platform_map:
                platforms.append(platform_map[p])
            else:
                print(f"❌ 不支持的平台: {p}")

    if not platforms:
        print("❌ 没有有效的平台需要处理")
        return

    results = {}
    for platform, domain in platforms:
        try:
            success = extract_platform(platform, domain, browsers)
            results[platform] = success
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            results[platform] = False

    print("\n" + "=" * 60)
    print("汇总结果:")
    print("=" * 60)
    for platform, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {platform.upper():10} {status}")

    success_count = sum(results.values())
    print(f"\n总计: {success_count}/{len(results)} 个平台配置成功")
    print("=" * 60)

    if success_count < len(results):
        print("\n提示: 如果某些平台失败，请尝试:")
        print("  1. 确保已在浏览器中登录对应平台")
        print("  2. 使用 --browser 参数指定其他浏览器")
        print("  3. 检查 .env 文件是否被正确更新")


if __name__ == '__main__':
    main()
