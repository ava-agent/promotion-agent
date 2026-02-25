"""Platform management commands."""

from __future__ import annotations

import typer

from promotion_agent.cli.formatters import print_health, print_platforms
from promotion_agent.config.loader import load_settings
from promotion_agent.core.registry import list_platforms

platforms_app = typer.Typer(help="Platform management")


@platforms_app.command("list")
def platforms_list() -> None:
    """List all registered platforms."""
    import promotion_agent.platforms  # noqa: F401

    print_platforms(list_platforms())


@platforms_app.command("check")
def platforms_check() -> None:
    """Health check all configured platforms."""
    import promotion_agent.platforms  # noqa: F401

    settings = load_settings()
    available = list_platforms()
    checks: dict[str, bool] = {}

    for name, cls in available.items():
        try:
            instance = cls(settings)
            if not instance.validate_config():
                checks[name] = False
                continue
            checks[name] = instance.health_check()
        except Exception:
            checks[name] = False

    print_health(checks)
