"""Template loading and rendering with Jinja2."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

# Default templates directory (shipped with package)
_DEFAULT_TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates"


def get_template_dir(custom_dir: str | None = None) -> Path:
    """Get the templates directory path."""
    if custom_dir:
        return Path(custom_dir)
    return _DEFAULT_TEMPLATE_DIR


def list_templates(custom_dir: str | None = None) -> list[str]:
    """List available template names."""
    template_dir = get_template_dir(custom_dir)
    if not template_dir.exists():
        return []
    return [f.stem for f in template_dir.glob("*.md")]


def render_template(
    name: str,
    variables: dict | None = None,
    custom_dir: str | None = None,
) -> str:
    """Render a template with the given variables."""
    template_dir = get_template_dir(custom_dir)
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape([]),
        keep_trailing_newline=True,
    )
    template = env.get_template(f"{name}.md")
    return template.render(**(variables or {}))


def show_template(name: str, custom_dir: str | None = None) -> str:
    """Return raw template content."""
    template_dir = get_template_dir(custom_dir)
    path = template_dir / f"{name}.md"
    return path.read_text()
