import shutil
import subprocess
import tempfile
from pathlib import Path
import typer
from rich import print

from .main import app, verbose_state
from .config import (
    get_config,
    get_skills_lock,
    save_skills_lock,
    get_skills_storage_dir,
    get_scope_dir,
)
from .models import SkillSource, SyncMode, DEFAULT_AGENTS


GH_PREFIX = "gh"  # Used to namespace GitHub sources in storage
LOCAL_SOURCE_TYPE = "local"
GITHUB_SOURCE_TYPE = "github"


def rel_home(p):
    return str(p).replace(str(Path.home()), "~")


def run_git_clone(repo_url: str, dest_dir: Path, **kwargs):
    str_kwargs_flattened = []
    for k, v in kwargs.items():
        if len(k) == 1:
            str_kwargs_flattened.append(f"-{k}")
        elif len(k) > 1:
            str_kwargs_flattened.append(f"--{k.replace('_', '-')}")
        else:
            continue

        if isinstance(v, bool):
            continue  # Flags don't have a value
        str_kwargs_flattened.append(str(v))

    try:
        subprocess.run(
            ["git", "clone", *str_kwargs_flattened, repo_url, str(dest_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"[red]Failed to clone repository: {e.stderr.decode()}[/red]")
        raise typer.Exit(code=1)


@app.command("add")
def add_skill(
    repo: str = typer.Argument(
        ...,
        help="GitHub repository (owner/repo) or local skills directory",
    ),
    category: str = typer.Option(
        "misc", "--category", help="Category for the skill (e.g., productivity/custom)"
    ),
    path: str = typer.Option(
        "skills/", "--path", help="[GitHub only] Path to skills directory in the repo (default: skills/)"
    ),
    skills: str = typer.Option(
        None, "--skills", help="[GitHub only] Comma-separated list of skill names to add (default: all)"
    ),
    verbose: bool = False,
):
    """Install skills from a GitHub repository (optionally using --path/--skills) or a local directory.

    For GitHub sources, you can:
    - Use --path to specify a subdirectory under the repo (default: skills/)
    - Use --skills to select specific skill names (comma-separated) to add from the skills directory
    - Both options are ignored for local sources (paths or directories)
    """
    verbose_state.verbose = verbose
    source_type = GITHUB_SOURCE_TYPE
    source_layout = None
    source_key = repo
    source_display = repo
    found_skills: list[Path] = []
    target_dir: Path | None = None

    local_path = Path(repo).expanduser()
    is_local_source = local_path.exists()

    if is_local_source:
        if not local_path.is_dir():
            print(f"[red]Local source must be a directory: {repo}[/red]")
            raise typer.Exit(code=1)

        resolved_local = local_path.resolve()
        source_type = LOCAL_SOURCE_TYPE
        source_key = str(resolved_local)
        source_display = rel_home(resolved_local)

        if (resolved_local / "SKILL.md").exists():
            source_layout = "single"
            found_skills = [resolved_local]
        else:
            source_layout = "collection"
            for item in resolved_local.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    found_skills.append(item)

        if verbose_state.verbose:
            print(
                f"Found {len(found_skills)} local skills from [cyan]{source_display}[/cyan]:\n\t"
                + ", ".join(f"[blue]{skill.name}[/blue]" for skill in found_skills)
            )
        if not found_skills:
            print(
                "[red]No skills found. Provide either a skill directory with SKILL.md or a directory containing skill subdirectories with SKILL.md.[/red]"
            )
            raise typer.Exit(code=1)
    else:
        if "/" not in repo:
            print("[red]Repository must be in format 'owner/repo'[/red]")
            raise typer.Exit(code=1)

        owner, repo_name = repo.split("/", 1)
        repo_url = f"https://github.com/{repo}.git"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            print(f"Cloning {repo_url} to {rel_home(temp_path)}...")
            run_git_clone(repo_url, temp_path, depth=1)

            # Support both default and custom subdirectory for skills
            skills_dir = temp_path / path if path else temp_path / "skills"
            if not skills_dir.exists() or not skills_dir.is_dir():
                print(f"[red]No '{path or 'skills/'}' directory found in {repo}[/red]")
                raise typer.Exit(code=1)

            storage_base = get_skills_storage_dir()
            target_dir = storage_base / category / GH_PREFIX / owner / repo_name

            all_skills = [item for item in skills_dir.iterdir() if item.is_dir() and (item / "SKILL.md").exists()]

            if skills:
                selected = set(s.strip() for s in skills.split(",") if s.strip())
                found_skills = [item for item in all_skills if item.name in selected]
            else:
                found_skills = all_skills

            if verbose_state.verbose:
                print(
                    f"Found {len(found_skills)} skills at [cyan]{rel_home(target_dir)}[/cyan]:\n\t"
                    + ", ".join(
                        f"[blue]{skill.name}[/blue]" for skill in found_skills
                    )
                )
            if not found_skills:
                print(f"[red]No skills found inside the '{path}' directory matching selection.[/red]")
                raise typer.Exit(code=1)

            if target_dir.exists():
                print(f"Overwriting existing directory at {rel_home(target_dir)}...")
                shutil.rmtree(target_dir)

            for skill in found_skills:
                dest_skill_dir = target_dir / skill.name
                shutil.copytree(skill, dest_skill_dir)

            if verbose_state.verbose:
                print(f"Copied skills to [cyan]{rel_home(target_dir)}[/cyan]")

    config = get_config()
    lock = get_skills_lock(config)
    lock.sources[source_key] = SkillSource(
        repo=repo,
        source_type=source_type,
        source_path=source_key if source_type == LOCAL_SOURCE_TYPE else None,
        source_layout=source_layout,
        category=category,
        skills=[skill.name for skill in found_skills],
    )
    save_skills_lock(config, lock)

    if source_type == LOCAL_SOURCE_TYPE:
        print(
            f"✅ Successfully added {len(found_skills)} local skills from {source_display}"
        )
    else:
        print(
            f"✅ Successfully added {len(found_skills)} skills from {repo} to [green]{rel_home(target_dir)}[/green]"
        )

    # Trigger sync
    sync_skills(verbose=verbose_state.verbose)


@app.command("remove")
def remove_skill(
    target: str = typer.Argument(..., help="Skill name or repository (owner/repo)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    verbose: bool = False,
):
    """Remove a skill or all skills from a repository."""
    verbose_state.verbose = verbose
    if not yes:
        typer.confirm(f"Are you sure you want to remove {target}?", abort=True)

    config = get_config()
    lock = get_skills_lock(config)

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
    default_skills_dir = scope_dir / "skills"
    targets.append(default_skills_dir)
    for agent_name in config.agents:
        if agent_name in DEFAULT_AGENTS:
            agent = DEFAULT_AGENTS[agent_name]
            loc = (
                agent.local_location
                if config.scope == "local"
                else agent.global_location
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
        print(f"🗑️ Removed skill '[yellow]{skill_to_remove}[/yellow]' from {repo_to_remove}")
        if not source.skills:
            del lock.sources[repo_to_remove]
            print(f"No more skills in [yellow]{repo_to_remove}[/yellow], removed repository reference.")
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
        print(f"🗑️ Removed repository '[yellow]{repo_to_remove}[/yellow]' and all its skills.")

    save_skills_lock(config, lock)
    print(f"Removed {len(removed_skills)} skills from " + ", ".join([f"[yellow]{rel_home(t)}[/yellow]" for t in targets]))
    sync_skills(verbose=verbose_state.verbose)


@app.command("sync")
def sync_skills(verbose: bool = False):
    """Update all links/copies in default-lib and for other agents."""
    verbose_state.verbose = verbose
    config = get_config()
    lock = get_skills_lock(config)
    scope_dir = get_scope_dir(config)

    # Target directories
    targets = []

    # Default scope directory
    default_skills_dir = scope_dir / "skills"
    targets.append(default_skills_dir)

    # Agent directories
    for agent_name in config.agents:
        if agent_name in DEFAULT_AGENTS:
            agent = DEFAULT_AGENTS[agent_name]
            # Use global/local location based on scope
            loc = (
                agent.local_location
                if config.scope == "local"
                else agent.global_location
            )
            targets.append(Path(loc).expanduser().resolve())
        else:
            print(f"[yellow]Warning: Unknown agent '{agent_name}'. Skipping.[/yellow]")

    # Ensure target directories exist
    for t in targets:
        t.mkdir(parents=True, exist_ok=True)

    # We only overwrite skills managed by our lockfile
    # to avoid blowing away user's manual skills.

    # Process each skill source
    total_links = 0
    synced_skills = 0
    missing_skills: list[tuple[str, Path]] = []

    for source_key, source in lock.sources.items():
        source_type = source.source_type or GITHUB_SOURCE_TYPE
        storage_dir = None
        local_source_root = None

        if source_type == LOCAL_SOURCE_TYPE:
            local_path_str = source.source_path or source_key
            local_source_root = Path(local_path_str).expanduser().resolve()
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
            if source_type == LOCAL_SOURCE_TYPE:
                if source.source_layout == "single":
                    skill_src_dir = local_source_root
                else:
                    skill_src_dir = local_source_root / skill
            else:
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

                # Clean up existing managed target
                if target_skill_dir.exists() or target_skill_dir.is_symlink():
                    if target_skill_dir.is_symlink():
                        target_skill_dir.unlink()
                        if verbose_state.verbose:
                            print(f"Removed old symlink [magenta]{rel_home(target_skill_dir)}[/magenta]")
                    elif target_skill_dir.is_dir():
                        shutil.rmtree(target_skill_dir)
                        if verbose_state.verbose:
                            print(f"Removed old directory [magenta]{rel_home(target_skill_dir)}[/magenta]")
                    else:
                        target_skill_dir.unlink()
                        if verbose_state.verbose:
                            print(f"Removed old file [magenta]{rel_home(target_skill_dir)}[/magenta]")

                if config.sync_mode == SyncMode.LINK:
                    target_skill_dir.symlink_to(skill_src_dir, target_is_directory=True)
                    total_links += 1
                    if verbose_state.verbose:
                        print(f"🔗 Linked [cyan]{rel_home(target_skill_dir)}[/cyan] -> [cyan]{rel_home(skill_src_dir)}[/cyan]")
                else:
                    shutil.copytree(skill_src_dir, target_skill_dir)
                    if verbose_state.verbose:
                        print(f"📁 Copied [cyan]{rel_home(skill_src_dir)}[/cyan] -> [cyan]{rel_home(target_skill_dir)}[/cyan]")

    if missing_skills and not verbose_state.verbose:
        print(
            f"⚠️  Skipped {len(missing_skills)} missing skills from the lockfile."
        )

    print(f"🔄 Synced {synced_skills} skills across {len(targets)} locations.")
    if verbose_state.verbose:
        print(f"Added {total_links} symlinks (sync_mode=[cyan]{str(config.sync_mode)}[/cyan])")


@app.command("list")
def list_skills():
    """List installed skills as a table."""
    from rich.table import Table
    config = get_config()
    lock = get_skills_lock(config)

    if not lock.sources:
        print("No skills installed.")
        return

    table = Table(title="Installed Skills")
    table.add_column("Repo", style="cyan", no_wrap=True)
    table.add_column("Skill Name", style="magenta")
    table.add_column("Location", style="green")
    table.add_column("Agents", style="yellow")

    # Determine all agent directories
    agent_dirs = {}
    for agent_name in config.agents:
        if agent_name in DEFAULT_AGENTS:
            agent = DEFAULT_AGENTS[agent_name]
            loc = agent.local_location if config.scope == "local" else agent.global_location
            agent_dirs[agent_name] = loc
        else:
            agent_dirs[agent_name] = "(unknown)"

    # Default location
    default_loc = str((get_scope_dir(config) / "skills").expanduser().resolve())

    for repo, source in lock.sources.items():
        for skill in source.skills:
            # Default location
            locations = [default_loc]
            # Agent locations
            agent_list = []
            for agent_name, loc in agent_dirs.items():
                agent_list.append(agent_name)
                locations.append(str(Path(loc).expanduser().resolve()))
            # Only show unique locations
            locations_str = "\n".join(sorted(set(locations)))
            agents_str = ", ".join(agent_list) if agent_list else "none"
            table.add_row(repo, skill, locations_str, agents_str)
    print(table)
