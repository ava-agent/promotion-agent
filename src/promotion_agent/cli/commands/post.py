"""The main `promote post` command."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from promotion_agent.cli.formatters import print_results
from promotion_agent.config.loader import load_settings
from promotion_agent.core.content import PromotionContent
from promotion_agent.core.registry import list_platforms
from promotion_agent.core.result import PostResult
from promotion_agent.content.templates import render_template

console = Console()


def post_command(
    platform: list[str] = typer.Option(
        [], "-p", "--platform", help="Target platform(s)"
    ),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="Post title"),
    body: Optional[str] = typer.Option(None, "-b", "--body", help="Post body"),
    file: Optional[Path] = typer.Option(
        None, "-f", "--file", help="Read body from file"
    ),
    template: Optional[str] = typer.Option(None, help="Use a named template"),
    var: list[str] = typer.Option([], help="Template variable KEY=VALUE"),
    tag: list[str] = typer.Option([], help="Tags"),
    url: Optional[str] = typer.Option(None, help="Project URL"),
    subreddit: Optional[str] = typer.Option(None, help="Reddit subreddit"),
    submolt: Optional[str] = typer.Option(None, help="MoltBook submolt"),
    draft: bool = typer.Option(False, help="Dev.to: save as draft"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without posting"),
    all_platforms: bool = typer.Option(False, "--all", help="Post to all platforms"),
) -> None:
    """Post content to social media platforms."""
    # Import platforms to trigger registration
    import promotion_agent.platforms  # noqa: F401

    settings = load_settings()

    # Resolve body content
    post_body = _resolve_body(body, file, template, var)
    if not title:
        console.print("[red]Error: --title is required[/red]")
        raise typer.Exit(1)
    if not post_body:
        console.print("[red]Error: --body, --file, or --template is required[/red]")
        raise typer.Exit(1)

    # Build metadata
    metadata: dict = {}
    if subreddit:
        metadata["reddit_subreddit"] = subreddit
    if submolt:
        metadata["moltbook_submolt"] = submolt
    if draft:
        metadata["devto_published"] = False

    content = PromotionContent(
        title=title,
        body=post_body,
        tags=tag,
        url=url,
        metadata=metadata,
    )

    # Determine target platforms
    targets = _resolve_targets(platform, all_platforms)
    if not targets:
        console.print("[red]Error: specify --platform or --all[/red]")
        raise typer.Exit(1)

    if dry_run:
        _print_dry_run(content, targets)
        return

    # Post to each platform
    results: list[PostResult] = []
    available = list_platforms()

    for name in targets:
        if name not in available:
            results.append(
                PostResult(platform=name, success=False, error="Platform not found")
            )
            continue

        cls = available[name]
        try:
            instance = cls(settings)
            if not instance.validate_config():
                results.append(
                    PostResult(
                        platform=name,
                        success=False,
                        error="Missing configuration. Check .env file.",
                    )
                )
                continue
            result = instance.post(content)
            results.append(result)
        except Exception as e:
            results.append(PostResult(platform=name, success=False, error=str(e)))

    print_results(results)


def _resolve_body(
    body: str | None,
    file: Path | None,
    template: str | None,
    var: list[str],
) -> str | None:
    """Resolve post body from body text, file, or template."""
    if body:
        return body
    if file:
        return file.read_text()
    if template:
        variables = {}
        for v in var:
            if "=" in v:
                k, val = v.split("=", 1)
                variables[k] = val
        return render_template(template, variables)
    return None


def _resolve_targets(platform: list[str], all_platforms: bool) -> list[str]:
    """Resolve which platforms to target."""
    if all_platforms:
        import promotion_agent.platforms  # noqa: F401

        return list(list_platforms().keys())
    return platform


def _print_dry_run(content: PromotionContent, targets: list[str]) -> None:
    """Print dry-run preview."""
    console.print("\n[bold yellow]DRY RUN - No content will be posted[/bold yellow]\n")
    console.print(f"[bold]Title:[/bold] {content.title}")
    console.print(f"[bold]URL:[/bold] {content.url or 'N/A'}")
    console.print(f"[bold]Tags:[/bold] {', '.join(content.tags) or 'N/A'}")
    console.print(f"[bold]Targets:[/bold] {', '.join(targets)}")
    console.print(f"\n[bold]Body:[/bold]\n{content.body}")
    if content.metadata:
        console.print(f"\n[bold]Metadata:[/bold] {content.metadata}")
