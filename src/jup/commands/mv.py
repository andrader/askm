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
    new_destination: str = typer.Argument(
        ..., help="New category or filesystem path for the skill"
    ),
    verbose: bool = False,
):
    """Move a skill or repository to a new category or filesystem path."""
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
    source_type = source.source_type or GITHUB_SOURCE_TYPE

    # Determine if new_destination is a path or a category
    is_path = "/" in new_destination or new_destination.startswith(".")
    new_category = old_category if is_path else new_destination

    if not is_path and old_category == new_category and not source.source_path:
        print(f"Skill is already in category '[cyan]{new_category}[/cyan]'.")
        return

    if source_type == GITHUB_SOURCE_TYPE:
        storage_base = get_skills_storage_dir()
        repo_ref = source.repo or repo_key
        if "/" not in repo_ref:
            print(f"[red]Invalid repository reference: {repo_ref}[/red]")
            raise typer.Exit(code=1)

        owner, repo_name = repo_ref.split("/", 1)

        if source.source_path:
            old_dir = Path(source.source_path).expanduser().resolve()
        else:
            old_dir = storage_base / old_category / GH_PREFIX / owner / repo_name

        if is_path:
            new_dir = Path(new_destination).expanduser().resolve()
            # If it's a directory that already exists and doesn't look like the repo name,
            # maybe we should append the repo name?
            # But the user might want to move it TO that exact path.
            # Standard 'mv' behavior: if dest is a dir, move src INTO it.
            if new_dir.is_dir():
                new_dir = new_dir / repo_name
        else:
            new_dir = storage_base / new_category / GH_PREFIX / owner / repo_name

        if old_dir.exists():
            if old_dir.resolve() == new_dir.resolve():
                print(f"Skill is already at [cyan]{rel_home(new_dir)}[/cyan].")
                return

            if new_dir.exists():
                print(
                    f"[yellow]Warning: Target directory {rel_home(new_dir)} already exists. Overwriting...[/yellow]"
                )
                if new_dir.is_dir():
                    shutil.rmtree(new_dir)
                else:
                    new_dir.unlink()

            new_dir.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_dir), str(new_dir))
            if verbose:
                print(
                    f"Moved [cyan]{rel_home(old_dir)}[/cyan] to [cyan]{rel_home(new_dir)}[/cyan]"
                )
        else:
            print(
                f"[yellow]Warning: Source directory {rel_home(old_dir)} not found. Only updating lockfile.[/yellow]"
            )

        # Update source_path: if it's in the default storage, we can keep it None or update it.
        # If it's a custom path, we MUST set it.
        if is_path:
            source.source_path = str(new_dir)
        else:
            # If moving back to a category, clear source_path to use default logic
            source.source_path = None

    # Update lockfile
    source.category = new_category
    save_skills_lock(config, lock)

    if is_path:
        print(
            f"✅ Moved [magenta]{target}[/magenta] to [green]{rel_home(Path(new_destination).expanduser())}[/green]"
        )
    else:
        print(
            f"✅ Moved [magenta]{target}[/magenta] from [yellow]{old_category}[/yellow] to [green]{new_category}[/green]"
        )

    # Trigger sync to update symlinks
    from .sync import sync_skills

    sync_skills(verbose=verbose_state.verbose)
