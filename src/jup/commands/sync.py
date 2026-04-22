from typing import Annotated, Optional

import typer

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
    """Update all links/copies in default-lib and for other harnesses."""
    verbose_state.verbose = verbose
    # We cannot pass config here directly from CLI, it is meant for internal calls via sync_logic
    sync_logic(
        update=update, verbose=verbose, interactive=interactive, custom_dir=custom_dir
    )


def up_shortcut(verbose: bool = False):
    """Shortcut for jup sync --update"""
    verbose_state.verbose = verbose
    sync_logic(update=True, verbose=verbose)
