#!/usr/bin/env python3
"""自动从 Chrome 浏览器获取知乎 Cookie 并更新 .env 文件."""

import os
import sys
import re


def get_zhihu_cookie_from_chrome():
    """从 Chrome 浏览器读取知乎 Cookie."""
    try:
        import browser_cookie3
    except ImportError:
        print("❌ 需要先安装 browser_cookie3: pip install browser-cookie3")
        print("或者: uv add browser-cookie3")
        sys.exit(1)

    print("🔍 正在从 Chrome 读取知乎 Cookie...")

    try:
        # 获取 Chrome 的所有 cookie (尝试多个 profile)
        cj = None
        import sqlite3
        import glob

        # 查找所有 Chrome profile 的 cookie 文件
        cookie_paths = glob.glob(os.path.expanduser(
            '~/Library/Application Support/Google/Chrome/**/Cookies'),
            recursive=True
        )

        # 按修改时间排序，获取最新的
        cookie_paths.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        for cookie_path in cookie_paths:
            try:
                print(f"   尝试读取: {cookie_path}")
                cj = browser_cookie3.chrome(
                    cookie_file=cookie_path,
                    domain_name='zhihu.com'
                )
                if cj:
                    break
            except Exception as e:
                continue

        if not cj:
            cj = browser_cookie3.chrome(domain_name='zhihu.com')

        # 提取需要的 cookie
        cookie_dict = {}
        for cookie in cj:
            if 'zhihu' in cookie.domain:
                cookie_dict[cookie.name] = cookie.value

        if not cookie_dict:
            print("❌ 未找到知乎 Cookie，请确认已登录知乎")
            return None

        # 知乎 API 需要的核心 cookie 字段
        essential_cookies = [
            '_xsrf',      # CSRF token
            '_zap',       # 追踪 ID
            'd_c0',       # 设备 ID
            '__snaker__id',  # 反爬 ID
            'captcha_ticket_v2',  # 验证码票据
            'z_c0',       # 登录凭证 (重要!)
            'SESSIONID',  # Session ID
        ]

        # 构建 cookie 字符串
        cookie_parts = []
        found_essential = []

        for name in essential_cookies:
            if name in cookie_dict:
                cookie_parts.append(f"{name}={cookie_dict[name]}")
                found_essential.append(name)

        # 添加其他可能需要的 cookie
        for name, value in cookie_dict.items():
            if name not in essential_cookies:
                cookie_parts.append(f"{name}={value}")

        cookie_str = '; '.join(cookie_parts)

        print(f"✅ 找到 {len(cookie_dict)} 个 cookie 字段")
        print(f"   核心字段: {', '.join(found_essential)}")

        # 检查关键登录凭证
        if 'z_c0' not in cookie_dict and 'SESSIONID' not in cookie_dict:
            print("⚠️ 警告: 未找到登录凭证 (z_c0 或 SESSIONID)")
            print("   可能未登录或 Cookie 已过期")

        return cookie_str

    except Exception as e:
        print(f"❌ 读取 Cookie 失败: {e}")
        return None


def update_env_file(cookie_str):
    """更新 .env 文件中的知乎 Cookie."""
    env_file = '.env'

    try:
        # 读取现有内容
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = ""

        # 构建新的 cookie 行
        new_line = f"PROMOTE_ZHIHU_COOKIE={cookie_str}\n"

        # 检查是否已存在该变量
        pattern = r'^PROMOTE_ZHIHU_COOKIE=.*$'
        if re.search(pattern, content, re.MULTILINE):
            # 替换现有行
            new_content = re.sub(pattern, new_line.strip(), content, flags=re.MULTILINE)
            print("📝 更新现有 Cookie...")
        else:
            # 添加新行
            new_content = content + new_line
            print("📝 添加新 Cookie...")

        # 写入文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"✅ Cookie 已保存到 {env_file}")
        return True

    except Exception as e:
        print(f"❌ 更新 .env 文件失败: {e}")
        return False


def test_cookie(cookie_str):
    """快速测试 Cookie 是否有效."""
    import urllib.request
    import json

    print("\n🧪 测试 Cookie 有效性...")

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
                print(f"✅ Cookie 有效! 登录用户: {data.get('name')}")
                return True
            elif 'error' in data:
                print(f"❌ Cookie 无效: {data['error'].get('message', 'Unknown error')}")
                return False
            else:
                print(f"⚠️ 未知响应: {data}")
                return False

    except Exception as e:
        print(f"❌ 测试请求失败: {e}")
        return False


def main():
    """主函数."""
    print("=" * 50)
    print("知乎 Cookie 自动获取工具")
    print("=" * 50)
    print()

    # 获取 cookie
    cookie_str = get_zhihu_cookie_from_chrome()
    if not cookie_str:
        sys.exit(1)

    # 更新 .env 文件
    if not update_env_file(cookie_str):
        sys.exit(1)

    # 测试 cookie
    test_cookie(cookie_str)

    print()
    print("=" * 50)
    print("完成! 现在可以运行知乎发布测试了")
    print("=" * 50)


if __name__ == '__main__':
    main()
