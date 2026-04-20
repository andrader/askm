import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
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
from ..models import SkillSource
from .utils import (
    GH_PREFIX,
    LOCAL_SOURCE_TYPE,
    GITHUB_SOURCE_TYPE,
    rel_home,
    run_git_clone,
    is_path_in_harness_dir,
)


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
    config = get_config()

    if is_local_source:
        if not local_path.is_dir():
            print(f"[red]Local source must be a directory: {repo}[/red]")
            raise typer.Exit(code=1)

        resolved_local = local_path.resolve()
        harness_name = is_path_in_harness_dir(resolved_local, config)
        if harness_name:
            print(
                f"[yellow]Source is inside a harness directory ({harness_name}).[/yellow]"
            )

            if typer.confirm(
                "Move to central storage? (Recommended for management)", default=True
            ):
                storage_base = get_skills_storage_dir()
                new_path = storage_base / category / resolved_local.name

                if new_path.exists():
                    print(
                        f"[red]Destination {rel_home(new_path)} already exists. Aborting move.[/red]"
                    )
                else:
                    print(f"Moving to [cyan]{rel_home(new_path)}[/cyan]...")
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(resolved_local), str(new_path))
                    resolved_local = new_path

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
            try:
                run_git_clone(repo_url, temp_path, depth=1)
            except subprocess.CalledProcessError:
                # Error message already printed by run_git_clone
                raise typer.Exit(code=1)

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

    lock = get_skills_lock(config)

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
    from . import sync_skills

    sync_skills(verbose=verbose_state.verbose)
