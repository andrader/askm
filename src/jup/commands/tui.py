import asyncio
import json
from pathlib import Path

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
from prompt_toolkit.layout.dimension import Dimension
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
from ..config import get_config, get_all_harnesses
from ..core.filesystem import rel_home


class TUIState:
    def __init__(self):
        self.tabs = ["installed", "discover", "agents", "settings"]
        self.current_tab_idx = 0

        # Data
        self.installed_skills = []
        self.unmanaged_skills = []
        self.discover_skills = []
        self.agents = []
        self.settings = []  # List of (key, value)

        # Selection/Focus
        self.indices = {tab: 0 for tab in self.tabs}
        self.selected = {tab: set() for tab in self.tabs}

        self.preview_content = "Welcome to jup TUI"
        self.is_loading = False
        self.search_query = "latest"

        # Scroll offset for preview
        self.preview_line_offset = 0

    @property
    def current_tab(self):
        return self.tabs[self.current_tab_idx]

    def get_current_list(self):
        if self.current_tab == "installed":
            return self.installed_skills + self.unmanaged_skills
        elif self.current_tab == "discover":
            return self.discover_skills
        elif self.current_tab == "agents":
            return self.agents
        elif self.current_tab == "settings":
            return self.settings
        return []

    def get_current_index(self):
        return self.indices[self.current_tab]

    def set_current_index(self, idx):
        lst = self.get_current_list()
        if not lst:
            self.indices[self.current_tab] = 0
        else:
            self.indices[self.current_tab] = idx % len(lst)

    def get_selected_set(self):
        return self.selected[self.current_tab]


def tui_command():
    """Interactive TUI for managing skills."""
    state = TUIState()
    kb = KeyBindings()

    # --- Data Loading ---

    def load_installed_data():
        data = get_installed_skills_data()
        state.installed_skills = data["installed"]
        state.unmanaged_skills = data["unmanaged"]

    def load_discover_data(query="latest"):
        state.is_loading = True
        state.discover_skills = search_skills_registry(query)
        state.is_loading = False

    def load_agents_data():
        config = get_config()
        all_h = get_all_harnesses(config)
        state.agents = []
        for name, h in all_h.items():
            state.agents.append(
                {
                    "name": name,
                    "global_location": rel_home(Path(h.global_location)),
                    "local_location": rel_home(Path(h.local_location)),
                }
            )

    def load_settings_data():
        config = get_config()
        state.settings = list(config.model_dump().items())

    # Initial Load
    load_installed_data()

    # --- UI Logic ---

    async def update_preview():
        idx = state.get_current_index()
        lst = state.get_current_list()
        state.preview_line_offset = 0  # Reset scroll

        if not lst or idx >= len(lst):
            state.preview_content = "No item selected."
            return

        item = lst[idx]

        if state.current_tab == "installed":
            # Header with metadata
            header_lines = []
            header_lines.append(f"# {item['name']}")
            header_lines.append(f"**Scope**: {item.get('scope', 'unknown')}")
            header_lines.append(f"**Category**: {item.get('category', 'misc')}")

            if "repo" in item:
                header_lines.append(f"**Repo**: {item['repo']}")
                header_lines.append(f"**Source Path**: {item['source_path']}")

                # Status / Harnesses
                header_lines.append("\n**Status in Harnesses:**")
                for h_name, info in item.get("status", {}).items():
                    symbol = "🔗 (Symlink)" if info["is_symlink"] else "📁 (Dir)"
                    if info["is_broken"]:
                        status = "⛓️‍💥 Broken"
                    elif info["exists"]:
                        status = "✅ OK"
                    else:
                        status = "❌ Missing"
                    header_lines.append(
                        f"- {h_name}: {status} {symbol} at `{info['path']}`"
                    )
            else:
                header_lines.append(f"**Path**: {item['path']} (Unmanaged)")

            header_lines.append("---")

            # Read local SKILL.md
            source_path = item.get("source_path") or item.get("path")
            content = ""
            if source_path:
                p = Path(source_path).expanduser()
                skill_md = p / "SKILL.md" if p.is_dir() else p
                if skill_md.exists() and skill_md.is_file():
                    content = skill_md.read_text()
                else:
                    content = f"*SKILL.md not found at {source_path}*"

            state.preview_content = "\n".join(header_lines) + "\n\n" + content

        elif state.current_tab == "discover":
            repo, internal_path = get_repo_and_path(item)
            state.preview_content = f"Fetching remote SKILL.md for {repo}...\n\n"
            # Metadata
            meta = [
                f"# {item.get('name')}",
                f"**Repo**: {repo}",
                f"**Installs**: {item.get('installs', 0):,}",
                "---",
            ]

            # In a real app we'd use a thread, but fetch_remote_skill_md is fast enough for now
            # or we could make it a proper async task if the user experience suffers.
            md_content = fetch_remote_skill_md(repo, item.get("name"), internal_path)
            state.preview_content = "\n".join(meta) + "\n\n" + md_content

        elif state.current_tab == "agents":
            lines = [
                f"# Agent Harness: {item['name']}",
                f"**Global Path**: `{item['global_location']}`",
                f"**Local Path**: `{item['local_location']}`",
                "---",
                "Skills in this harness are managed via `jup sync`.",
            ]
            state.preview_content = "\n".join(lines)

        elif state.current_tab == "settings":
            key, val = item
            lines = [
                f"# Setting: {key}",
                "---",
                f"**Value**: `{json.dumps(val, indent=2)}`",
            ]
            state.preview_content = "\n".join(lines)

    # --- Keybindings ---

    @kb.add("tab")
    def _(event):
        state.current_tab_idx = (state.current_tab_idx + 1) % len(state.tabs)
        if state.current_tab == "discover" and not state.discover_skills:
            load_discover_data(state.search_query)
        elif state.current_tab == "agents":
            load_agents_data()
        elif state.current_tab == "settings":
            load_settings_data()
        elif state.current_tab == "installed":
            load_installed_data()

        asyncio.create_task(update_preview())
        event.app.invalidate()

    @kb.add("up")
    def _(event):
        state.set_current_index(state.get_current_index() - 1)
        asyncio.create_task(update_preview())

    @kb.add("down")
    def _(event):
        state.set_current_index(state.get_current_index() + 1)
        asyncio.create_task(update_preview())

    @kb.add("pageup")
    def _(event):
        state.preview_line_offset = max(0, state.preview_line_offset - 10)

    @kb.add("pagedown")
    def _(event):
        state.preview_line_offset += 10

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
            selected_indices = state.selected["discover"]
            if not selected_indices:
                selected_indices = {state.indices["discover"]}

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

    @kb.add("d")
    def _(event):
        if state.current_tab == "installed":
            selected_indices = state.selected["installed"]
            if not selected_indices:
                selected_indices = {state.indices["installed"]}

            skills = state.get_current_list()
            to_remove = [skills[i] for i in selected_indices if i < len(skills)]
            managed_to_remove = [s for s in to_remove if "repo" in s]

            if managed_to_remove:
                event.app.exit()
                for s in managed_to_remove:
                    print(f"Removing [red]{s['name']}[/red]...")
                    remove_skill(s["name"])

    # --- Rendering ---

    def get_header_text():
        tabs = []
        for i, tab in enumerate(state.tabs):
            if state.current_tab_idx == i:
                tabs.append(f"<reverse>  {tab.upper()}  </reverse>")
            else:
                tabs.append(f"  {tab.upper()}  ")
        return HTML("".join(tabs))

    def get_sidebar_text():
        lines = []
        lst = state.get_current_list()
        idx = state.get_current_index()
        selected = state.get_selected_set()

        if not lst:
            return HTML("<ansigray>  No items found.</ansigray>")

        for i, item in enumerate(lst):
            if state.current_tab in ["installed", "discover"]:
                name = item.get("name", "Unknown")
                repo = item.get("repo", "unmanaged")
                installs = item.get("installs", 0)
                line = render_skill_line(
                    name, repo, installs, i in selected, i == idx, width=38
                )
            elif state.current_tab == "agents":
                name = item["name"]
                pointer = ">" if i == idx else " "
                line = f"{pointer} [ ] <b>{name}</b>"
                if i == idx:
                    line = f"<reverse>{line}</reverse>"
            elif state.current_tab == "settings":
                name = item[0]
                pointer = ">" if i == idx else " "
                line = f"{pointer} [ ] <b>{name}</b>"
                if i == idx:
                    line = f"<reverse>{line}</reverse>"

            lines.append(line)
        return HTML("\n".join(lines))

    def get_preview_text():
        content = state.preview_content
        full_tokens = format_markdown_for_tui(content)

        # Simple scroll implementation: slice the lines
        # This is a bit complex with PygmentsTokens (list of (Token, text))
        # We'd need to convert to text lines, slice, then back to tokens or use a real TextArea.
        # For now, let's just show it. prompt-toolkit Windows handle scrolling if they have a content control.
        return full_tokens

    def get_footer_text():
        count = len(state.get_current_list())
        sel_count = len(state.get_selected_set())
        shortcuts = "<b>Tab</b>: Switch | <b>Space</b>: Select | <b>PgUp/Dn</b>: Scroll | <b>q</b>: Quit"
        return HTML(f" {sel_count}/{count} | {shortcuts}")

    # Start update task for initial selection
    asyncio.create_task(update_preview())

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
                        # 40% Width for sidebar
                        Window(
                            content=FormattedTextControl(get_sidebar_text),
                            width=Dimension(weight=4),
                        ),
                        Window(width=1, char="|"),
                        # 60% Width for preview
                        Window(
                            content=FormattedTextControl(get_preview_text),
                            wrap_lines=True,
                            # We can use the window's vertical_scroll variable indirectly
                            # by wrapping this in a container that supports scrolling,
                            # but FormattedTextControl is static.
                            # Let's use a read-only TextArea for the preview to get native scrolling.
                            width=Dimension(weight=6),
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
