from enum import Enum

import typer
from rich import print
from .config import get_config, save_config
from .models import SyncMode, ScopeType, JupConfig



class VerboseState:
    verbose: bool = False

verbose_state = VerboseState()



app = typer.Typer(help="jup - Agent Skills Manager", no_args_is_help=True, context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
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
def config_get(key: str = typer.Argument(..., help="Config key to get (scope, agents, sync-mode)")):
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
    value: str = typer.Argument(..., help="Value to set")
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
            config.agents = [v.strip() for v in value.split(",")] if value.lower() != "none" else []
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

@config_app.command("unset", short_help="Unset a config value (revert to default)", no_args_is_help=True)
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
