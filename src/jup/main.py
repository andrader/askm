import typer
from importlib.metadata import version as get_version
from enum import Enum
from rich import print
from .config import get_config, save_config
from .models import SyncMode, ScopeType, JupConfig


class VerboseState:
    verbose: bool = False


verbose_state = VerboseState()


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


config_app = typer.Typer(help="Manage configuration settings", no_args_is_help=True)
app.add_typer(config_app, name="config")


# Show all config values
@config_app.command("show", short_help="Show all config values")
def config_show():
    """Display all configuration values."""
    config = get_config()
    from rich.table import Table

    table = Table(title="Current Configuration")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    for key in JupConfig.model_fields:
        value = getattr(config, key)
        if isinstance(value, list):
            value_str = ", ".join(value) if value else "none"
        elif hasattr(value, "value"):
            value_str = value.value
        else:
            value_str = str(value)
        table.add_row(key, value_str)
    print(table)


@config_app.command("get", short_help="Get a config value", no_args_is_help=True)
def config_get(
    key: str = typer.Argument(..., help="Config key to get (scope, agents, sync-mode)"),
):
    config = get_config()
    # Normalize key
    normalize_key_map = {"sync-mode": "sync_mode"}
    norm_key = normalize_key_map.get(key, key)

    if norm_key in JupConfig.model_fields:
        value = getattr(config, norm_key)
        if isinstance(value, list):
            print(",".join(value) if value else "none")
        else:
            print(value.value if isinstance(value, Enum) else value)
    else:
        print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(code=1)


@config_app.command("set", short_help="Set a config value", no_args_is_help=True)
def config_set(
    key: str = typer.Argument(..., help="Config key to set"),
    value: str = typer.Argument(..., help="Value to set"),
):
    config = get_config()
    # Normalize key
    key_map = {"sync-mode": "sync_mode", "sync_mode": "sync_mode"}
    norm_key = key_map.get(key, key)
    if norm_key not in JupConfig.model_fields:
        print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(code=1)
    value = value.strip()
    try:
        if norm_key == "scope":
            config.scope = ScopeType(value)
        elif norm_key == "agents":
            config.agents = (
                [v.strip() for v in value.split(",")] if value.lower() != "none" else []
            )
        elif norm_key == "sync_mode":
            config.sync_mode = SyncMode(value)
        else:
            print(f"[red]Unknown config key: {key}[/red]")
            raise typer.Exit(code=1)
        save_config(config)
        print(f"Set {key} to {value}")
    except ValueError:
        print(f"[red]Invalid value for {key}: {value}[/red]")
        raise typer.Exit(code=1)


@config_app.command(
    "unset", short_help="Unset a config value (revert to default)", no_args_is_help=True
)
def config_unset(key: str = typer.Argument(..., help="Config key to unset")):
    config = get_config()
    key_map = {"sync-mode": "sync_mode", "sync_mode": "sync_mode"}
    norm_key = key_map.get(key, key)
    if norm_key == "scope":
        config.scope = ScopeType.GLOBAL
    elif norm_key == "agents":
        config.agents = []
    elif norm_key == "sync_mode":
        config.sync_mode = SyncMode.LINK
    else:
        print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(code=1)
    save_config(config)
    print(f"Unset {key} (reverted to default)")


# Import command registrations after app and shared state are defined.
from . import commands  # noqa: E402,F401


def main():
    app()


if __name__ == "__main__":
    main()
