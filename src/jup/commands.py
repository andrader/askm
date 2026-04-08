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
    repo: str = typer.Argument(..., help="GitHub repository (e.g., obra/superpowers)"),
    category: str = typer.Option(
        "misc", "--category", help="Category for the skill (e.g., productivity/custom)"
    ),
    verbose: bool = False,
):
    """Install skills from a GitHub repository."""
    verbose_state.verbose = verbose
    if "/" not in repo:
        print("[red]Repository must be in format 'owner/repo'[/red]")
        raise typer.Exit(code=1)

    owner, repo_name = repo.split("/", 1)
    repo_url = f"https://github.com/{repo}.git"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Cloning {repo_url} to {rel_home(temp_path)}...")
        run_git_clone(repo_url, temp_path, depth=1)

        skills_dir = temp_path / "skills"
        if not skills_dir.exists() or not skills_dir.is_dir():
            print(f"[red]No 'skills/' directory found in {repo}[/red]")
            raise typer.Exit(code=1)

        # Determine internal storage path
        storage_base = get_skills_storage_dir()
        target_dir = storage_base / category / GH_PREFIX / owner / repo_name

        # Extract nested skills
        found_skills: list[Path] = []
        for item in skills_dir.iterdir():
            # check if is dir and contains a SKILL.md file
            if item.is_dir() and (item / "SKILL.md").exists():
                found_skills.append(item)

        if verbose_state.verbose:
            print(f"Found {len(found_skills)} skills at [cyan]{rel_home(target_dir)}[/cyan]:\n\t" + ", ".join(f"[blue]{skill.name}[/blue]" for skill in found_skills))
        if not found_skills:
            print("[red]No skills found inside the 'skills/' directory.[/red]")
            raise typer.Exit(code=1)

        # Clear existing if any
        if target_dir.exists():
            print(f"Overwriting existing directory at {rel_home(target_dir)}...")
            shutil.rmtree(target_dir)

        # Copy all skills to internal storage
        for skill in found_skills:
            dest_skill_dir = target_dir / skill.name
            shutil.copytree(skill, dest_skill_dir)

        if verbose_state.verbose:
            print(f"Copied skills to [cyan]{rel_home(target_dir)}[/cyan]")




        # Update Lockfile
        config = get_config()
        lock = get_skills_lock(config)
        lock.sources[repo] = SkillSource(
            repo=repo, category=category, skills=[skill.name for skill in found_skills]
        )
        save_skills_lock(config, lock)

        print(f"✅ Successfully added {len(found_skills)} skills from {repo} to [green]{rel_home(target_dir)}[/green]")

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

    if "/" in target and target in lock.sources:
        repo_to_remove = target
    else:
        # Search for skill name
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

    for repo, source in lock.sources.items():
        owner, repo_name = repo.split("/", 1)
        storage_dir = (
            get_skills_storage_dir() / str(source.category) / "gh" / owner / repo_name
        )

        for skill in source.skills:
            skill_src_dir = storage_dir / skill
            if not skill_src_dir.exists():
                print(f"⚠️  Source dir for '[red]{skill}[/red]' missing: [red]{rel_home(skill_src_dir)}[/red]")
                continue

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

    print(f"🔄 Synced {sum(len(s.skills) for s in lock.sources.values())} skills across {len(targets)} locations.")
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
