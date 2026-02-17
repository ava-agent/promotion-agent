"""Configuration management commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from promotion_agent.config.loader import load_settings

config_app = typer.Typer(help="Configuration management")
console = Console()


def _mask(value: str | None) -> str:
    """Mask a secret value for display."""
    if not value:
        return "[dim]not set[/dim]"
    if len(value) <= 8:
        return "****"
    return value[:4] + "****" + value[-4:]


@config_app.command("show")
def config_show() -> None:
    """Display current configuration (secrets masked)."""
    settings = load_settings()

    table = Table(title="Current Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    secret_keys = {"api_key", "secret", "password"}

    for key, value in settings.model_dump().items():
        display_key = f"PROMOTE_{key.upper()}"
        str_val = str(value) if value is not None else None

        if any(s in key for s in secret_keys):
            display_val = _mask(str_val)
        else:
            display_val = str_val or "[dim]not set[/dim]"

        table.add_row(display_key, display_val)

    console.print(table)


@config_app.command("validate")
def config_validate() -> None:
    """Validate all platform credentials."""
    import promotion_agent.platforms  # noqa: F401

    from promotion_agent.core.registry import list_platforms

    settings = load_settings()
    available = list_platforms()

    table = Table(title="Credential Validation")
    table.add_column("Platform", style="cyan")
    table.add_column("Status")

    for name, cls in available.items():
        try:
            instance = cls(settings)
            if instance.validate_config():
                table.add_row(name, "[green]Valid[/green]")
            else:
                table.add_row(name, "[red]Missing credentials[/red]")
        except Exception as e:
            table.add_row(name, f"[red]Error: {e}[/red]")

    console.print(table)
