import asyncio

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
    WindowAlign,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from rich import print

from .list import get_installed_skills_data
from .utils_tui import (
    search_skills_registry,
    get_repo_and_path,
    format_markdown_for_tui,
    render_skill_line,
)
from .utils import fetch_remote_skill_md
from .add import add_skill
from .remove import remove_skill


class TUIState:
    def __init__(self):
        self.current_tab = "installed"  # "installed", "discover"
        self.installed_skills = []
        self.unmanaged_skills = []
        self.discover_skills = []

        self.installed_index = 0
        self.discover_index = 0

        self.selected_installed = set()  # Indices
        self.selected_discover = set()  # Indices

        self.preview_content = "Move cursor to see SKILL.md"
        self.is_loading = False
        self.search_query = "latest"

        self.view_mode = "list"  # "list" or "preview"

    def get_current_list(self):
        if self.current_tab == "installed":
            # Show managed first then unmanaged
            return self.installed_skills + self.unmanaged_skills
        return self.discover_skills

    def get_current_index(self):
        if self.current_tab == "installed":
            return self.installed_index
        return self.discover_index

    def set_current_index(self, idx):
        if self.current_tab == "installed":
            self.installed_index = idx
        else:
            self.discover_index = idx

    def get_selected_set(self):
        if self.current_tab == "installed":
            return self.selected_installed
        return self.selected_discover


def tui_command():
    """Interactive TUI for managing skills."""
    state = TUIState()
    kb = KeyBindings()

    # Load initial data
    def load_installed_data():
        data = get_installed_skills_data()
        state.installed_skills = data["installed"]
        state.unmanaged_skills = data["unmanaged"]

    load_installed_data()

    def load_discover_data(query="latest"):
        state.is_loading = True
        state.discover_skills = search_skills_registry(query)
        state.is_loading = False

    # Asynchronous preview fetcher
    async def update_preview(idx=None):
        if idx is None:
            idx = state.get_current_index()

        skills = state.get_current_list()
        if not skills or idx >= len(skills):
            state.preview_content = "No skill selected."
            return

        skill = skills[idx]
        name = skill.get("name", "Unknown")

        if state.current_tab == "installed":
            # Try to read local SKILL.md
            from pathlib import Path

            source_path = skill.get("source_path") or skill.get("path")
            if source_path:
                p = Path(source_path).expanduser()
                skill_md = p / "SKILL.md" if p.is_dir() else p
                if skill_md.exists() and skill_md.is_file():
                    state.preview_content = skill_md.read_text()
                else:
                    state.preview_content = f"SKILL.md not found at {source_path}"
            else:
                state.preview_content = "Source path unknown."
        else:
            # Discover tab - fetch remote
            repo, internal_path = get_repo_and_path(skill)
            state.preview_content = f"Fetching remote SKILL.md for {repo}..."
            # Note: in a real async TUI we'd run this in a thread or task
            # For simplicity in prompt_toolkit, we'll do it synchronously for now
            # but ideally use loop.run_in_executor
            content = fetch_remote_skill_md(repo, name, internal_path)
            state.preview_content = content

    @kb.add("tab")
    def _(event):
        if state.current_tab == "installed":
            state.current_tab = "discover"
            if not state.discover_skills:
                load_discover_data(state.search_query)
        else:
            state.current_tab = "installed"
            load_installed_data()
        state.view_mode = "list"
        event.app.invalidate()

    @kb.add("up")
    def _(event):
        skills = state.get_current_list()
        if skills:
            idx = state.get_current_index()
            state.set_current_index((idx - 1) % len(skills))
            if state.view_mode == "preview":
                asyncio.create_task(update_preview())

    @kb.add("down")
    def _(event):
        skills = state.get_current_list()
        if skills:
            idx = state.get_current_index()
            state.set_current_index((idx + 1) % len(skills))
            if state.view_mode == "preview":
                asyncio.create_task(update_preview())

    @kb.add("right")
    def _(event):
        if state.view_mode == "list":
            state.view_mode = "preview"
            asyncio.create_task(update_preview())

    @kb.add("left")
    @kb.add("escape")
    def _(event):
        if state.view_mode == "preview":
            state.view_mode = "list"
        else:
            event.app.exit()

    @kb.add("space")
    def _(event):
        idx = state.get_current_index()
        selected = state.get_selected_set()
        if idx in selected:
            selected.remove(idx)
        else:
            selected.add(idx)

    @kb.add("q")
    @kb.add("c-c")
    def _(event):
        event.app.exit()

    @kb.add("enter")
    def _(event):
        if state.current_tab == "discover":
            # Install selected or current
            selected_indices = state.selected_discover
            if not selected_indices:
                selected_indices = {state.discover_index}

            to_install = [
                state.discover_skills[i]
                for i in selected_indices
                if i < len(state.discover_skills)
            ]
            event.app.exit()

            for s in to_install:
                repo, path = get_repo_and_path(s)
                print(f"Installing [magenta]{s.get('name')}[/magenta]...")
                add_skill(repo=repo, path=path)
        else:
            # Maybe re-sync or something?
            pass

    @kb.add("d")
    def _(event):
        if state.current_tab == "installed":
            # Uninstall selected or current
            selected_indices = state.selected_installed
            if not selected_indices:
                selected_indices = {state.installed_index}

            skills = state.get_current_list()
            to_remove = [skills[i] for i in selected_indices if i < len(skills)]

            # Filter for managed skills (unmanaged can't be 'removed' via lockfile)
            managed_to_remove = [s for s in to_remove if "repo" in s]

            if managed_to_remove:
                event.app.exit()
                for s in managed_to_remove:
                    print(f"Removing [red]{s['name']}[/red]...")
                    remove_skill(s["name"])
            else:
                # TODO: show message that unmanaged can't be removed this way
                pass

    def get_header_text():
        tabs = []
        for tab in ["installed", "discover"]:
            if state.current_tab == tab:
                tabs.append(f"<reverse>  {tab.upper()}  </reverse>")
            else:
                tabs.append(f"  {tab.upper()}  ")

        return HTML("".join(tabs))

    def get_sidebar_text():
        lines = []
        skills = state.get_current_list()
        idx = state.get_current_index()
        selected = state.get_selected_set()

        if not skills:
            return HTML("<ansigray>  No skills found.</ansigray>")

        for i, skill in enumerate(skills):
            name = skill.get("name", "Unknown")
            repo = skill.get("repo", "unmanaged")
            installs = skill.get("installs", 0)

            line = render_skill_line(
                name=name,
                repo=repo,
                installs=installs,
                is_selected=i in selected,
                is_current=i == idx,
                width=38,
            )
            lines.append(line)
        return HTML("\n".join(lines))

    def get_preview_text():
        if state.view_mode == "list":
            return HTML("<ansigray>Press [Right] to preview SKILL.md</ansigray>")

        content = state.preview_content
        return format_markdown_for_tui(content)

    def get_footer_text():
        skills = state.get_current_list()
        selected = state.get_selected_set()
        count = len(skills)
        sel_count = len(selected)

        shortcuts = "<b>Tab</b>: Switch | <b>Space</b>: Select | <b>Right</b>: Preview | <b>q</b>: Quit"
        if state.current_tab == "installed":
            shortcuts += " | <b>d</b>: Remove"
        else:
            shortcuts += " | <b>Enter</b>: Install"

        return HTML(f" {sel_count}/{count} selected | {shortcuts}")

    layout = Layout(
        HSplit(
            [
                Window(
                    content=FormattedTextControl(get_header_text),
                    height=1,
                    align=WindowAlign.CENTER,
                ),
                Window(height=1, char="-"),
                VSplit(
                    [
                        Window(
                            content=FormattedTextControl(get_sidebar_text), width=40
                        ),
                        Window(width=1, char="|"),
                        Window(
                            content=FormattedTextControl(get_preview_text),
                            wrap_lines=True,
                        ),
                    ]
                ),
                Window(height=1, char="-"),
                Window(content=FormattedTextControl(get_footer_text), height=1),
            ]
        )
    )

    app = Application(layout=layout, key_bindings=kb, full_screen=True)
    app.run()


if __name__ == "__main__":
    tui_command()
