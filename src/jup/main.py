import typer
from typing import Optional
from importlib.metadata import version as get_version
from enum import Enum
from rich import print
from .config import get_all_harnesses, get_config, save_config
from .models import DEFAULT_HARNESSES, HarnessConfig, JupConfig, ScopeType, SyncMode


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
    key: str = typer.Argument(
        ..., help="Config key to get (scope, harnesses, sync-mode)"
    ),
):
    config = get_config()
    # Normalize key
    normalize_key_map = {"sync-mode": "sync_mode", "agents": "harnesses"}
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
    key_map = {
        "sync-mode": "sync_mode",
        "sync_mode": "sync_mode",
        "agents": "harnesses",
    }
    norm_key = key_map.get(key, key)
    if norm_key not in JupConfig.model_fields:
        print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(code=1)
    value = value.strip()
    try:
        if norm_key == "scope":
            config.scope = ScopeType(value)
        elif norm_key == "harnesses":
            config.harnesses = (
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
    key_map = {
        "sync-mode": "sync_mode",
        "sync_mode": "sync_mode",
        "agents": "harnesses",
    }
    norm_key = key_map.get(key, key)
    if norm_key == "scope":
        config.scope = ScopeType.GLOBAL
    elif norm_key == "harnesses":
        config.harnesses = []
    elif norm_key == "sync_mode":
        config.sync_mode = SyncMode.LINK
    else:
        print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(code=1)
    save_config(config)
    print(f"Unset {key} (reverted to default)")


harness_app = typer.Typer(help="Manage harness providers", no_args_is_help=True)
app.add_typer(harness_app, name="harness")


@harness_app.command("list")
def harness_list():
    """List all available harness providers."""
    config = get_config()
    all_harnesses = get_all_harnesses(config)
    from rich.table import Table

    table = Table(title="Harness Providers")
    table.add_column("Name", style="magenta")
    table.add_column("Global Location", style="cyan")
    table.add_column("Local Location", style="cyan")
    table.add_column("Type", style="yellow")

    for name, harness in all_harnesses.items():
        harness_type = "default" if name in DEFAULT_HARNESSES else "custom"
        table.add_row(
            name, harness.global_location, harness.local_location, harness_type
        )
    print(table)


@harness_app.command("add")
def harness_add(
    name: str = typer.Argument(..., help="Harness name"),
    global_location: str = typer.Option(
        ...,
        "--global-location",
        "-g",
        help="Global skills directory",
        prompt="Global skills directory (e.g. ~/.gemini/skills)",
    ),
    local_location: str = typer.Option(
        ...,
        "--local-location",
        "-l",
        help="Local skills directory",
        prompt="Local skills directory (e.g. ./.gemini/skills)",
    ),
):
    """Add a new custom harness provider."""
    config = get_config()
    all_harnesses = get_all_harnesses(config)
    if name in all_harnesses:
        print(f"[red]Harness '{name}' already exists.[/red]")
        raise typer.Exit(code=1)

    harness = HarnessConfig(
        name=name, global_location=global_location, local_location=local_location
    )
    config.custom_harnesses[name] = harness
    save_config(config)
    print(f"Added custom harness provider: [magenta]{name}[/magenta]")


@harness_app.command("edit")
def harness_edit(
    name: str = typer.Argument(..., help="Harness name"),
    global_location: Optional[str] = typer.Option(
        None, "--global-location", "-g", help="Global skills directory"
    ),
    local_location: Optional[str] = typer.Option(
        None, "--local-location", "-l", help="Local skills directory"
    ),
):
    """Edit an existing custom harness provider."""
    config = get_config()
    if name in DEFAULT_HARNESSES:
        print(f"[red]Cannot edit default harness '{name}'.[/red]")
        raise typer.Exit(code=1)
    if name not in config.custom_harnesses:
        print(f"[red]Custom harness '{name}' does not exist.[/red]")
        raise typer.Exit(code=1)

    harness = config.custom_harnesses[name]
    if global_location is not None:
        harness.global_location = global_location
    if local_location is not None:
        harness.local_location = local_location

    config.custom_harnesses[name] = harness
    save_config(config)
    print(f"Updated custom harness provider: [magenta]{name}[/magenta]")


@harness_app.command("remove")
def harness_remove(name: str = typer.Argument(..., help="Harness name")):
    """Remove a custom harness provider."""
    config = get_config()
    if name in DEFAULT_HARNESSES:
        print(f"[red]Cannot remove default harness '{name}'.[/red]")
        raise typer.Exit(code=1)
    if name not in config.custom_harnesses:
        print(f"[red]Custom harness '{name}' does not exist.[/red]")
        raise typer.Exit(code=1)

    del config.custom_harnesses[name]
    save_config(config)
    print(f"Removed custom harness provider: [magenta]{name}[/magenta]")


# Import command registrations after app and shared state are defined.
from . import commands  # noqa: E402,F401


def main():
    app()


if __name__ == "__main__":
    main()
