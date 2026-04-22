import shutil
import subprocess
import tempfile
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich import print

from ..config import (
    get_config,
    get_skills_storage_dir,
    skills_lock_session,
)
from ..context import verbose_state
from ..models import SkillSource, ScopeType
from ..core.filesystem import rel_home, validate_path
from ..core.constants import GH_PREFIX, LOCAL_SOURCE_TYPE, GITHUB_SOURCE_TYPE
from ..core.git import run_git_clone
from .utils import (
    is_path_in_harness_dir,
)


def parse_repo_arg(repo_arg: str):
    """
    Parses the repo argument.
    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo/tree/main/path/to/skill
    - owner/repo
    - owner/repo/path/to/skill
    - @version suffix on any of the above
    Returns (owner, repo, path, version, is_url) or None if local.
    """
    if not repo_arg:
        return None

    # 1. Detect and ignore git SSH URLs (e.g. git@github.com:owner/repo.git)
    if (
        "@" in repo_arg
        and ":" in repo_arg
        and not repo_arg.startswith(("http", "ssh://"))
    ):
        return None

    # 2. Extract version suffix (if any)
    # We split only the LAST @ to avoid confusion with usernames in URLs
    # and to handle cases like owner/repo@v1 correctly.
    version = None
    if "@" in repo_arg and not repo_arg.startswith("@"):
        is_url = "://" in repo_arg
        # If it's a URL, only extract if it's NOT a /tree/ URL (where branch is already present)
        # OR if the @ is at the very end (explicit version override)
        if not is_url or "/tree/" not in repo_arg:
            parts = repo_arg.rsplit("@", 1)
            # If the part after @ contains /, it's probably not a version suffix but part of a path
            if "/" not in parts[1]:
                repo_arg = parts[0]
                version = parts[1]

    # 3. Handle SSH and HTTP URLs
    if repo_arg.startswith(("http://", "https://", "ssh://")):
        parsed = urllib.parse.urlparse(repo_arg)
        # Handle userinfo in netloc (e.g. git@github.com)
        netloc = parsed.netloc
        if "@" in netloc:
            netloc = netloc.split("@")[-1]
        # Handle port in netloc (e.g. github.com:443)
        if ":" in netloc:
            netloc = netloc.split(":")[0]

        if netloc == "github.com":
            # Normalize path: remove redundant slashes and ..
            path_parts = [p for p in parsed.path.split("/") if p and p != ".."]
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1]
                if repo.endswith(".git"):
                    repo = repo[:-4]
                subpath = None
                if len(path_parts) > 4 and path_parts[2] == "tree":
                    subpath = "/".join(path_parts[4:])
                    if not version:
                        version = path_parts[3]
                return owner, repo, subpath, version, True
        return None  # Not a supported GitHub URL

    # 4. Handle shorthand owner/repo or local paths
    # Normalize: strip only trailing slashes and collapse multiple slashes and strip ..
    repo_arg_norm = "/".join(p for p in repo_arg.split("/") if p and p != "..")
    if repo_arg.startswith("/"):
        return None  # Absolute path is always local

    parts = repo_arg_norm.split("/")
    if len(parts) >= 2:
        # Check if it exists locally FIRST to allow local shadowing if intended
        # but only if it's a valid local path.
        if Path(repo_arg).expanduser().exists():
            return None

        owner = parts[0]
        repo = parts[1]
        subpath = "/".join(parts[2:]) if len(parts) > 2 else None
        return owner, repo, subpath, version, False

    return None


def inject_metadata(skill_md_path: Path, repo_url: str, version: Optional[str]):
    if not skill_md_path.exists():
        return
    content = skill_md_path.read_text()
    lines = content.splitlines()

    has_frontmatter = False
    end_idx = -1

    if lines and lines[0] == "---":
        for i in range(1, len(lines)):
            if lines[i] == "---":
                end_idx = i
                has_frontmatter = True
                break

    if has_frontmatter:
        new_lines = []
        for i in range(1, end_idx):
            if lines[i].startswith("source:") or lines[i].startswith("version:"):
                continue
            new_lines.append(lines[i])

        new_lines.append(f"source: {repo_url}")
        if version and version != "None":
            new_lines.append(f"version: {version}")

        final_lines = ["---"] + new_lines + ["---"] + lines[end_idx + 1 :]
        skill_md_path.write_text("\n".join(final_lines) + "\n")
    else:
        frontmatter = ["---", f"source: {repo_url}"]
        if version:
            frontmatter.append(f"version: {version}")
        frontmatter.extend(["---", ""])

        # If the file had content, make sure we have a blank line between frontmatter and content
        if content:
            if not content.startswith("\n"):
                frontmatter.append("")
            skill_md_path.write_text("\n".join(frontmatter) + content)
        else:
            skill_md_path.write_text("\n".join(frontmatter))


def add_skill(
    repo: str = typer.Argument(
        ...,
        help="GitHub repository (owner/repo), URL, or local directory. Can include @version.",
    ),
    category: str = typer.Option(
        "misc", "--category", help="Category for the skill (e.g., productivity/custom)"
    ),
    path: str = typer.Option(
        None,
        "--path",
        help="[GitHub only] Path to skills directory in the repo.",
    ),
    skills: str = typer.Option(
        None,
        "--skills",
        help="[GitHub only] Comma-separated list of skill names to add (default: all)",
    ),
    agent: str = typer.Option(
        None,
        "--agent",
        "-a",
        help="Comma-separated agents to install to (overrides config.harnesses)",
    ),
    scope: ScopeType = typer.Option(
        None,
        "--scope",
        help="Target scope (user or local)",
    ),
    custom_dir: str = typer.Option(
        None,
        "--dir",
        help="Install to a custom directory (overrides --agent and --scope)",
    ),
    verbose: bool = False,
):
    """Install skills from a GitHub repository or a local directory."""
    verbose_state.verbose = verbose
    source_type = GITHUB_SOURCE_TYPE
    source_layout = None
    source_key = repo
    source_display = repo
    found_skills: list[Path] = []
    target_dir: Path | None = None
    config = get_config()

    if scope:
        config.scope = scope
    if agent:
        config.harnesses = [a.strip() for a in agent.split(",")]

    parsed_repo = parse_repo_arg(repo)
    if not parsed_repo:
        local_path = Path(repo).expanduser()
        if not local_path.exists() or not local_path.is_dir():
            print(
                f"[red]Local source must be an existing directory or invalid repo format: {repo}[/red]"
            )
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

        if (resolved_local / "SKILL.md").exists():
            source_layout = "single"
            found_skills = [resolved_local]
        else:
            source_layout = "collection"
            for item in resolved_local.iterdir():
                if item.is_dir() and (item / "SKILL.md").exists():
                    found_skills.append(item)

        if verbose_state.verbose:
            print(f"Found {len(found_skills)} local skills.")
        if not found_skills:
            print("[red]No skills found.[/red]")
            raise typer.Exit(code=1)
        version_resolved = None
        repo_url = None
    else:
        owner, repo_name, parsed_path, version_resolved, is_url = parsed_repo
        repo_url = f"https://github.com/{owner}/{repo_name}.git"

        if parsed_path and not path:
            path = parsed_path

        # Normalize case for keys to avoid duplicates
        source_key = f"{owner.lower()}/{repo_name.lower()}"
        if path:
            source_key += f"/{path}"
        if version_resolved:
            source_key += f"@{version_resolved}"

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            print(f"Cloning {repo_url}...")
            try:
                if version_resolved:
                    run_git_clone(repo_url, temp_path, branch=version_resolved, depth=1)
                else:
                    run_git_clone(repo_url, temp_path, depth=1)
            except subprocess.CalledProcessError:
                raise typer.Exit(code=1)

            skills_dir = temp_path / path if path else temp_path / "skills"
            fallback_skills_dir = temp_path / ".claude" / "skills"

            if not skills_dir.exists() or not skills_dir.is_dir():
                if (
                    (not path or path == "skills/")
                    and fallback_skills_dir.exists()
                    and fallback_skills_dir.is_dir()
                ):
                    skills_dir = fallback_skills_dir
                elif (temp_path / "SKILL.md").exists() and not path:
                    # The root of the repo is the skill
                    skills_dir = temp_path
                else:
                    print(
                        f"[red]Skills directory not found at {path or 'skills/'}[/red]"
                    )
                    raise typer.Exit(code=1)

            storage_base = get_skills_storage_dir()
            target_dir = storage_base / category / GH_PREFIX / owner / repo_name
            if version_resolved:
                target_dir = target_dir.with_name(f"{repo_name}-{version_resolved}")

            # CRITICAL: Validate path AFTER all modifications (including @version)
            validate_path(target_dir, storage_base)

            if (skills_dir / "SKILL.md").exists():
                all_skills = [skills_dir]
                source_layout = "single"
            else:
                source_layout = "collection"
                # Support skills/*/SKILL.md discovery
                all_skills = [item for item in skills_dir.glob("*/SKILL.md")]
                all_skills = [item.parent for item in all_skills]

            if skills:
                selected = set(s.strip() for s in skills.split(",") if s.strip())
                found_skills = [item for item in all_skills if item.name in selected]
            else:
                found_skills = all_skills

            if not found_skills:
                print("[red]No skills found matching selection.[/red]")
                raise typer.Exit(code=1)

            if target_dir.exists():
                shutil.rmtree(target_dir)
            target_dir.mkdir(parents=True, exist_ok=True)

            for skill in found_skills:
                dest_skill_dir = (
                    target_dir / skill.name
                    if source_layout == "collection"
                    else target_dir
                )
                if source_layout == "single" and target_dir.exists():
                    shutil.rmtree(target_dir)  # clear if exist
                shutil.copytree(skill, dest_skill_dir)
                inject_metadata(dest_skill_dir / "SKILL.md", repo_url, version_resolved)

            if source_layout == "single":
                # Ensure found_skills points to the destination target_dir so lockfile stores correct name
                found_skills = [target_dir]

    with skills_lock_session(config) as lock:
        lock.sources[source_key] = SkillSource(
            repo=f"{owner.lower()}/{repo_name.lower()}"
            if source_type == GITHUB_SOURCE_TYPE
            else None,
            source_type=source_type,
            source_path=source_key if source_type == LOCAL_SOURCE_TYPE else None,
            source_layout=source_layout,
            category=category,
            skills=[skill.name for skill in found_skills],
            version=version_resolved,
            source=repo_url if source_type == GITHUB_SOURCE_TYPE else source_key,
            last_updated=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )

    if source_type == LOCAL_SOURCE_TYPE:
        print(
            f"✅ Successfully added {len(found_skills)} local skills from {source_display}"
        )
    else:
        assert target_dir is not None
        print(
            f"✅ Successfully added {len(found_skills)} skills from {owner}/{repo_name} to [green]{rel_home(target_dir)}[/green]"
        )

    # Trigger sync with potential custom_dir
    from ..core.sync import sync_logic

    sync_logic(
        verbose=verbose_state.verbose,
        custom_dir=custom_dir,
        config=config,
        logger=print,
    )
