import shutil
from pathlib import Path

import typer
from rich import print

from ..config import (
    get_config,
    get_skills_lock,
    get_skills_storage_dir,
    save_skills_lock,
)
from ..main import app, verbose_state
from .utils import GH_PREFIX, GITHUB_SOURCE_TYPE, rel_home


@app.command("mv")
def move_skill(
    target: str = typer.Argument(..., help="Skill name or repository (owner/repo)"),
    new_category: str = typer.Argument(..., help="New category for the skill"),
    verbose: bool = False,
):
    """Move a skill or repository to a new category."""
    verbose_state.verbose = verbose
    config = get_config()
    lock = get_skills_lock(config)

    repo_key = None
    if target in lock.sources:
        repo_key = target
    else:
        # Search for skill name
        for r, source in lock.sources.items():
            if target in source.skills:
                repo_key = r
                break

        if not repo_key:
            # Check for local path
            maybe_local = Path(target).expanduser()
            if maybe_local.exists():
                resolved = str(maybe_local.resolve())
                if resolved in lock.sources:
                    repo_key = resolved

    if not repo_key:
        print(f"[red]Could not find '{target}' in installed skills.[/red]")
        raise typer.Exit(code=1)

    source = lock.sources[repo_key]
    old_category = source.category or "misc"

    if old_category == new_category:
        print(f"Skill is already in category '[cyan]{new_category}[/cyan]'.")
        return

    source_type = source.source_type or GITHUB_SOURCE_TYPE

    if source_type == GITHUB_SOURCE_TYPE:
        storage_base = get_skills_storage_dir()
        repo_ref = source.repo or repo_key
        if "/" not in repo_ref:
            print(f"[red]Invalid repository reference: {repo_ref}[/red]")
            raise typer.Exit(code=1)

        owner, repo_name = repo_ref.split("/", 1)

        old_dir = storage_base / old_category / GH_PREFIX / owner / repo_name
        new_dir = storage_base / new_category / GH_PREFIX / owner / repo_name

        if old_dir.exists():
            if new_dir.exists():
                print(
                    f"[yellow]Warning: Target directory {rel_home(new_dir)} already exists. Overwriting...[/yellow]"
                )
                shutil.rmtree(new_dir)

            new_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(old_dir, new_dir)
            if verbose:
                print(
                    f"Moved [cyan]{rel_home(old_dir)}[/cyan] to [cyan]{rel_home(new_dir)}[/cyan]"
                )
        else:
            print(
                f"[yellow]Warning: Source directory {rel_home(old_dir)} not found. Only updating lockfile.[/yellow]"
            )

    # Update lockfile
    source.category = new_category
    save_skills_lock(config, lock)

    print(
        f"✅ Moved [magenta]{target}[/magenta] from [yellow]{old_category}[/yellow] to [green]{new_category}[/green]"
    )

    # Trigger sync to update symlinks (since source paths changed for GitHub skills)
    from . import sync_skills

    sync_skills(verbose=verbose_state.verbose)
