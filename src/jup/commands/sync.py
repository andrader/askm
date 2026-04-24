import typer
from rich import print
from prompt_toolkit.shortcuts import checkboxlist_dialog
from typing import Annotated, Optional, List

from ..context import verbose_state
from ..core.sync import sync_logic


def sync_skills(
    update: Annotated[
        bool,
        typer.Option("--update", "-u", help="Update GitHub sources before syncing"),
    ] = False,
    interactive: Annotated[
        bool,
        typer.Option(
            "--interactive", "-i", help="Select which skills to sync interactively"
        ),
    ] = False,
    verbose: bool = False,
    custom_dir: Optional[str] = None,
):
    """
    Update all links/copies in default-lib and for other harnesses.

    Aliases: up (sync --update)
    """
    verbose_state.verbose = verbose

    def interactive_callback(all_skills: List[str]) -> Optional[List[str]]:
        values = [(s, s) for s in all_skills]
        return checkboxlist_dialog(
            title="Interactive Sync",
            text="Select skills to sync (Space to toggle, Enter to confirm):",
            values=values,
            default_values=all_skills,
        ).run()

    sync_logic(
        update=update,
        verbose=verbose,
        interactive_callback=interactive_callback if interactive else None,
        custom_dir=custom_dir,
        logger=print,
    )


def up_shortcut(verbose: bool = False):
    """
    Shortcut for jup sync --update

    Aliases: up
    """
    verbose_state.verbose = verbose
    sync_logic(update=True, verbose=verbose)
