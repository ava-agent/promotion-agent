"""Authentication commands — set/clear cookies and tokens for platforms."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from promotion_agent.config.loader import load_settings

auth_app = typer.Typer(help="Authentication management")
console = Console()

# Platforms that use cookie-based auth and the corresponding env key
COOKIE_PLATFORMS = {
    "juejin": "PROMOTE_JUEJIN_COOKIE",
    "csdn": "PROMOTE_CSDN_COOKIE",
    "zhihu": "PROMOTE_ZHIHU_COOKIE",
}


def _env_file_path() -> Path:
    """Return the .env file path to write to."""
    # Prefer PROMOTE_ENV_FILE, then OpenClaw skill dir, then ~/.config
    import os

    override = os.environ.get("PROMOTE_ENV_FILE")
    if override:
        return Path(override)

    openclaw_env = Path.home() / ".openclaw" / "skills" / "promotion-agent" / ".env"
    config_env = Path.home() / ".config" / "promotion-agent" / ".env"
    cwd_env = Path.cwd() / ".env"

    # Return the first one that already exists, or default to openclaw path
    for path in [cwd_env, config_env, openclaw_env]:
        try:
            if path.is_file():
                return path
        except (OSError, PermissionError):
            continue

    # Default: create in openclaw skill dir
    return openclaw_env


def _read_env_dict(path: Path) -> dict[str, str]:
    """Read a .env file into a dict, preserving order."""
    result: dict[str, str] = {}
    if not path.is_file():
        return result
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, value = line.split("=", 1)
            result[key.strip()] = value.strip()
    return result


def _write_env_dict(path: Path, env: dict[str, str]) -> None:
    """Write a dict back to a .env file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{k}={v}" for k, v in env.items()]
    path.write_text("\n".join(lines) + "\n")


@auth_app.command("set-cookie")
def set_cookie(
    platform: str = typer.Argument(help="Platform name: juejin, csdn, or zhihu"),
    cookie: str = typer.Argument(help="Cookie string from browser"),
) -> None:
    """Save a cookie for a Chinese platform."""
    platform = platform.lower()
    if platform not in COOKIE_PLATFORMS:
        console.print(
            f"[red]Unknown cookie platform: {platform}. "
            f"Choose from: {', '.join(COOKIE_PLATFORMS)}[/red]"
        )
        raise typer.Exit(1)

    env_key = COOKIE_PLATFORMS[platform]
    env_path = _env_file_path()

    env = _read_env_dict(env_path)
    env[env_key] = cookie
    _write_env_dict(env_path, env)

    console.print(f"[green]Saved {env_key} to {env_path}[/green]")
    console.print(f"Cookie length: {len(cookie)} chars")


@auth_app.command("clear-cookie")
def clear_cookie(
    platform: str = typer.Argument(help="Platform name: juejin, csdn, or zhihu"),
) -> None:
    """Remove a saved cookie for a platform."""
    platform = platform.lower()
    if platform not in COOKIE_PLATFORMS:
        console.print(
            f"[red]Unknown cookie platform: {platform}. "
            f"Choose from: {', '.join(COOKIE_PLATFORMS)}[/red]"
        )
        raise typer.Exit(1)

    env_key = COOKIE_PLATFORMS[platform]
    env_path = _env_file_path()

    env = _read_env_dict(env_path)
    if env_key in env:
        del env[env_key]
        _write_env_dict(env_path, env)
        console.print(f"[green]Removed {env_key} from {env_path}[/green]")
    else:
        console.print(f"[yellow]{env_key} not found in {env_path}[/yellow]")


@auth_app.command("status")
def auth_status() -> None:
    """Show authentication status for all cookie-based platforms."""
    settings = load_settings()

    from rich.table import Table

    table = Table(title="Cookie Auth Status")
    table.add_column("Platform", style="cyan")
    table.add_column("Status")
    table.add_column("Cookie Length")

    for platform, env_key in COOKIE_PLATFORMS.items():
        attr = env_key.replace("PROMOTE_", "").lower()
        value = getattr(settings, attr, None)
        if value:
            table.add_row(
                platform,
                "[green]Set[/green]",
                str(len(value)),
            )
        else:
            table.add_row(platform, "[red]Not set[/red]", "-")

    console.print(table)
    console.print(
        "\n[dim]Tip: Cookies expire ~monthly. "
        "Use 'promote auth set-cookie <platform> <cookie>' to update.[/dim]"
    )
