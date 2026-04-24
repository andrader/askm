import shutil
from pathlib import Path

import typer
from rich import print

from ..config import (
    get_all_harnesses,
    get_config,
    get_scope_dir,
    skills_lock_session,
)
from ..context import verbose_state
from ..core.filesystem import rel_home


def remove_skill(
    target: str = typer.Argument(..., help="Skill name or repository (owner/repo)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    verbose: bool = False,
):
    """
    Remove a skill or all skills from a repository.

    Aliases: rm, uninstall
    """
    verbose_state.verbose = verbose
    if not yes:
        typer.confirm(f"Are you sure you want to remove {target}?", abort=True)

    config = get_config()
    with skills_lock_session(config) as lock:
        repo_to_remove = None
        skill_to_remove = None

        if target in lock.sources:
            repo_to_remove = target
        else:
            maybe_local_target = Path(target).expanduser()
            if maybe_local_target.exists():
                resolved_target = str(maybe_local_target.resolve())
                if resolved_target in lock.sources:
                    repo_to_remove = resolved_target

            # Search for skill name
            if not repo_to_remove:
                for repo, source in lock.sources.items():
                    if target in source.skills:
                        skill_to_remove = target
                        repo_to_remove = repo
                        break

        if not repo_to_remove:
            print(f"[red]Could not find {target} in installed skills.[/red]")
            raise typer.Exit(code=1)

        source = lock.sources[repo_to_remove]

        # Remove symlinks/directories for this skill/repo from all targets
        targets = []
        scope_dir = get_scope_dir(config)
        default_skills_dir = scope_dir
        targets.append(default_skills_dir)
        all_harnesses = get_all_harnesses(config)
        for harness_name in config.harnesses:
            if harness_name in all_harnesses:
                harness = all_harnesses[harness_name]
                loc = (
                    harness.local_location
                    if config.scope == "local"
                    else harness.global_location
                )
                targets.append(Path(loc).expanduser().resolve())

        removed_skills = []
        if skill_to_remove:
            # Remove only the specific skill
            for t in targets:
                skill_path = t / skill_to_remove
                if skill_path.exists() or skill_path.is_symlink():
                    if skill_path.is_symlink() or skill_path.is_file():
                        skill_path.unlink()
                    elif skill_path.is_dir():
                        shutil.rmtree(skill_path)
                    if verbose_state.verbose:
                        print(f"Removed skill at [red]{rel_home(skill_path)}[/red]")
            source.skills.remove(skill_to_remove)
            removed_skills.append(skill_to_remove)
            print(
                f"🗑️ Removed skill '[yellow]{skill_to_remove}[/yellow]' from {repo_to_remove}"
            )
            if not source.skills:
                del lock.sources[repo_to_remove]
                print(
                    f"No more skills in [yellow]{repo_to_remove}[/yellow], removed repository reference."
                )
        else:
            # Remove all skills from this repo
            for skill in list(source.skills):
                for t in targets:
                    skill_path = t / skill
                    if skill_path.exists() or skill_path.is_symlink():
                        if skill_path.is_symlink() or skill_path.is_file():
                            skill_path.unlink()
                        elif skill_path.is_dir():
                            shutil.rmtree(skill_path)
                        if verbose_state.verbose:
                            print(f"Removed skill at [red]{rel_home(skill_path)}[/red]")
                removed_skills.append(skill)
            del lock.sources[repo_to_remove]
            print(
                f"🗑️ Removed repository '[yellow]{repo_to_remove}[/yellow]' and all its skills."
            )
    print(
        f"Removed {len(removed_skills)} skills from "
        + ", ".join([f"[yellow]{rel_home(t)}[/yellow]" for t in targets])
    )
    # Trigger sync
    from .sync import sync_logic

    sync_logic(verbose=verbose_state.verbose, logger=print)
