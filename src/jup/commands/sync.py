import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional

import typer
from prompt_toolkit.shortcuts import checkboxlist_dialog
from rich import print

from ..config import (
    get_all_harnesses,
    get_config,
    get_scope_dir,
    get_skills_lock,
    get_skills_storage_dir,
)
from ..main import app, verbose_state
from ..models import SyncMode, JupConfig
from .utils import (
    GH_PREFIX,
    GITHUB_SOURCE_TYPE,
    LOCAL_SOURCE_TYPE,
    rel_home,
    run_git_pull,
)


@app.command("sync")
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


@app.command("up", hidden=True)
def up_shortcut(verbose: bool = False):
    """Shortcut for jup sync --update"""
    verbose_state.verbose = verbose
    sync_logic(update=True, verbose=verbose)


def sync_logic(
    update: bool = False,
    verbose: bool = False,
    interactive: bool = False,
    custom_dir: Optional[str] = None,
    config: Optional[JupConfig] = None,
):
    if config is None:
        config = get_config()
    lock = get_skills_lock(config)
    scope_dir = get_scope_dir(config)

    selected_skills = None
    if interactive:
        all_skills = []
        for source_key, source in lock.sources.items():
            for skill in source.skills:
                all_skills.append((skill, skill))

        if not all_skills:
            print("[yellow]No skills found in lockfile to sync.[/yellow]")
            return

        # Sort for better UI
        all_skills.sort()

        selected_skills = checkboxlist_dialog(
            title="Interactive Sync",
            text="Select skills to sync (Space to toggle, Enter to confirm):",
            values=all_skills,
            default_values=[s[0] for s in all_skills],
        ).run()

        if selected_skills is None:
            # User cancelled
            return

        if not selected_skills:
            print("[yellow]No skills selected. Nothing to sync.[/yellow]")
            return

    # 1. Update GitHub sources if requested
    if update:
        print("Checking for updates...")
        updated_count = 0
        for source_key, source in lock.sources.items():
            # If interactive, only update sources that have selected skills
            if selected_skills is not None:
                if not any(s in selected_skills for s in source.skills):
                    continue

            source_type = source.source_type or GITHUB_SOURCE_TYPE
            if source_type == GITHUB_SOURCE_TYPE:
                if source.source_path:
                    storage_dir = Path(source.source_path).expanduser().resolve()
                else:
                    repo_ref = source.repo or source_key
                    if "/" not in repo_ref:
                        continue
                    owner, repo_name = repo_ref.split("/", 1)
                    storage_dir = (
                        get_skills_storage_dir()
                        / str(source.category or "misc")
                        / GH_PREFIX
                        / owner
                        / repo_name
                    )

                if storage_dir.exists() and (storage_dir / ".git").exists():
                    if verbose:
                        print(f"Updating [cyan]{rel_home(storage_dir)}[/cyan]...")
                    try:
                        run_git_pull(storage_dir)
                        updated_count += 1
                        # Update last_updated on successful pull
                        source.last_updated = datetime.now(timezone.utc).isoformat(
                            timespec="seconds"
                        )
                    except Exception:
                        print(f"[red]Failed to update {rel_home(storage_dir)}[/red]")

        if updated_count > 0:
            from ..config import save_skills_lock

            save_skills_lock(config, lock)
            print(f"Updated {updated_count} GitHub sources.")

    # Target directories
    targets = []

    # Default scope directory
    default_skills_dir = scope_dir
    targets.append(default_skills_dir)

    # Harness directories
    all_harnesses = get_all_harnesses(config)
    for harness_name in config.harnesses:
        if harness_name in all_harnesses:
            harness = all_harnesses[harness_name]
            # Use global/local location based on scope
            loc = (
                harness.local_location
                if config.scope == "local"
                else harness.global_location
            )
            targets.append(Path(loc).expanduser().resolve())
        else:
            print(
                f"[yellow]Warning: Unknown harness '{harness_name}'. Skipping.[/yellow]"
            )

    # Identify directories of inactive harnesses to clean up
    active_target_paths = {t.resolve() for t in targets}
    inactive_targets = []
    for harness_name, harness in all_harnesses.items():
        loc = (
            harness.local_location
            if config.scope == "local"
            else harness.global_location
        )
        p = Path(loc).expanduser().resolve()
        if p.exists() and p.resolve() not in active_target_paths:
            inactive_targets.append(p)

    # Ensure active target directories exist
    for t in targets:
        t.mkdir(parents=True, exist_ok=True)

    # We only overwrite skills managed by our lockfile
    # to avoid blowing away user's manual skills.

    # 1. Clean up managed skills from inactive harnesses and removed skills
    # Collect all skills that SHOULD exist
    all_managed_skills = set()
    for source in lock.sources.values():
        all_managed_skills.update(source.skills)

    # Clean inactive harnesses
    removed_from_inactive = 0
    for it in inactive_targets:
        for skill in all_managed_skills:
            skill_path = it / skill
            if skill_path.exists() or skill_path.is_symlink():
                # We only remove it if it's a symlink (our default) or if we're sure it's ours.
                # For now, being aggressive and removing it if it matches a managed skill name.
                if skill_path.is_symlink() or skill_path.is_file():
                    skill_path.unlink()
                elif skill_path.is_dir():
                    shutil.rmtree(skill_path)
                removed_from_inactive += 1

    if removed_from_inactive > 0 and verbose_state.verbose:
        print(
            f"🧹 Cleaned {removed_from_inactive} skills from {len(inactive_targets)} inactive harness directories."
        )

    # 2. Process each skill source
    total_links = 0
    synced_skills = 0
    missing_skills: list[tuple[str, Path]] = []

    for source_key, source in lock.sources.items():
        # Update last_updated on sync (update)
        source.last_updated = datetime.now(timezone.utc).isoformat(timespec="seconds")

        source_type = source.source_type or GITHUB_SOURCE_TYPE
        storage_dir: Path | None = None
        local_source_root: Path | None = None

        if source_type == LOCAL_SOURCE_TYPE:
            local_path_str = source.source_path or source_key
            local_source_root = Path(local_path_str).expanduser().resolve()
        else:
            if source.source_path:
                storage_dir = Path(source.source_path).expanduser().resolve()
            else:
                repo_ref = source.repo or source_key
                if "/" not in repo_ref:
                    print(f"⚠️  Invalid repository reference: [red]{repo_ref}[/red]")
                    continue
                owner, repo_name = repo_ref.split("/", 1)
                storage_dir = (
                    get_skills_storage_dir()
                    / str(source.category or "misc")
                    / GH_PREFIX
                    / owner
                    / repo_name
                )

        for skill in source.skills:
            if selected_skills is not None and skill not in selected_skills:
                continue

            if source_type == LOCAL_SOURCE_TYPE:
                if local_source_root is None:
                    print(f"⚠️  Invalid local source path for [red]{source_key}[/red].")
                    continue
                if source.source_layout == "single":
                    skill_src_dir = local_source_root
                else:
                    skill_src_dir = local_source_root / skill
            else:
                if storage_dir is None:
                    print(f"⚠️  Invalid storage directory for [red]{source_key}[/red].")
                    continue
                skill_src_dir = storage_dir / skill

            if not skill_src_dir.exists():
                missing_skills.append((skill, skill_src_dir))
                if verbose_state.verbose:
                    print(
                        f"⚠️  Source dir for '[red]{skill}[/red]' missing: [red]{rel_home(skill_src_dir)}[/red]"
                    )
                continue

            synced_skills += 1

            for target_base in targets:
                target_skill_dir = target_base / skill

                # SAFETY CHECK: Don't touch if target is the same as source
                if (
                    target_skill_dir.exists()
                    and target_skill_dir.resolve() == skill_src_dir.resolve()
                ):
                    if verbose_state.verbose:
                        print(
                            f"✅ [green]{skill}[/green] is already at source location [cyan]{rel_home(target_skill_dir)}[/cyan], skipping."
                        )
                    continue

                # Clean up existing managed target
                if target_skill_dir.exists() or target_skill_dir.is_symlink():
                    if target_skill_dir.is_symlink():
                        target_skill_dir.unlink()
                        if verbose_state.verbose:
                            print(
                                f"Removed old symlink [magenta]{rel_home(target_skill_dir)}[/magenta]"
                            )
                    elif target_skill_dir.is_dir():
                        shutil.rmtree(target_skill_dir)
                        if verbose_state.verbose:
                            print(
                                f"Removed old directory [magenta]{rel_home(target_skill_dir)}[/magenta]"
                            )
                    else:
                        target_skill_dir.unlink()
                        if verbose_state.verbose:
                            print(
                                f"Removed old file [magenta]{rel_home(target_skill_dir)}[/magenta]"
                            )

                if config.sync_mode == SyncMode.LINK:
                    target_skill_dir.symlink_to(skill_src_dir, target_is_directory=True)
                    total_links += 1
                    if verbose_state.verbose:
                        print(
                            f"🔗 Linked [cyan]{rel_home(target_skill_dir)}[/cyan] -> [cyan]{rel_home(skill_src_dir)}[/cyan]"
                        )
                else:
                    shutil.copytree(skill_src_dir, target_skill_dir)
                    if verbose_state.verbose:
                        print(
                            f"📁 Copied [cyan]{rel_home(skill_src_dir)}[/cyan] -> [cyan]{rel_home(target_skill_dir)}[/cyan]"
                        )

    if missing_skills and not verbose_state.verbose:
        print(f"⚠️  Skipped {len(missing_skills)} missing skills from the lockfile.")

    print(f"🔄 Synced {synced_skills} skills across {len(targets)} locations.")
    if verbose_state.verbose:
        print(
            f"Added {total_links} symlinks (sync_mode=[cyan]{str(config.sync_mode)}[/cyan])"
        )
