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
from prompt_toolkit.widgets import TextArea
from pygments.lexers.markup import MarkdownLexer
from prompt_toolkit.lexers import PygmentsLexer
from rich import print

from .list import get_installed_skills_data
from .utils_tui import (
    search_skills_registry,
    get_repo_and_path,
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
        self.settings = []

        # Selection/Focus
        self.indices = {tab: 0 for tab in self.tabs}
        self.selected = {tab: set() for tab in self.tabs}

        self.is_loading = False
        self.search_query = "latest"

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


async def async_tui_main():
    state = TUIState()
    kb = KeyBindings()

    # Preview Area - Use TextArea for better scrolling
    preview_area = TextArea(
        text="Loading...",
        read_only=True,
        lexer=PygmentsLexer(MarkdownLexer),
        scrollbar=True,
        line_numbers=False,
    )

    # --- Data Loading ---

    def load_installed_data():
        data = get_installed_skills_data()
        state.installed_skills = data["installed"]
        state.unmanaged_skills = data["unmanaged"]

    async def load_discover_data(query="latest"):
        state.is_loading = True
        # Fetching in a thread to keep UI responsive
        loop = asyncio.get_running_loop()
        state.discover_skills = await loop.run_in_executor(
            None, search_skills_registry, query
        )
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

        if not lst or idx >= len(lst):
            preview_area.text = "No item selected."
            return

        item = lst[idx]

        if state.current_tab == "installed":
            header_lines = []
            header_lines.append(f"# {item['name']}")
            header_lines.append(f"**Scope**: {item.get('scope', 'unknown')}")
            header_lines.append(f"**Category**: {item.get('category', 'misc')}")

            if "repo" in item:
                header_lines.append(f"**Repo**: {item['repo']}")
                header_lines.append(f"**Source Path**: {item['source_path']}")
                header_lines.append("\n**Status in Harnesses:**")
                for h_name, info in item.get("status", {}).items():
                    symbol = "🔗 (Symlink)" if info["is_symlink"] else "📁 (Dir)"
                    status = "✅ OK" if info["exists"] else "❌ Missing"
                    if info["is_broken"]:
                        status = "⛓️‍💥 Broken"
                    header_lines.append(
                        f"- {h_name}: {status} {symbol} at `{info['path']}`"
                    )
            else:
                header_lines.append(f"**Path**: {item['path']} (Unmanaged)")

            header_lines.append("---")

            source_path = item.get("source_path") or item.get("path")
            content = ""
            if source_path:
                p = Path(source_path).expanduser()
                skill_md = p / "SKILL.md" if p.is_dir() else p
                if skill_md.exists():
                    content = await asyncio.get_running_loop().run_in_executor(
                        None, skill_md.read_text
                    )
                else:
                    content = f"*SKILL.md not found at {source_path}*"

            preview_area.text = "\n".join(header_lines) + "\n\n" + content

        elif state.current_tab == "discover":
            repo, internal_path = get_repo_and_path(item)
            preview_area.text = f"Fetching remote SKILL.md for {repo}...\n\n"
            meta = [
                f"# {item.get('name')}",
                f"**Repo**: {repo}",
                f"**Installs**: {item.get('installs', 0):,}",
                "---",
            ]

            loop = asyncio.get_running_loop()
            md_content = await loop.run_in_executor(
                None, fetch_remote_skill_md, repo, item.get("name"), internal_path
            )
            preview_area.text = "\n".join(meta) + "\n\n" + md_content

        elif state.current_tab == "agents":
            lines = [
                f"# Agent Harness: {item['name']}",
                f"**Global Path**: `{item['global_location']}`",
                f"**Local Path**: `{item['local_location']}`",
                "---",
                "Skills in this harness are managed via `jup sync`.",
            ]
            preview_area.text = "\n".join(lines)

        elif state.current_tab == "settings":
            key, val = item
            lines = [
                f"# Setting: {key}",
                "---",
                f"**Value**: `{json.dumps(val, indent=2)}`",
            ]
            preview_area.text = "\n".join(lines)

    # --- Keybindings ---

    @kb.add("tab")
    def _(event):
        state.current_tab_idx = (state.current_tab_idx + 1) % len(state.tabs)
        if state.current_tab == "discover":
            asyncio.create_task(load_discover_data(state.search_query))
        elif state.current_tab == "agents":
            load_agents_data()
        elif state.current_tab == "settings":
            load_settings_data()
        elif state.current_tab == "installed":
            load_installed_data()

        asyncio.create_task(update_preview())

    @kb.add("up")
    def _(event):
        state.set_current_index(state.get_current_index() - 1)
        asyncio.create_task(update_preview())

    @kb.add("down")
    def _(event):
        state.set_current_index(state.get_current_index() + 1)
        asyncio.create_task(update_preview())

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
            selected_indices = state.selected["discover"] or {state.indices["discover"]}
            to_install = [
                state.discover_skills[i]
                for i in selected_indices
                if i < len(state.discover_skills)
            ]
            event.app.exit(result=("install", to_install))
        elif state.current_tab == "installed":
            pass

    @kb.add("d")
    def _(event):
        if state.current_tab == "installed":
            selected_indices = state.selected["installed"] or {
                state.indices["installed"]
            }
            skills = state.get_current_list()
            to_remove = [
                skills[i]
                for i in selected_indices
                if i < len(skills) and "repo" in skills[i]
            ]
            if to_remove:
                event.app.exit(result=("remove", to_remove))

    # --- Rendering Helpers ---

    def get_header_text():
        tabs = [
            f"<reverse>  {t.upper()}  </reverse>"
            if state.current_tab == t
            else f"  {t.upper()}  "
            for t in state.tabs
        ]
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
                line = render_skill_line(
                    item.get("name", "Unknown"),
                    item.get("repo", "unmanaged"),
                    item.get("installs", 0),
                    i in selected,
                    i == idx,
                    width=38,
                )
            else:
                name = (
                    item
                    if isinstance(item, str)
                    else (item["name"] if isinstance(item, dict) else item[0])
                )
                pointer = ">" if i == idx else " "
                line = f"{pointer} [ ] <b>{name}</b>"
                if i == idx:
                    line = f"<reverse>{line}</reverse>"
            lines.append(line)
        return HTML("\n".join(lines))

    def get_footer_text():
        count = len(state.get_current_list())
        sel_count = len(state.get_selected_set())
        shortcuts = "<b>Tab</b>: Switch | <b>Space</b>: Select | <b>q</b>: Quit"
        return HTML(f" {sel_count}/{count} | {shortcuts}")

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
                            content=FormattedTextControl(get_sidebar_text),
                            width=Dimension(weight=4),
                        ),
                        Window(width=1, char="|"),
                        Window(content=preview_area.control, width=Dimension(weight=6)),
                    ]
                ),
                Window(height=1, char="-"),
                Window(content=FormattedTextControl(get_footer_text), height=1),
            ]
        )
    )

    app = Application(layout=layout, key_bindings=kb, full_screen=True)

    # Load initial preview
    asyncio.create_task(update_preview())

    result = await app.run_async()
    return result


def tui_command():
    """Interactive TUI for managing skills."""
    try:
        result = asyncio.run(async_tui_main())
        if result:
            action, items = result
            if action == "install":
                for s in items:
                    repo, path = get_repo_and_path(s)
                    print(f"Installing [magenta]{s.get('name')}[/magenta]...")
                    add_skill(repo=repo, path=path)
            elif action == "remove":
                for s in items:
                    print(f"Removing [red]{s['name']}[/red]...")
                    remove_skill(s["name"])
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    tui_command()
