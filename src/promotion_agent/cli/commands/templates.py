"""Template management commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.syntax import Syntax

from promotion_agent.content.templates import (
    list_templates,
    render_template,
    show_template,
)

templates_app = typer.Typer(help="Template management")
console = Console()


@templates_app.command("list")
def templates_list() -> None:
    """List available templates."""
    names = list_templates()
    if not names:
        console.print("[yellow]No templates found[/yellow]")
        return
    console.print("[bold]Available templates:[/bold]")
    for name in names:
        console.print(f"  - {name}")


@templates_app.command("show")
def templates_show(name: str = typer.Argument(help="Template name")) -> None:
    """Display raw template content."""
    try:
        content = show_template(name)
        syntax = Syntax(content, "markdown", theme="monokai")
        console.print(syntax)
    except FileNotFoundError:
        console.print(f"[red]Template '{name}' not found[/red]")
        raise typer.Exit(1)


@templates_app.command("render")
def templates_render(
    name: str = typer.Argument(help="Template name"),
    var: list[str] = typer.Option([], help="Variable KEY=VALUE"),
) -> None:
    """Render a template with variables."""
    variables = {}
    for v in var:
        if "=" in v:
            k, val = v.split("=", 1)
            variables[k] = val

    try:
        result = render_template(name, variables)
        console.print(result)
    except Exception as e:
        console.print(f"[red]Template error: {e}[/red]")
        raise typer.Exit(1)
