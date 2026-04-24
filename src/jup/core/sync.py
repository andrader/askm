import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Callable

from ..config import (
    get_all_harnesses,
    get_config,
    get_scope_dir,
    get_skills_storage_dir,
    skills_lock_session,
)
from ..models import SyncMode, JupConfig, SkillsLock
from .filesystem import rel_home, validate_path
from .constants import GH_PREFIX, GITHUB_SOURCE_TYPE, LOCAL_SOURCE_TYPE
from .git import run_git_pull


def sync_logic(
    update: bool = False,
    verbose: bool = False,
    interactive_callback: Optional[Callable[[List[str]], Optional[List[str]]]] = None,
    custom_dir: Optional[str] = None,
    config: Optional[JupConfig] = None,
    logger: Optional[Callable[[str], None]] = None,
):
    if config is None:
        config = get_config()

    def log(msg: str):
        if logger:
            logger(msg)

    with skills_lock_session(config) as lock:
        return _sync_with_lock(
            lock,
            config,
            update,
            verbose,
            interactive_callback,
            custom_dir,
            log,
        )


def _sync_with_lock(
    lock: SkillsLock,
    config: JupConfig,
    update: bool = False,
    verbose: bool = False,
    interactive_callback: Optional[Callable[[List[str]], Optional[List[str]]]] = None,
    custom_dir: Optional[str] = None,
    log: Optional[Callable[[str], None]] = None,
):
    def _log(msg: str):
        if log:
            log(msg)

    scope_dir = get_scope_dir(config)

    selected_skills = None
    if interactive_callback:
        all_skill_names = []
        for source_key, source in lock.sources.items():
            for skill in source.skills:
                all_skill_names.append(skill)

        if not all_skill_names:
            _log("[yellow]No skills found in lockfile to sync.[/yellow]")
            return

        all_skill_names.sort()
        selected_skills = interactive_callback(all_skill_names)

        if selected_skills is None:
            # User cancelled
            return

        if not selected_skills:
            _log("[yellow]No skills selected. Nothing to sync.[/yellow]")
            return

    # 1. Update GitHub sources if requested
    if update:
        _log("Checking for updates...")
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
                        _log(f"Updating [cyan]{rel_home(storage_dir)}[/cyan]...")
                    try:
                        run_git_pull(storage_dir)
                        updated_count += 1
                        # Update last_updated on successful pull
                        source.last_updated = datetime.now(timezone.utc).isoformat(
                            timespec="seconds"
                        )
                    except Exception:
                        _log(f"[red]Failed to update {rel_home(storage_dir)}[/red]")

        if updated_count > 0:
            _log(f"Updated {updated_count} GitHub sources.")

    # Target directories
    targets = []
    all_harnesses = get_all_harnesses(config)

    if custom_dir:
        targets.append(Path(custom_dir).expanduser().resolve())
    else:
        # Default scope directory
        default_skills_dir = scope_dir
        targets.append(default_skills_dir)

        # Harness directories
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
                _log(
                    f"[yellow]Warning: Unknown harness '{harness_name}'. Skipping.[/yellow]"
                )

    # Deduplicate targets while preserving order (optional, but good for consistent logging)
    seen = set()
    deduped_targets = []
    for t in targets:
        resolved_t = t.resolve()
        if resolved_t not in seen:
            seen.add(resolved_t)
            deduped_targets.append(t)
    targets = deduped_targets

    # Identify directories of inactive harnesses to clean up
    active_target_paths = seen  # already resolved set
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
        try:
            t.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            _log(
                f"[red]Error: Could not create target directory {rel_home(t)}: {e}[/red]"
            )
            continue

    # 1. Clean up managed skills from inactive harnesses and removed skills
    all_managed_skills = set()
    for source in lock.sources.values():
        all_managed_skills.update(source.skills)

    # Clean inactive harnesses
    removed_from_inactive = 0
    for it in inactive_targets:
        for skill in all_managed_skills:
            skill_path = it / skill
            if skill_path.exists() or skill_path.is_symlink():
                try:
                    validate_path(skill_path, it, follow_symlinks=False)
                    # For safety, only remove if matched a managed skill
                    if verbose:
                        _log(
                            f"🧹 Removing [cyan]{skill}[/cyan] from inactive harness [yellow]{rel_home(it)}[/yellow]"
                        )
                    if skill_path.is_symlink() or skill_path.is_file():
                        skill_path.unlink()
                    elif skill_path.is_dir():
                        shutil.rmtree(skill_path)
                    removed_from_inactive += 1
                except ValueError:
                    if verbose:
                        _log(
                            f"⚠️  Skipping potentially unsafe path: [red]{skill_path}[/red]"
                        )
                    continue

    if removed_from_inactive > 0 and verbose:
        _log(
            f"🧹 Cleaned {removed_from_inactive} skills from {len(inactive_targets)} inactive harness directories."
        )

    # 2. Process each skill source
    total_links = 0
    synced_skills = 0
    missing_skills: List[tuple[str, Path]] = []

    for source_key, source in lock.sources.items():
        # Update last_updated on sync
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
                    _log(f"⚠️  Invalid repository reference: [red]{repo_ref}[/red]")
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
                    continue
                if source.source_layout == "single":
                    skill_src_dir = local_source_root
                else:
                    skill_src_dir = local_source_root / skill
            else:
                if storage_dir is None:
                    continue
                skill_src_dir = storage_dir / skill

            if not skill_src_dir.exists():
                missing_skills.append((skill, skill_src_dir))
                if verbose:
                    _log(
                        f"⚠️  Source dir for '[red]{skill}[/red]' missing: [red]{rel_home(skill_src_dir)}[/red]"
                    )
                continue

            synced_skills += 1

            for target_base in targets:
                target_skill_dir = target_base / skill
                try:
                    validate_path(target_skill_dir, target_base, follow_symlinks=False)
                except ValueError:
                    if verbose:
                        _log(
                            f"⚠️  Skipping potentially unsafe path: [red]{target_skill_dir}[/red]"
                        )
                    continue

                # SAFETY CHECK: Don't touch if target is the same as source AND sync mode matches
                if (
                    target_skill_dir.exists()
                    and target_skill_dir.resolve() == skill_src_dir.resolve()
                ):
                    # Only skip if the actual mode matches (is_symlink vs is_dir)
                    current_is_link = target_skill_dir.is_symlink()
                    desired_is_link = config.sync_mode == SyncMode.LINK

                    if current_is_link == desired_is_link:
                        if verbose:
                            _log(
                                f"✅ [green]{skill}[/green] is already at source location [cyan]{rel_home(target_skill_dir)}[/cyan] (mode=[cyan]{config.sync_mode}[/cyan]), skipping."
                            )
                        continue

                # Clean up existing managed target
                if target_skill_dir.exists() or target_skill_dir.is_symlink():
                    try:
                        if verbose:
                            _log(
                                f"🔗 Unlinking [yellow]{rel_home(target_skill_dir)}[/yellow]"
                            )
                        if target_skill_dir.is_symlink():
                            target_skill_dir.unlink()
                        elif target_skill_dir.is_dir():
                            shutil.rmtree(target_skill_dir)
                        else:
                            target_skill_dir.unlink()
                    except Exception as e:
                        if verbose:
                            _log(
                                f"[red]Failed to remove {rel_home(target_skill_dir)}: {e}[/red]"
                            )
                        continue

                try:
                    if config.sync_mode == SyncMode.LINK:
                        if verbose:
                            _log(
                                f"🔗 Linking [cyan]{skill}[/cyan] -> [yellow]{rel_home(target_skill_dir)}[/yellow]"
                            )
                        target_skill_dir.symlink_to(
                            skill_src_dir, target_is_directory=True
                        )
                        total_links += 1
                    else:
                        if verbose:
                            _log(
                                f"📂 Copying [cyan]{skill}[/cyan] -> [yellow]{rel_home(target_skill_dir)}[/yellow]"
                            )
                        shutil.copytree(skill_src_dir, target_skill_dir)
                except Exception as e:
                    _log(
                        f"[red]Error: Could not sync {skill} to {rel_home(target_skill_dir)}: {e}[/red]"
                    )

    if missing_skills and not verbose:
        _log(f"⚠️  Skipped {len(missing_skills)} missing skills from the lockfile.")

    _log(f"🔄 Synced {synced_skills} skills across {len(targets)} locations.")
    if verbose:
        _log(
            f"Added {total_links} symlinks (sync_mode=[cyan]{str(config.sync_mode)}[/cyan])"
        )
    return synced_skills, len(targets), total_links
