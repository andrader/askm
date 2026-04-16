import json
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

import typer
from rich import print
from rich.markdown import Markdown

from .config import (
    get_all_agents,
    get_config,
    get_scope_dir,
    get_skills_lock,
    get_skills_storage_dir,
    save_skills_lock,
)
from .main import app, verbose_state
from .models import SkillSource, SyncMode

from typing import Dict, Optional, Any

GH_PREFIX = "gh"  # Used to namespace GitHub sources in storage
LOCAL_SOURCE_TYPE = "local"
GITHUB_SOURCE_TYPE = "github"


def rel_home(p):
    return str(p).replace(str(Path.home()), "~")


def fetch_remote_skill_md(
    repo: str, skill_name: Optional[str] = None, internal_path: str = ""
) -> str:
    """Fetch SKILL.md content from GitHub."""
    # Try different common paths for SKILL.md
    paths_to_try = []
    base_path = internal_path.strip("/")

    if skill_name:
        if base_path:
            # If internal_path points to the skill directory itself
            paths_to_try.append(f"{base_path}/SKILL.md")
            # If internal_path points to a parent directory
            paths_to_try.append(f"{base_path}/{skill_name}/SKILL.md")
        else:
            # Common default locations
            paths_to_try.append(f"skills/{skill_name}/SKILL.md")
            paths_to_try.append(f".claude/skills/{skill_name}/SKILL.md")
            paths_to_try.append(f"{skill_name}/SKILL.md")
            paths_to_try.append("SKILL.md")
    else:
        if base_path:
            paths_to_try.append(f"{base_path}/SKILL.md")
            paths_to_try.append("SKILL.md")
        else:
            paths_to_try.append("SKILL.md")
            paths_to_try.append("skills/SKILL.md")
            paths_to_try.append(".claude/skills/SKILL.md")

    for p in paths_to_try:
        url = f"https://raw.githubusercontent.com/{repo}/main/{p}"
        try:
            with urllib.request.urlopen(url) as response:
                return response.read().decode()
        except Exception:
            # Try master branch if main fails
            url = f"https://raw.githubusercontent.com/{repo}/master/{p}"
            try:
                with urllib.request.urlopen(url) as response:
                    return response.read().decode()
            except Exception:
                continue

    return f"SKILL.md not found in {repo}.\nTried paths:\n- " + "\n- ".join(
        paths_to_try
    )


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
        help="GitHub repository (owner/repo) or local skills directory. For GitHub, if the skills directory is missing, jup will also look for .claude/skills/ as a fallback.",
    ),
    category: str = typer.Option(
        "misc", "--category", help="Category for the skill (e.g., productivity/custom)"
    ),
    path: str = typer.Option(
        "skills/",
        "--path",
        help="[GitHub only] Path to skills directory in the repo (default: skills/). If not found, .claude/skills/ is tried as a fallback.",
    ),
    skills: str = typer.Option(
        None,
        "--skills",
        help="[GitHub only] Comma-separated list of skill names to add (default: all)",
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
            fallback_skills_dir = temp_path / ".claude" / "skills"
            if not skills_dir.exists() or not skills_dir.is_dir():
                # Try fallback only if path was not explicitly provided or was default 'skills/'
                if (
                    (not path or path == "skills/")
                    and fallback_skills_dir.exists()
                    and fallback_skills_dir.is_dir()
                ):
                    skills_dir = fallback_skills_dir
                    if verbose_state.verbose:
                        print(
                            f"[yellow]Falling back to .claude/skills/ in {repo}[/yellow]"
                        )
                else:
                    # If the directory doesn't exist, it might be that the repo root is the skill dir
                    # but only if path was not explicitly set or if it was set to something that doesn't exist.
                    # Actually, if the path was explicitly set, we should check if it's a skill dir.
                    pass

            storage_base = get_skills_storage_dir()
            target_dir = storage_base / category / GH_PREFIX / owner / repo_name

            # Check if skills_dir itself is a skill (has SKILL.md)
            if (skills_dir / "SKILL.md").exists():
                all_skills = [skills_dir]
                source_layout = "single"
            else:
                source_layout = "collection"
                all_skills = [
                    item
                    for item in skills_dir.iterdir()
                    if item.is_dir() and (item / "SKILL.md").exists()
                ]

            if skills:
                selected = set(s.strip() for s in skills.split(",") if s.strip())
                found_skills = [item for item in all_skills if item.name in selected]
            else:
                found_skills = all_skills

            if verbose_state.verbose:
                print(
                    f"Found {len(found_skills)} skills at [cyan]{rel_home(target_dir)}[/cyan]:\n\t"
                    + ", ".join(f"[blue]{skill.name}[/blue]" for skill in found_skills)
                )
            if not found_skills:
                print(
                    f"[red]No skills found inside the '{path}' directory matching selection.[/red]"
                )
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
    from datetime import datetime, timezone

    lock.sources[source_key] = SkillSource(
        repo=repo,
        source_type=source_type,
        source_path=source_key if source_type == LOCAL_SOURCE_TYPE else None,
        source_layout=source_layout,
        category=category,
        skills=[skill.name for skill in found_skills],
        last_updated=datetime.now(timezone.utc).isoformat(timespec="seconds"),
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
    default_skills_dir = scope_dir
    targets.append(default_skills_dir)
    all_agents = get_all_agents(config)
    for agent_name in config.agents:
        if agent_name in all_agents:
            agent = all_agents[agent_name]
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

    save_skills_lock(config, lock)
    print(
        f"Removed {len(removed_skills)} skills from "
        + ", ".join([f"[yellow]{rel_home(t)}[/yellow]" for t in targets])
    )
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
    default_skills_dir = scope_dir
    targets.append(default_skills_dir)

    # Agent directories
    all_agents = get_all_agents(config)
    for agent_name in config.agents:
        if agent_name in all_agents:
            agent = all_agents[agent_name]
            # Use global/local location based on scope
            loc = (
                agent.local_location
                if config.scope == "local"
                else agent.global_location
            )
            targets.append(Path(loc).expanduser().resolve())
        else:
            print(f"[yellow]Warning: Unknown agent '{agent_name}'. Skipping.[/yellow]")

    # Identify directories of inactive agents to clean up
    active_target_paths = {t.resolve() for t in targets}
    inactive_targets = []
    for agent_name, agent in all_agents.items():
        loc = agent.local_location if config.scope == "local" else agent.global_location
        p = Path(loc).expanduser().resolve()
        if p.exists() and p.resolve() not in active_target_paths:
            inactive_targets.append(p)

    # Ensure active target directories exist
    for t in targets:
        t.mkdir(parents=True, exist_ok=True)

    # We only overwrite skills managed by our lockfile
    # to avoid blowing away user's manual skills.

    # 1. Clean up managed skills from inactive agents and removed skills
    # Collect all skills that SHOULD exist
    all_managed_skills = set()
    for source in lock.sources.values():
        all_managed_skills.update(source.skills)

    # Clean inactive agents
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
            f"🧹 Cleaned {removed_from_inactive} skills from {len(inactive_targets)} inactive agent directories."
        )

    # Clean removed skills from active targets
    # (skills that are in the target but NOT in the lockfile)
    # This is a bit tricky because we don't want to delete user's manual skills.
    # However, jup's philosophy is that it manages these directories.
    # For now, we only clean up if the skill was previously managed.
    # Since we don't track "previously managed" outside the lockfile,
    # we might need a way to identify them.
    # But wait, the user's request is specifically about old symlinks when agents change.

    # 2. Process each skill source
    total_links = 0
    synced_skills = 0
    missing_skills: list[tuple[str, Path]] = []

    from datetime import datetime, timezone

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


@app.command("list")
def list_skills(
    only_local: bool = typer.Option(
        False, "--only-local", help="Show only local skills"
    ),
    remote: bool = typer.Option(
        False, "--remote", help="Show only remote (GitHub) skills"
    ),
):
    """List installed skills as a table."""
    from rich.table import Table
    from rich.text import Text

    config = get_config()
    lock = get_skills_lock(config)

    if not lock.sources:
        print("No skills installed.")
        return

    # Filter sources
    sources_to_show = []
    for source_key, source in lock.sources.items():
        source_type = source.source_type or GITHUB_SOURCE_TYPE
        if only_local and source_type != LOCAL_SOURCE_TYPE:
            continue
        if remote and source_type == LOCAL_SOURCE_TYPE:
            continue
        sources_to_show.append((source_key, source))

    if not sources_to_show:
        print("No matching skills installed.")
        return

    table = Table(title="Installed Skills")
    table.add_column("Skill Name", style="magenta", no_wrap=True)
    table.add_column("Repo/Origin", style="cyan")
    table.add_column("Location", style="green")
    table.add_column("Last Updated", style="white")

    # Determine targets (where skills are installed)
    targets = [get_scope_dir(config)]
    all_agents = get_all_agents(config)
    for agent_name in config.agents:
        if agent_name in all_agents:
            agent = all_agents[agent_name]
            loc = (
                agent.local_location
                if config.scope == "local"
                else agent.global_location
            )
            targets.append(Path(loc).expanduser().resolve())
    targets = list(set(targets))

    def format_location_path(p: Path) -> str:
        # Suppress /skills suffix
        if p.name == "skills":
            p = p.parent
        return rel_home(p)

    for source_key, source in sources_to_show:
        source_type = source.source_type or GITHUB_SOURCE_TYPE
        repo_ref = source.repo or source_key

        if source_type == LOCAL_SOURCE_TYPE:
            local_ref = source.source_path or source_key
            repo_display = Text(rel_home(Path(local_ref).expanduser().resolve()))
        else:
            repo_display = Text(
                repo_ref, style=f"cyan link https://github.com/{repo_ref}"
            )

        last_updated = source.last_updated or "-"
        if last_updated != "-" and "T" in last_updated:
            last_updated = last_updated.split("T")[0]

        for skill in source.skills:
            loc_list = []
            for t in targets:
                skill_path = t / skill
                if skill_path.exists() or skill_path.is_symlink():
                    symbol = "🔗 " if skill_path.is_symlink() else "📁 "
                    loc_list.append(f"{symbol}{format_location_path(t)}")

            locations_str = "\n".join(sorted(set(loc_list)))
            table.add_row(
                str(skill),
                repo_display,
                locations_str,
                str(last_updated),
            )
        table.add_section()

    print(table)


@app.command("show")
def show_skill(
    target: str = typer.Argument(
        ..., help="GitHub repository (owner/repo) or local skills directory."
    ),
    skill: str = typer.Option(
        None, "--skill", help="[GitHub only] Specific skill name to show"
    ),
    verbose: bool = False,
):
    """Show the content of SKILL.md and the directory structure of a skill."""
    from rich.tree import Tree
    from rich.console import Console

    console = Console()

    local_path = Path(target).expanduser()
    if local_path.exists():
        # Local source
        if local_path.is_file():
            if local_path.name == "SKILL.md":
                content = local_path.read_text()
                console.print(Markdown(content))
            else:
                print(f"[red]{target} is a file but not SKILL.md[/red]")
        else:
            skill_md = local_path / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                console.print(Markdown(content))
            else:
                print(f"[yellow]No SKILL.md found in {target}[/yellow]")

            # Show tree
            def add_to_tree(path: Path, tree: Tree):
                for item in sorted(path.iterdir()):
                    if item.name.startswith(".") or item.name == "__pycache__":
                        continue
                    if item.is_dir():
                        branch = tree.add(f"[bold blue]{item.name}/[/bold blue]")
                        add_to_tree(item, branch)
                    else:
                        tree.add(item.name)

            tree = Tree(f"[bold cyan]{rel_home(local_path)}[/bold cyan]")
            add_to_tree(local_path, tree)
            console.print(tree)
    else:
        # Remote source
        if "/" not in target:
            print("[red]Target must be a local path or 'owner/repo'[/red]")
            raise typer.Exit(code=1)

        repo = target
        print(f"Fetching information for [cyan]{repo}[/cyan]...")

        content = fetch_remote_skill_md(repo, skill)
        console.print(Markdown(content))

        # Show remote tree using GitHub API
        try:
            api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
            req = urllib.request.Request(api_url)
            # Add User-Agent to avoid 403
            req.add_header("User-Agent", "jup-cli")
            with urllib.request.urlopen(req) as response:
                tree_data = json.loads(response.read().decode())

            tree = Tree(f"[bold cyan]github.com/{repo}[/bold cyan]")
            nodes = {"": tree}

            # GitHub returns flat list of paths
            for item in tree_data.get("tree", []):
                path = item["path"]
                if path.startswith(".") or "/." in path or "__pycache__" in path:
                    continue

                parts = path.split("/")
                parent_path = "/".join(parts[:-1])
                name = parts[-1]

                if parent_path in nodes:
                    if item["type"] == "tree":
                        nodes[path] = nodes[parent_path].add(
                            f"[bold blue]{name}/[/bold blue]"
                        )
                    else:
                        nodes[parent_path].add(name)

            console.print(tree)
        except Exception as e:
            if verbose:
                print(f"[yellow]Could not fetch remote tree: {e}[/yellow]")
            else:
                print(
                    "[yellow]Could not fetch remote tree (GitHub API rate limit or private repo?)[/yellow]"
                )


@app.command("find")
def find_skills(
    query: str = typer.Argument(..., help="Search query for the skills registry"),
    limit: int = typer.Option(
        None, "--limit", "-n", help="Limit the number of results shown"
    ),
    min_installs: int = typer.Option(
        0, "--min-installs", "-i", help="Minimum number of installs to filter results"
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-it", help="Run in interactive mode to install skills"
    ),
    verbose: bool = False,
):
    """Search for skills in the skills.sh registry."""
    from rich.table import Table

    verbose_state.verbose = verbose
    api_url = f"https://skills.sh/api/search?q={urllib.parse.quote(query)}"

    if verbose_state.verbose:
        print(f"Searching registry: [cyan]{api_url}[/cyan]")

    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"[red]Failed to query the registry: {e}[/red]")
        raise typer.Exit(code=1)

    skills = data.get("skills", [])

    # Filter by min_installs
    if min_installs > 0:
        skills = [s for s in skills if s.get("installs", 0) >= min_installs]

    # Limit results
    if limit is not None:
        skills = skills[:limit]

    if not skills:
        print(f"No skills found for '[yellow]{query}[/yellow]' matching filters.")
        return

    if not interactive:
        table = Table(title=f"Search Results for '{query}'")
        table.add_column("#", style="dim", width=4)
        table.add_column("Skill / Name", style="magenta")
        table.add_column("Source / Repo", style="cyan")
        table.add_column("Installs", style="green", justify="right")

        for i, skill in enumerate(skills, 1):
            name = skill.get("name", skill.get("skillId", "Unknown"))
            source_id = skill.get("id", "")
            repo = (
                source_id.replace("github/", "")
                if source_id.startswith("github/")
                else source_id
            )
            installs = skill.get("installs", 0)
            table.add_row(str(i), name, repo, f"{installs:,}")
        print(table)
        return

    from prompt_toolkit import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.layout.containers import WindowAlign
    from prompt_toolkit.formatted_text import HTML

    kb = KeyBindings()
    state: Dict[str, Any] = {
        "index": 0,
        "selected": set(),
        "preview_content": "Select a skill and press [Right] to preview.",
        "skills_to_install": [],
        "view": "list",  # "list" or "preview"
    }

    def get_skill_at(idx):
        return skills[idx]

    def get_repo_and_path(skill):
        source_id = skill.get("id", "")
        full_path = (
            source_id.replace("github/", "")
            if source_id.startswith("github/")
            else source_id
        )
        parts = full_path.split("/")
        if len(parts) >= 2:
            repo = f"{parts[0]}/{parts[1]}"
            internal_path = "/".join(parts[2:]) if len(parts) > 2 else ""
        else:
            repo = full_path
            internal_path = ""
        return repo, internal_path

    def update_preview(event=None):
        skill = get_skill_at(state["index"])
        repo, internal_path = get_repo_and_path(skill)
        state["preview_content"] = f"Fetching SKILL.md for {repo}..."
        if event:
            event.app.invalidate()

        md_content = fetch_remote_skill_md(repo, skill.get("name"), internal_path)
        state["preview_content"] = md_content

    @kb.add("up")
    def _(event):
        state["index"] = (state["index"] - 1) % len(skills)
        if state["view"] == "preview":
            update_preview(event)

    @kb.add("down")
    def _(event):
        state["index"] = (state["index"] + 1) % len(skills)
        if state["view"] == "preview":
            update_preview(event)

    @kb.add("right")
    def _(event):
        if state["view"] == "list":
            update_preview(event)
            state["view"] = "preview"

    @kb.add("left")
    @kb.add("escape")
    def _(event):
        if state["view"] == "preview":
            state["view"] = "list"
        else:
            event.app.exit()

    @kb.add("space")
    def _(event):
        if state["view"] == "list":
            if state["index"] in state["selected"]:
                state["selected"].remove(state["index"])
            else:
                state["selected"].add(state["index"])

    @kb.add("enter")
    def _(event):
        state["skills_to_install"] = [skills[i] for i in state["selected"]]
        if not state["skills_to_install"] and state["view"] == "list":
            # If nothing selected, install the current one
            state["skills_to_install"] = [skills[state["index"]]]
        event.app.exit()

    @kb.add("c-c")
    def _(event):
        event.app.exit()

    def get_list_text():
        lines = []
        list_width = 48  # Total width for the list entries
        for i, skill in enumerate(skills):
            prefix = "[x]" if i in state["selected"] else "[ ]"
            pointer = ">" if i == state["index"] else " "
            name = skill.get("name", "Unknown")
            source_id = skill.get("id", "")
            repo = (
                source_id.replace("github/", "")
                if source_id.startswith("github/")
                else source_id
            )
            installs = skill.get("installs", 0)
            formatted_installs = f"[{installs:,}]"

            # Main label: name (repo)
            label = f"{name} ({repo})"

            # Calculate how much space we have for the label
            # pointer(2) + prefix(4) + padding(min 1) + installs(len)
            fixed_parts_len = 2 + 4 + 1 + len(formatted_installs)
            available_for_label = list_width - fixed_parts_len

            if len(label) > available_for_label:
                label = label[: available_for_label - 3] + "..."

            padding_len = list_width - (2 + 4 + len(label) + len(formatted_installs))
            padding = " " * padding_len

            import xml.sax.saxutils as saxutils

            safe_label = saxutils.escape(label)
            safe_installs = saxutils.escape(formatted_installs)

            # Construct the line with HTML tags
            content = f"{pointer} {prefix} <b>{safe_label}</b>{padding}<ansigreen>{safe_installs}</ansigreen>"

            if i == state["index"]:
                lines.append(f"<reverse>{content}</reverse>")
            else:
                lines.append(content)
        return HTML("\n".join(lines) + "\n")

    def get_preview_text():
        content = state["preview_content"]
        if state["view"] != "preview" and not content.startswith("#"):
            return "Press [Right] to preview SKILL.md"

        from prompt_toolkit.formatted_text import PygmentsTokens
        from pygments.lexers.markup import MarkdownLexer

        # We can use Pygments for basic MD highlighting in the TUI
        # or just return the text. Since we are in a TUI,
        # actual Rich rendering to the screen is complex.
        # Let's use PygmentsTokens for a nice look.
        return PygmentsTokens(list(MarkdownLexer().get_tokens(content)))

    # We use a simple FormattedTextControl for the preview, but we might want to render it with Rich first
    # For now, let's keep it simple.

    app_ui = Application(
        layout=Layout(
            HSplit(
                [
                    Window(
                        content=FormattedTextControl(
                            HTML(
                                "<b>jup find</b> - Use Up/Down to navigate, Space to toggle, Right to preview, Enter to install, Esc to exit"
                            )
                        ),
                        height=1,
                        align=WindowAlign.CENTER,
                    ),
                    Window(height=1, char="-"),
                    VSplit(
                        [
                            Window(
                                content=FormattedTextControl(get_list_text), width=50
                            ),
                            Window(width=1, char="|"),
                            Window(
                                content=FormattedTextControl(
                                    lambda: get_preview_text()
                                ),
                                wrap_lines=True,
                            ),
                        ]
                    ),
                ]
            )
        ),
        key_bindings=kb,
        full_screen=True,
    )
    app_ui.run()

    if state["skills_to_install"]:
        for skill in state["skills_to_install"]:
            repo, internal_path = get_repo_and_path(skill)
            print(
                f"Installing [magenta]{skill.get('name')}[/magenta] from [cyan]{repo}[/cyan]..."
            )
            if internal_path:
                add_skill(repo=repo, path=internal_path, verbose=verbose)
            else:
                add_skill(repo=repo, verbose=verbose)
    else:
        print("Cancelled.")
