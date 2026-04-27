import json
import urllib.parse
import urllib.request
import xml.sax.saxutils as saxutils
from typing import Any, Dict, List, Tuple

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


def render_skill_line(
    name: str,
    repo: str,
    installs: int,
    is_selected: bool,
    is_current: bool,
    width: int = 48,
) -> str:
    """Render a single line for a skill list in the TUI."""
    prefix = "[x]" if is_selected else "[ ]"
    pointer = ">" if is_current else " "
    formatted_installs = f"[{installs:,}]"

    # Main label: name (repo)
    label = f"{name} ({repo})"

    # Calculate how much space we have for the label
    # pointer(2) + prefix(4) + padding(min 1) + installs(len)
    fixed_parts_len = 2 + 4 + 1 + len(formatted_installs)
    available_for_label = width - fixed_parts_len

    if len(label) > available_for_label:
        label = label[: max(0, available_for_label - 3)] + "..."

    padding_len = max(0, width - (2 + 4 + len(label) + len(formatted_installs)))
    padding = " " * padding_len

    safe_label = saxutils.escape(label)
    safe_installs = saxutils.escape(formatted_installs)

    content = f"{pointer} {prefix} <b>{safe_label}</b>{padding}<ansigreen>{safe_installs}</ansigreen>"

    if is_current:
        return f"<reverse>{content}</reverse>"
    return content
