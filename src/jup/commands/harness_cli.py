import typer
from typing import Optional
from rich import print
from rich.table import Table
from ..config import get_all_harnesses, get_config, save_config
from ..models import DEFAULT_HARNESSES, HarnessConfig

app = typer.Typer(help="Manage harness providers", no_args_is_help=True)


@app.command("list")
def harness_list():
    """List all available harness providers."""
    config = get_config()
    all_harnesses = get_all_harnesses(config)

    table = Table(title="Harness Providers")
    table.add_column("Name", style="magenta")
    table.add_column("Global Location", style="cyan")
    table.add_column("Local Location", style="cyan")
    table.add_column("Type", style="yellow")

    for name, harness in all_harnesses.items():
        is_default = name in DEFAULT_HARNESSES
        is_customized = name in config.custom_harnesses

        if is_default:
            harness_type = "[yellow]customized[/yellow]" if is_customized else "default"
        else:
            harness_type = "custom"

        table.add_row(
            name, harness.global_location, harness.local_location, harness_type
        )
    print(table)


@app.command("add")
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


@app.command("edit")
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


@app.command("remove")
def harness_remove(name: str = typer.Argument(..., help="Harness name")):
    """Remove a custom harness provider."""
    config = get_config()
    if name not in config.custom_harnesses:
        if name in DEFAULT_HARNESSES:
            print(
                f"[red]Cannot remove default harness '{name}' (it is not currently customized).[/red]"
            )
        else:
            print(f"[red]Custom harness '{name}' does not exist.[/red]")
        raise typer.Exit(code=1)

    del config.custom_harnesses[name]
    save_config(config)
    print(
        f"Removed custom harness provider: [magenta]{name}[/magenta] (reverted to default if applicable)"
    )
