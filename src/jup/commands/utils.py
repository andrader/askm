import json
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from rich import print

GH_PREFIX = "gh"  # Used to namespace GitHub sources in storage
LOCAL_SOURCE_TYPE = "local"
GITHUB_SOURCE_TYPE = "github"


def rel_home(p):
    return str(p).replace(str(Path.home()), "~")


def fetch_remote_skill_md(
    repo: str, skill_name: Optional[str] = None, internal_path: str = ""
) -> str:
    """Fetch SKILL.md content from GitHub."""
    # Try different common paths for SKILL.md
    paths_to_try = []
    base_path = internal_path.strip("/")

    if skill_name:
        # ALWAYS try standard location first
        standard_path = f"skills/{skill_name}/SKILL.md"
        paths_to_try.append(standard_path)

        if base_path:
            # If internal_path points to the skill directory itself
            p1 = f"{base_path}/SKILL.md"
            if p1 not in paths_to_try:
                paths_to_try.append(p1)
            # If internal_path points to a parent directory
            p2 = f"{base_path}/{skill_name}/SKILL.md"
            if p2 not in paths_to_try:
                paths_to_try.append(p2)

        # Common fallback locations
        others = [
            f".claude/skills/{skill_name}/SKILL.md",
            f"{skill_name}/SKILL.md",
            "SKILL.md",
        ]
        for p in others:
            if p not in paths_to_try:
                paths_to_try.append(p)
    else:
        if base_path:
            paths_to_try.append(f"{base_path}/SKILL.md")
            paths_to_try.append("SKILL.md")
        else:
            paths_to_try.append("SKILL.md")
            paths_to_try.append("skills/SKILL.md")
            paths_to_try.append(".claude/skills/SKILL.md")

    for p in paths_to_try:
        url = f"https://raw.githubusercontent.com/{repo}/main/{p}"
        try:
            req = urllib.request.Request(url)
            req.add_header("User-Agent", "jup-cli")
            with urllib.request.urlopen(req) as response:
                return response.read().decode()
        except Exception:
            # Try master branch if main fails
            url = f"https://raw.githubusercontent.com/{repo}/master/{p}"
            try:
                req = urllib.request.Request(url)
                req.add_header("User-Agent", "jup-cli")
                with urllib.request.urlopen(req) as response:
                    return response.read().decode()
            except Exception:
                continue

    # Fallback: Recursive search using GitHub API
    if skill_name:
        try:
            api_url = f"https://api.github.com/repos/{repo}/git/trees/main?recursive=1"
            req = urllib.request.Request(api_url)
            req.add_header("User-Agent", "jup-cli")
            with urllib.request.urlopen(req) as response:
                tree_data = json.loads(response.read().decode())
                for item in tree_data.get("tree", []):
                    path = item["path"]
                    # Search for repo/**/skill-name/SKILL.md
                    if (
                        path.endswith(f"/{skill_name}/SKILL.md")
                        or path == f"{skill_name}/SKILL.md"
                    ):
                        if path in paths_to_try:
                            continue  # Already tried

                        # Fetch the found path
                        url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
                        try:
                            req = urllib.request.Request(url)
                            req.add_header("User-Agent", "jup-cli")
                            with urllib.request.urlopen(req) as response:
                                return response.read().decode()
                        except Exception:
                            # Try master as well
                            url = f"https://raw.githubusercontent.com/{repo}/master/{path}"
                            try:
                                req = urllib.request.Request(url)
                                req.add_header("User-Agent", "jup-cli")
                                with urllib.request.urlopen(req) as response:
                                    return response.read().decode()
                            except Exception:
                                continue
        except Exception:
            # Fallback to master branch tree if main fails
            try:
                api_url = (
                    f"https://api.github.com/repos/{repo}/git/trees/master?recursive=1"
                )
                req = urllib.request.Request(api_url)
                req.add_header("User-Agent", "jup-cli")
                with urllib.request.urlopen(req) as response:
                    tree_data = json.loads(response.read().decode())
                    for item in tree_data.get("tree", []):
                        path = item["path"]
                        if (
                            path.endswith(f"/{skill_name}/SKILL.md")
                            or path == f"{skill_name}/SKILL.md"
                        ):
                            if path in paths_to_try:
                                continue
                            url = f"https://raw.githubusercontent.com/{repo}/master/{path}"
                            req = urllib.request.Request(url)
                            req.add_header("User-Agent", "jup-cli")
                            with urllib.request.urlopen(req) as response:
                                return response.read().decode()
            except Exception:
                pass

    return f"SKILL.md not found in {repo}.\nTried paths:\n- " + "\n- ".join(
        paths_to_try
    )


def run_git_clone(repo_url: str, dest_dir: Path, **kwargs):
    str_kwargs_flattened = []
    for k, v in kwargs.items():
        if len(k) == 1:
            str_kwargs_flattened.append(f"-{k}")
        elif len(k) > 1:
            str_kwargs_flattened.append(f"--{k.replace('_', '-')}")
        else:
            continue

        if isinstance(v, bool):
            continue  # Flags don't have a value
        str_kwargs_flattened.append(str(v))

    try:
        subprocess.run(
            ["git", "clone", *str_kwargs_flattened, repo_url, str(dest_dir)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone: {e.stderr.decode()}")
        raise
