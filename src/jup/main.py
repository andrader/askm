import typer
from importlib.metadata import version as get_version
from rich import print
from .core.constants import BANNER


def version_callback(value: bool):
    """Callback to show the version of the application."""
    if value:
        print(BANNER)
        try:
            v = get_version("jup")
        except Exception:
            v = "unknown"
        print(f"[bold]jup[/bold] version: [magenta]{v}[/magenta]")
        raise typer.Exit()


app = typer.Typer(
    help="jup - Agent Skills Manager",
    no_args_is_help=False,
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """jup - Agent Skills Manager"""
    if ctx.invoked_subcommand is None:
        print(BANNER)
        print("[bold]jup - Agent Skills Manager[/bold]")
        print()
        print(ctx.get_help())
        raise typer.Exit()


from .commands.config_cli import app as config_app  # noqa: E402
from .commands.harness_cli import app as harness_app  # noqa: E402

app.add_typer(config_app, name="config")

harness_help = harness_app.info.help or ""
harness_aliases = ["agent", "agents"]
harness_alias_str = f" [dim](aliases: {', '.join(harness_aliases)})[/dim]"
app.add_typer(harness_app, name="harness", help=harness_help + harness_alias_str)
for alias in harness_aliases:
    app.add_typer(harness_app, name=alias, hidden=True)


# Import command registrations after app and shared state are defined.
from .commands.add import add_skill  # noqa: E402
from .commands.remove import remove_skill  # noqa: E402
from .commands.sync import sync_skills, up_shortcut  # noqa: E402
from .commands.list import list_skills  # noqa: E402
from .commands.show import show_skill  # noqa: E402
from .commands.find import find_skills  # noqa: E402
from .commands.mv import move_skill  # noqa: E402
from .commands.tui import tui_command  # noqa: E402

# Command registration with aliases
COMMANDS = {
    "add": (add_skill, ["install"]),
    "remove": (remove_skill, ["rm", "uninstall"]),
    "sync": (sync_skills, []),
    "update": (up_shortcut, ["up"]),
    "list": (list_skills, ["ls"]),
    "show": (show_skill, []),
    "find": (find_skills, []),
    "move": (move_skill, ["mv"]),
    "tui": (tui_command, ["ui"]),
}

for main_name, (func, aliases) in COMMANDS.items():
    help_str = func.__doc__ or ""
    if aliases:
        # Get the first non-empty line of the docstring for the command help summary.
        lines = [line.strip() for line in help_str.split("\n") if line.strip()]
        first_line = lines[0] if lines else ""
        alias_str = f" [dim](aliases: {', '.join(aliases)})[/dim]"
        app.command(main_name, help=first_line + alias_str)(func)
    else:
        app.command(main_name)(func)

    for alias in aliases:
        app.command(alias, hidden=True)(func)


def main():
    app()


if __name__ == "__main__":
    main()
