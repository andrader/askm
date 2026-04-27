from typing import Any, Dict

import typer
from rich import print
from rich.table import Table

from ..context import verbose_state
from .add import add_skill
from .utils import (
    fetch_remote_skill_md,
)


from .utils_tui import (
    search_skills_registry,
    get_repo_and_path,
    format_markdown_for_tui,
    render_skill_line,
)


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
    verbose_state.verbose = verbose

    if verbose_state.verbose:
        print(f"Searching registry for query: [cyan]{query}[/cyan]")

    skills = search_skills_registry(query)

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
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
    from prompt_toolkit.layout.containers import WindowAlign
    from prompt_toolkit.layout.controls import FormattedTextControl

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
        for i, skill in enumerate(skills):
            name = skill.get("name", "Unknown")
            source_id = skill.get("id", "")
            repo = (
                source_id.replace("github/", "")
                if source_id.startswith("github/")
                else source_id
            )
            installs = skill.get("installs", 0)

            line = render_skill_line(
                name=name,
                repo=repo,
                installs=installs,
                is_selected=i in state["selected"],
                is_current=i == state["index"],
                width=48,
            )
            lines.append(line)
        return HTML("\n".join(lines) + "\n")

    def get_preview_text():
        content = state["preview_content"]
        if state["view"] != "preview" and not content.startswith("#"):
            return "Press [Right] to preview SKILL.md"

        return format_markdown_for_tui(content)

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
