"""CLI application root."""

import typer

from promotion_agent.cli.commands.auth import auth_app
from promotion_agent.cli.commands.config_cmd import config_app
from promotion_agent.cli.commands.platforms import platforms_app
from promotion_agent.cli.commands.post import post_command
from promotion_agent.cli.commands.templates import templates_app

app = typer.Typer(
    name="promote",
    help="Promote AI projects to social media platforms.",
    no_args_is_help=True,
)

app.command("post")(post_command)
app.add_typer(auth_app, name="auth")
app.add_typer(platforms_app, name="platforms")
app.add_typer(templates_app, name="templates")
app.add_typer(config_app, name="config")

if __name__ == "__main__":
    app()
