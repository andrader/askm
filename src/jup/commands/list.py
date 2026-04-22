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
from ..main import app
from ..models import ScopeType
from .utils import (
    GH_PREFIX,
    GITHUB_SOURCE_TYPE,
    LOCAL_SOURCE_TYPE,
    rel_home,
)


@app.command("list")
@app.command("ls", hidden=True)
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
):
    """List installed skills as a table or JSON."""
    if target:
        if target == "skills":
            pass
        elif target in ("agents", "agent", "harness", "harnesses"):
            from ..main import harness_list

            harness_list()
            return
        elif target == "config":
            from ..main import config_show

            config_show()
            return
        else:
            print(f"[red]Unknown list target: {target}[/red]")
            raise typer.Exit(code=1)

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
        configured_harnesses = []

        # 1. Default scope directory
        default_dir = get_scope_dir(temp_config)
        configured_harnesses.append((".agents", default_dir))

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
                configured_harnesses.append((harness_name, p))

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

        for source_key, source in sources_to_show:
            source_type = source.source_type or GITHUB_SOURCE_TYPE
            repo_ref = source.repo or source_key

            # Calculate source storage dir for this source
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

                # Check source existence
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

                status = {}
                for harness_name, harness_dir in configured_harnesses:
                    skill_path = harness_dir / skill_name
                    info = {
                        "path": format_location_path(harness_dir),
                        "exists": False,
                        "is_symlink": False,
                        "is_broken": False,
                    }

                    if skill_path.is_symlink():
                        info["is_symlink"] = True
                        if not skill_path.exists():
                            info["is_broken"] = True
                        else:
                            info["exists"] = True
                    elif skill_path.exists():
                        info["exists"] = True

                    status[harness_name] = info

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
                    }
                )

        # Scan for unmanaged skills in this scope
        for harness_name, harness_dir in configured_harnesses:
            if not harness_dir.exists():
                continue
            for item in harness_dir.iterdir():
                if item.is_dir() and item.name not in managed_skill_names:
                    # Check if it has a SKILL.md to be considered a skill
                    if (item / "SKILL.md").exists():
                        unmanaged_skills_data.append(
                            {
                                "name": item.name,
                                "harness": harness_name,
                                "path": rel_home(item),
                                "scope": current_scope.value,
                            }
                        )

    if as_json:
        output = {
            "installed": installed_skills_data,
            "unmanaged": unmanaged_skills_data,
        }
        print(json.dumps(output, indent=2))
        return

    if not installed_skills_data and not unmanaged_skills_data:
        print("No skills installed.")
        return

    # Render Table
    table = Table(title="Installed Skills")
    table.add_column("Scope", style="yellow")
    table.add_column("Skill Name", style="magenta", no_wrap=True)
    table.add_column("Repo/Origin", style="cyan")
    table.add_column("Other Locations", style="green")
    table.add_column("Last Updated", style="white")

    for skill in installed_skills_data:
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
            repo_text.append(
                repo_display, style=f"cyan link https://github.com/{repo_display}"
            )
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

        table.add_row(
            skill["scope"].capitalize(),
            skill["name"],
            repo_display,
            status_str,
            str(last_updated),
        )

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
        un_table.add_column("Harness", style="cyan")
        un_table.add_column("Path", style="green")

        for un in unmanaged_skills_data:
            un_table.add_row(
                un["scope"].capitalize(), un["name"], un["harness"], un["path"]
            )
        print(un_table)

    # Render Tips
    print("\n[bold blue]Tips:[/bold blue]")
    print("  - Manage unmanaged: [cyan]jup add <path>[/cyan]")
    print("  - Fix missing source: [cyan]jup mv <skill> <new-path> --ref-only[/cyan]")
    print("  - Fix broken/missing link: [cyan]jup sync[/cyan]")
