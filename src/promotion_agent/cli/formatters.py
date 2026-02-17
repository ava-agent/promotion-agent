"""Rich console output formatting."""

from rich.console import Console
from rich.table import Table

from promotion_agent.core.result import PostResult

console = Console()


def print_results(results: list[PostResult]) -> None:
    """Print posting results in a formatted table."""
    table = Table(title="Posting Results")
    table.add_column("Platform", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("URL / Error")

    for r in results:
        status = "[green]OK[/green]" if r.success else "[red]FAIL[/red]"
        detail = r.url or r.error or ""
        table.add_row(r.platform, status, detail)

    console.print(table)


def print_platforms(platforms: dict) -> None:
    """Print registered platforms in a table."""
    table = Table(title="Registered Platforms")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name")
    table.add_column("Required Config")

    for name, cls in platforms.items():
        keys = ", ".join(cls.REQUIRED_CONFIG_KEYS) if cls.REQUIRED_CONFIG_KEYS else "-"
        table.add_row(name, cls.DISPLAY_NAME, keys)

    console.print(table)


def print_health(checks: dict[str, bool]) -> None:
    """Print health check results."""
    table = Table(title="Platform Health Check")
    table.add_column("Platform", style="cyan")
    table.add_column("Status")

    for name, ok in checks.items():
        status = "[green]Connected[/green]" if ok else "[red]Failed[/red]"
        table.add_row(name, status)

    console.print(table)
