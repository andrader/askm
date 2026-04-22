import json
import urllib.parse
import urllib.request
from pathlib import Path

import typer
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.tree import Tree

from .utils import (
    fetch_remote_skill_md,
    rel_home,
)


def show_skill(
    target: str = typer.Argument(
        ..., help="GitHub repository (owner/repo) or local skills directory."
    ),
    skill: str = typer.Option(
        None, "--skill", help="[GitHub only] Specific skill name to show"
    ),
    verbose: bool = False,
):
    """Show the content of SKILL.md and the directory structure of a skill."""
    console = Console()

    local_path = Path(target).expanduser()
    if local_path.exists():
        # Local source
        if local_path.is_file():
            if local_path.name == "SKILL.md":
                content = local_path.read_text()
                console.print(Markdown(content))
            else:
                print(f"[red]{target} is a file but not SKILL.md[/red]")
        else:
            skill_md = local_path / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text()
                console.print(Markdown(content))
            else:
                print(f"[yellow]No SKILL.md found in {target}[/yellow]")

            # Show tree
            def add_to_tree(path: Path, tree: Tree):
                for item in sorted(path.iterdir()):
                    if item.name.startswith(".") or item.name == "__pycache__":
                        continue
                    if item.is_dir():
                        branch = tree.add(f"[bold blue]{item.name}/[/bold blue]")
                        add_to_tree(item, branch)
                    else:
                        tree.add(item.name)

            tree = Tree(f"[bold cyan]{rel_home(local_path)}[/bold cyan]")
            add_to_tree(local_path, tree)
            console.print(tree)
    else:
        # Remote source
        if "/" not in target:
            print("[red]Target must be a local path or 'owner/repo'[/red]")
            raise typer.Exit(code=1)

        repo = target
        print(f"Fetching information for [cyan]{repo}[/cyan]...")

        content = fetch_remote_skill_md(repo, skill)
        console.print(Markdown(content))

        # Show remote tree using GitHub API
        try:
            api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
            req = urllib.request.Request(api_url)
            # Add User-Agent to avoid 403
            req.add_header("User-Agent", "jup-cli")
            with urllib.request.urlopen(req) as response:
                tree_data = json.loads(response.read().decode())

            tree = Tree(f"[bold cyan]github.com/{repo}[/bold cyan]")
            nodes = {"": tree}

            # GitHub returns flat list of paths
            for item in tree_data.get("tree", []):
                path = item["path"]
                if path.startswith(".") or "/." in path or "__pycache__" in path:
                    continue

                parts = path.split("/")
                parent_path = "/".join(parts[:-1])
                name = parts[-1]

                if parent_path in nodes:
                    if item["type"] == "tree":
                        nodes[path] = nodes[parent_path].add(
                            f"[bold blue]{name}/[/bold blue]"
                        )
                    else:
                        nodes[parent_path].add(name)

            console.print(tree)
        except Exception as e:
            if verbose:
                print(f"[yellow]Could not fetch remote tree: {e}[/yellow]")
            else:
                print(
                    "[yellow]Could not fetch remote tree (GitHub API rate limit or private repo?)[/yellow]"
                )
