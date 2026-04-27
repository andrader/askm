import json
import urllib.parse
import urllib.request
import xml.sax.saxutils as saxutils
from typing import Any, Dict, List, Tuple, Optional

from prompt_toolkit.formatted_text import PygmentsTokens
from pygments.lexers.markup import MarkdownLexer


def search_skills_registry(query: str) -> List[Dict[str, Any]]:
    """Search for skills in the skills.sh registry."""
    api_url = f"https://skills.sh/api/search?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(api_url)
        req.add_header("User-Agent", "jup-cli")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
        return data.get("skills", [])
    except Exception:
        return []


def get_repo_and_path(skill: Dict[str, Any]) -> Tuple[str, str]:
    """Extract repo and internal path from a registry skill object."""
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


def format_markdown_for_tui(content: str) -> PygmentsTokens:
    """Format markdown text for prompt_toolkit using Pygments."""
    return PygmentsTokens(list(MarkdownLexer().get_tokens(content)))


def render_skill_header(width: int = 44) -> str:
    """Render the header for the skill list columns."""
    #   [ ] S CAT Skill Name (Repo) A
    return "      <ansicyan>S CAT Skill Name (Repo)      A</ansicyan>"


def render_skill_line(
    name: str,
    repo: str,
    installs: int = 0,
    is_selected: bool = False,
    is_current: bool = False,
    width: int = 44,
    scope: str = "",
    category: str = "",
    harnesses: Optional[List[str]] = None,
) -> str:
    """Render a single line for a skill list in the TUI with multiple columns."""
    prefix = "[x]" if is_selected else "[ ]"
    pointer = ">" if is_current else " "

    # Shorten Scope (U/L)
    scope_char = scope[0].upper() if scope else "?"

    # Shorten Category (3 chars)
    cat_short = (category[:3].upper() if category else "---").ljust(3)

    # Agent count
    agent_count = str(len(harnesses)) if harnesses else "0"

    # Colorize
    scope_colored = f"<ansiyellow>{scope_char}</ansiyellow>"
    cat_colored = f"<ansiblue>{cat_short}</ansiblue>"
    agent_colored = f"<ansigreen>{agent_count}</ansigreen>"

    # Main label: name (repo)
    if repo and repo != "unmanaged":
        label = f"{name} ({repo})"
    else:
        label = name

    # Calculate space for label
    # pointer(2) + prefix(4) + scope(2) + cat(4) + agent(2)
    meta_len = 2 + 4 + 2 + 4 + 2
    available_for_label = width - meta_len

    if len(label) > available_for_label:
        if len(name) <= available_for_label:
            label = name
        else:
            label = name[: max(0, available_for_label - 3)] + "..."

    # Align label to fill space before agent count
    padding_len = max(0, available_for_label - len(label))
    padding = " " * padding_len

    safe_label = saxutils.escape(label)

    content = f"{pointer} {prefix} {scope_colored} {cat_colored} <b>{safe_label}</b>{padding} {agent_colored}"

    if is_current:
        return f"<reverse>{content}</reverse>"
    return content
