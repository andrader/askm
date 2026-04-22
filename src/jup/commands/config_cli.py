import typer
from rich import print
from rich.table import Table
from enum import Enum
from ..config import get_config, save_config
from ..models import JupConfig, ScopeType, SyncMode

app = typer.Typer(help="Manage configuration settings", no_args_is_help=True)


@app.command("show", short_help="Show all config values")
def config_show():
    """Display all configuration values."""
    config = get_config()

    table = Table(title="Current Configuration")
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    for key in JupConfig.model_fields:
        if key == "custom_harnesses":
            continue
        value = getattr(config, key)
        if isinstance(value, list):
            value_str = ", ".join(value) if value else "none"
        elif hasattr(value, "value"):
            value_str = value.value
        else:
            value_str = str(value)
        table.add_row(key, value_str)
    print(table)


@app.command("get", short_help="Get a config value", no_args_is_help=True)
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


@app.command("set", short_help="Set a config value", no_args_is_help=True)
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


@app.command(
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
        config.scope = ScopeType.USER
    elif norm_key == "harnesses":
        config.harnesses = []
    elif norm_key == "sync_mode":
        config.sync_mode = SyncMode.LINK
    else:
        print(f"[red]Unknown config key: {key}[/red]")
        raise typer.Exit(code=1)
    save_config(config)
    print(f"Unset {key} (reverted to default)")
