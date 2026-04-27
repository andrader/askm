import json
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table
from rich.text import Text

from ..config import (
    get_all_harnesses,
    get_config,
    get_scope_dir,
    get_skills_lock,
    get_skills_storage_dir,
)
from ..models import ScopeType
from ..core.constants import (
    GH_PREFIX,
    GITHUB_SOURCE_TYPE,
    LOCAL_SOURCE_TYPE,
    BANNER,
)
from ..core.filesystem import rel_home


from .utils import (
    extract_skill_description,
)


def get_installed_skills_data(
    only_local: bool = False,
    remote: bool = False,
    scope: Optional[ScopeType] = None,
    show_descr: bool = False,
):
    """
    Core logic to gather data about installed and unmanaged skills.
    Returns a dict with 'installed' and 'unmanaged' lists.
    """
    config = get_config()

    if scope:
        scopes_to_check = [scope]
    else:
        # Show both by default if not specified
        scopes_to_check = [ScopeType.USER, ScopeType.LOCAL]

    installed_skills_data = []
    managed_skill_names = set()
    unmanaged_skills_data = []

    all_harnesses = get_all_harnesses(config)

    for current_scope in scopes_to_check:
        temp_config = config.model_copy()
        temp_config.scope = current_scope
        lock = get_skills_lock(temp_config)

        # Determine targets (where skills should be installed)
        configured_harnesses_paths: dict[Path, list[str]] = {}

        # 1. Default scope directory
        default_dir = get_scope_dir(temp_config)
        configured_harnesses_paths[default_dir] = [".agents"]

        # 2. Configured harnesses
        for harness_name in config.harnesses:
            if harness_name in all_harnesses:
                harness = all_harnesses[harness_name]
                loc = (
                    harness.local_location
                    if current_scope == ScopeType.LOCAL
                    else harness.global_location
                )
                p = Path(loc).expanduser().resolve()
                if p not in configured_harnesses_paths:
                    configured_harnesses_paths[p] = []
                if harness_name not in configured_harnesses_paths[p]:
                    configured_harnesses_paths[p].append(harness_name)

        # Filter sources
        sources_to_show = []
        for source_key, source in lock.sources.items():
            source_type = source.source_type or GITHUB_SOURCE_TYPE
            if only_local and source_type != LOCAL_SOURCE_TYPE:
                continue
            if remote and source_type == LOCAL_SOURCE_TYPE:
                continue
            sources_to_show.append((source_key, source))

        def format_location_path(p: Path) -> str:
            if p.name == "skills":
                p = p.parent
            return rel_home(p)

        # Cache harness directory contents
        harness_contents = {}
        for h_dir, h_names in configured_harnesses_paths.items():
            primary_name = h_names[0]
            if h_dir.exists():
                try:
                    contents = {}
                    for item in h_dir.iterdir():
                        info = {
                            "is_symlink": item.is_symlink(),
                            "is_broken": item.is_symlink() and not item.exists(),
                            "exists": item.exists(),
                            "is_dir": item.is_dir(),
                            "has_skill_md": (item / "SKILL.md").exists()
                            if item.is_dir()
                            else False,
                        }
                        contents[item.name] = info
                    harness_contents[primary_name] = contents
                except Exception:
                    harness_contents[primary_name] = {}
            else:
                harness_contents[primary_name] = {}

        for source_key, source in sources_to_show:
            source_type = source.source_type or GITHUB_SOURCE_TYPE
            repo_ref = source.repo or source_key

            storage_dir: Path | None = None
            local_source_root: Path | None = None

            if source_type == LOCAL_SOURCE_TYPE:
                local_path_str = source.source_path or source_key
                local_source_root = Path(local_path_str).expanduser().resolve()
            else:
                if source.source_path:
                    storage_dir = Path(source.source_path).expanduser().resolve()
                else:
                    if "/" in repo_ref:
                        owner, repo_name = repo_ref.split("/", 1)
                        storage_dir = (
                            get_skills_storage_dir()
                            / str(source.category or "misc")
                            / GH_PREFIX
                            / owner
                            / repo_name
                        )

            for skill_name in source.skills:
                managed_skill_names.add(skill_name)

                skill_src_dir = None
                if source_type == LOCAL_SOURCE_TYPE:
                    if local_source_root:
                        skill_src_dir = (
                            local_source_root
                            if source.source_layout == "single"
                            else local_source_root / skill_name
                        )
                elif storage_dir:
                    skill_src_dir = storage_dir / skill_name

                source_exists = skill_src_dir.exists() if skill_src_dir else False

                description = ""
                if show_descr and source_exists and skill_src_dir:
                    skill_md = skill_src_dir / "SKILL.md"
                    if skill_md.exists():
                        description = extract_skill_description(skill_md.read_text())

                status = {}
                for h_dir, h_names in configured_harnesses_paths.items():
                    primary_name = h_names[0]
                    display_name = ", ".join(h_names)
                    info = {
                        "path": format_location_path(h_dir),
                        "exists": False,
                        "is_symlink": False,
                        "is_broken": False,
                    }

                    h_contents = harness_contents.get(primary_name, {})
                    if skill_name in h_contents:
                        item_info = h_contents[skill_name]
                        info["is_symlink"] = item_info["is_symlink"]
                        info["is_broken"] = item_info["is_broken"]
                        info["exists"] = item_info["exists"]

                    status[display_name] = info

                installed_skills_data.append(
                    {
                        "name": skill_name,
                        "repo": repo_ref,
                        "source_type": source_type,
                        "source_exists": source_exists,
                        "source_path": rel_home(skill_src_dir)
                        if skill_src_dir
                        else "unknown",
                        "status": status,
                        "last_updated": source.last_updated or "-",
                        "scope": current_scope.value,
                        "version": source.version,
                        "source": source.source,
                        "category": source.category or "misc",
                        "description": description,
                    }
                )

        # Scan for unmanaged skills in this scope
        for h_dir, h_names in configured_harnesses_paths.items():
            primary_name = h_names[0]
            display_name = ", ".join(h_names)
            h_contents = harness_contents.get(primary_name, {})
            for item_name, info in h_contents.items():
                if info["is_dir"] and item_name not in managed_skill_names:
                    if info["has_skill_md"]:
                        description = ""
                        if show_descr:
                            skill_md = h_dir / item_name / "SKILL.md"
                            if skill_md.exists():
                                description = extract_skill_description(
                                    skill_md.read_text()
                                )

                        unmanaged_skills_data.append(
                            {
                                "name": item_name,
                                "harness": display_name,
                                "path": rel_home(h_dir / item_name),
                                "scope": current_scope.value,
                                "description": description,
                            }
                        )

    return {
        "installed": installed_skills_data,
        "unmanaged": unmanaged_skills_data,
    }


def list_skills(
    target: Optional[str] = typer.Argument(None, hidden=True),
    only_local: bool = typer.Option(
        False, "--only-local", help="Show only local skills (from local path source)"
    ),
    remote: bool = typer.Option(
        False, "--remote", help="Show only remote (GitHub) skills"
    ),
    scope: Optional[ScopeType] = typer.Option(
        None, "--scope", help="Filter by scope (global or local)"
    ),
    as_json: bool = typer.Option(False, "--json", help="Output in JSON format"),
    show_descr: bool = typer.Option(
        False, "--descr", "--description", help="Show skill descriptions"
    ),
):
    """
    List installed skills as a table or JSON.

    Aliases: ls
    """
    if not as_json:
        print(BANNER)

    if target:
        if target != "skills":
            if only_local or remote or scope is not None or as_json:
                print(
                    f"[red]Options like --json, --only-local, --remote, --scope are not supported for target '{target}'.[/red]"
                )
                raise typer.Exit(code=1)

        if target == "skills":
            pass
        elif target in ("agents", "agent", "harness", "harnesses"):
            from .harness_cli import harness_list

            harness_list()
            return
        elif target == "config":
            from .config_cli import config_show

            config_show()
            return
        else:
            print(f"[red]Unknown list target: {target}[/red]")
            raise typer.Exit(code=1)

    data = get_installed_skills_data(
        only_local=only_local, remote=remote, scope=scope, show_descr=show_descr
    )
    installed_skills_data = data["installed"]
    unmanaged_skills_data = data["unmanaged"]

    if as_json:
        # Use standard print for JSON to avoid rich colorization
        import sys

        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return

    if not installed_skills_data and not unmanaged_skills_data:
        print("No skills installed.")
        return

    # Render Table
    table = Table(title="Installed Skills")
    table.add_column("Scope", style="yellow")
    table.add_column("Category", style="blue")
    table.add_column("Skill Name", style="magenta")
    if show_descr:
        table.add_column("Description", style="italic white")
    table.add_column("Repo/Origin", style="cyan")
    table.add_column("Other Locations", style="green")
    table.add_column("Last Updated", style="white")

    for skill in installed_skills_data:
        skill_display = skill["name"]
        if skill.get("version"):
            skill_display += f" [dim]@{skill['version']}[/dim]"

        status_lines = []
        for harness_name, info in skill["status"].items():
            symbol = "🔗" if info["is_symlink"] else "📁"
            if info["is_broken"]:
                status_lines.append(f"[red]⛓️‍💥 {harness_name} ({info['path']})[/red]")
            elif info["exists"]:
                status_lines.append(
                    f"[green]{symbol} {harness_name}[/green] [dim]({info['path']})[/dim]"
                )
            else:
                status_lines.append(
                    f"[red]{symbol} {harness_name} ({info['path']})[/red] [bold red]❌[/bold red]"
                )

        status_str = "\n".join(status_lines)

        last_updated = skill["last_updated"]
        if last_updated != "-" and "T" in last_updated:
            last_updated = last_updated.split("T")[0]

        repo_display = skill["repo"]
        source_gone_symbol = (
            " [bold red]⚠️[/bold red]" if not skill["source_exists"] else ""
        )
        if skill["source_type"] == GITHUB_SOURCE_TYPE:
            repo_text = Text("🌐 ", style="white")
            url = skill.get("source") or f"https://github.com/{repo_display}"
            repo_text.append(repo_display, style=f"cyan link {url}")
            if source_gone_symbol:
                repo_text.append(" ⚠️", style="bold red")
            repo_display = repo_text
        else:
            repo_text = Text("🏠 ", style="white")
            repo_text.append(
                rel_home(Path(repo_display).expanduser().resolve()), style="cyan"
            )
            if source_gone_symbol:
                repo_text.append(" ⚠️", style="bold red")
            repo_display = repo_text

        row = [
            skill["scope"].capitalize(),
            skill["category"],
            skill_display,
        ]
        if show_descr:
            row.append(skill["description"])
        row.extend(
            [
                repo_display,
                status_str,
                str(last_updated),
            ]
        )
        table.add_row(*row)

    if installed_skills_data:
        print(table)
        print(
            "\n[dim]Legend: 🏠 Local | 🌐 GitHub | 🔗 Symlink | 📁 Directory | ❌ Missing | ⛓️‍💥 Broken | ⚠️ Source Gone[/dim]"
        )
    elif not only_local and not remote:
        print("No managed skills installed.")

    # Render Unmanaged Table
    if unmanaged_skills_data:
        print("\n[yellow]Unmanaged Skills (not in lockfile):[/yellow]")
        un_table = Table()
        un_table.add_column("Scope", style="yellow")
        un_table.add_column("Skill Name", style="magenta")
        if show_descr:
            un_table.add_column("Description", style="italic white")
        un_table.add_column("Harness", style="cyan")
        un_table.add_column("Path", style="green")

        for un in unmanaged_skills_data:
            row = [un["scope"].capitalize(), un["name"]]
            if show_descr:
                row.append(un["description"])
            row.extend([un["harness"], un["path"]])
            un_table.add_row(*row)
        print(un_table)

    # Render Tips
    print("\n[bold blue]Tips:[/bold blue]")
    print("  - Manage unmanaged: [cyan]jup add <path>[/cyan]")
    print(
        "  - Filter by scope: [cyan]jup list --scope local[/cyan] or [cyan]--scope user[/cyan]"
    )
    print(
        "  - Filter by type: [cyan]jup list --only-local[/cyan] or [cyan]--remote[/cyan]"
    )
    print("  - Fix missing source: [cyan]jup mv <skill> <new-path> --ref-only[/cyan]")
    print("  - Fix broken/missing link: [cyan]jup sync[/cyan]")
