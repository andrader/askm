import json
from pathlib import Path

import typer
from rich import print
from rich.table import Table
from rich.text import Text

from ..config import (
    get_all_agents,
    get_config,
    get_scope_dir,
    get_skills_lock,
)
from ..main import app
from .utils import (
    LOCAL_SOURCE_TYPE,
    GITHUB_SOURCE_TYPE,
    rel_home,
)


@app.command("list")
@app.command("ls", hidden=True)
def list_skills(
    only_local: bool = typer.Option(
        False, "--only-local", help="Show only local skills"
    ),
    remote: bool = typer.Option(
        False, "--remote", help="Show only remote (GitHub) skills"
    ),
    as_json: bool = typer.Option(False, "--json", help="Output in JSON format"),
):
    """List installed skills as a table or JSON."""
    config = get_config()
    lock = get_skills_lock(config)

    # Determine targets (where skills should be installed)
    all_agents = get_all_agents(config)
    configured_agents = []

    # 1. Default scope directory
    default_dir = get_scope_dir(config)
    configured_agents.append(("default", default_dir))

    # 2. Configured agents
    for agent_name in config.agents:
        if agent_name in all_agents:
            agent = all_agents[agent_name]
            loc = (
                agent.local_location
                if config.scope == "local"
                else agent.global_location
            )
            p = Path(loc).expanduser().resolve()
            configured_agents.append((agent_name, p))

    # Filter sources
    sources_to_show = []
    for source_key, source in lock.sources.items():
        source_type = source.source_type or GITHUB_SOURCE_TYPE
        if only_local and source_type != LOCAL_SOURCE_TYPE:
            continue
        if remote and source_type == LOCAL_SOURCE_TYPE:
            continue
        sources_to_show.append((source_key, source))

    # Prepare data for display/JSON
    installed_skills_data = []
    managed_skill_names = set()

    for source_key, source in sources_to_show:
        source_type = source.source_type or GITHUB_SOURCE_TYPE
        repo_ref = source.repo or source_key

        for skill_name in source.skills:
            managed_skill_names.add(skill_name)
            status = {}
            for agent_name, agent_dir in configured_agents:
                skill_path = agent_dir / skill_name
                if skill_path.exists() or skill_path.is_symlink():
                    status[agent_name] = "installed"
                else:
                    status[agent_name] = "missing"

            installed_skills_data.append(
                {
                    "name": skill_name,
                    "repo": repo_ref,
                    "source_type": source_type,
                    "status": status,
                    "last_updated": source.last_updated or "-",
                }
            )

    # Scan for unmanaged skills
    unmanaged_skills_data = []
    for agent_name, agent_dir in configured_agents:
        if not agent_dir.exists():
            continue
        for item in agent_dir.iterdir():
            if item.is_dir() and item.name not in managed_skill_names:
                # Check if it has a SKILL.md to be considered a skill
                if (item / "SKILL.md").exists():
                    unmanaged_skills_data.append(
                        {"name": item.name, "agent": agent_name, "path": rel_home(item)}
                    )

    if as_json:
        output = {
            "installed": installed_skills_data,
            "unmanaged": unmanaged_skills_data,
        }
        print(json.dumps(output, indent=2))
        return

    if not lock.sources and not unmanaged_skills_data:
        print("No skills installed.")
        return

    # Render Table
    table = Table(title="Installed Skills")
    table.add_column("Skill Name", style="magenta", no_wrap=True)
    table.add_column("Repo/Origin", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Last Updated", style="white")

    def format_location_path(p: Path) -> str:
        if p.name == "skills":
            p = p.parent
        return rel_home(p)

    for skill in installed_skills_data:
        status_lines = []
        for agent_name, state in skill["status"].items():
            color = "green" if state == "installed" else "red"
            icon = "✅" if state == "installed" else "❌"
            status_lines.append(f"[{color}]{icon} {agent_name}[/{color}]")

        status_str = "\n".join(status_lines)

        last_updated = skill["last_updated"]
        if last_updated != "-" and "T" in last_updated:
            last_updated = last_updated.split("T")[0]

        repo_display = skill["repo"]
        if skill["source_type"] == GITHUB_SOURCE_TYPE:
            repo_display = Text(
                repo_display, style=f"cyan link https://github.com/{repo_display}"
            )
        else:
            repo_display = rel_home(Path(repo_display).expanduser().resolve())

        table.add_row(
            skill["name"],
            repo_display,
            status_str,
            str(last_updated),
        )

    if installed_skills_data:
        print(table)
    elif not only_local and not remote:
        print("No managed skills installed.")

    # Render Unmanaged Table
    if unmanaged_skills_data:
        print("\n[yellow]Unmanaged Skills (not in lockfile):[/yellow]")
        un_table = Table()
        un_table.add_column("Skill Name", style="magenta")
        un_table.add_column("Agent", style="cyan")
        un_table.add_column("Path", style="green")

        for un in unmanaged_skills_data:
            un_table.add_row(un["name"], un["agent"], un["path"])
        print(un_table)
