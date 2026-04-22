import typer
from importlib.metadata import version as get_version
from rich import print


BANNER = r"""
[cyan]   _             [/cyan]
[cyan]  ([/cyan][magenta]●[/magenta][cyan])_   _ _ __  [/cyan]
[cyan]  | | | | | '_ \ [/cyan]
[cyan]  | | |_| | |_) |[/cyan]
[cyan] _/ |\__,_| .__/ [/cyan]
[cyan]|__/      |_|    [/cyan]
"""


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
app.add_typer(harness_app, name="harness")
app.add_typer(harness_app, name="agent", hidden=True)
app.add_typer(harness_app, name="agents", hidden=True)


# Import command registrations after app and shared state are defined.
from .commands.add import add_skill  # noqa: E402
from .commands.remove import remove_skill  # noqa: E402
from .commands.sync import sync_skills, up_shortcut  # noqa: E402
from .commands.list import list_skills  # noqa: E402
from .commands.show import show_skill  # noqa: E402
from .commands.find import find_skills  # noqa: E402
from .commands.mv import move_skill  # noqa: E402

app.command("add")(add_skill)
app.command("install", hidden=True)(add_skill)
app.command("remove")(remove_skill)
app.command("rm", hidden=True)(remove_skill)
app.command("uninstall", hidden=True)(remove_skill)
app.command("sync")(sync_skills)
app.command("up", hidden=True)(up_shortcut)
app.command("list")(list_skills)
app.command("ls", hidden=True)(list_skills)
app.command("show")(show_skill)
app.command("find")(find_skills)
app.command("mv")(move_skill)


def main():
    app()


if __name__ == "__main__":
    main()
