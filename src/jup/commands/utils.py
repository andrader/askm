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
        # Standard location
        paths_to_try.append(f"skills/{skill_name}/SKILL.md")

        if base_path:
            # If internal_path points to the skill directory itself
            paths_to_try.append(f"{base_path}/SKILL.md")
            # If internal_path points to a parent directory
            p_full = f"{base_path}/{skill_name}/SKILL.md"
            if p_full not in paths_to_try:
                paths_to_try.append(p_full)

        # Root location fallback
        if "SKILL.md" not in paths_to_try:
            paths_to_try.append("SKILL.md")
    else:
        if base_path:
            paths_to_try.append(f"{base_path}/SKILL.md")
        if "SKILL.md" not in paths_to_try:
            paths_to_try.append("SKILL.md")

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
    # Whitelist of allowed flags and options to prevent injection
    ALLOWED_FLAGS = {"depth", "branch", "single_branch", "no_tags", "quiet"}
    str_kwargs_flattened = []

    for k, v in kwargs.items():
        if k not in ALLOWED_FLAGS:
            if k == "verbose":
                continue  # ignore
            # Potentially unsafe argument
            continue

        flag_name = f"--{k.replace('_', '-')}"
        str_kwargs_flattened.append(flag_name)

        if isinstance(v, bool):
            if v is False:
                str_kwargs_flattened.pop()  # remove the flag if it was False
            continue

        # Sanitize value - basic check for leading hyphens to avoid being treated as flags
        val = str(v)
        if val.startswith("-"):
            print(f"⚠️  Ignoring potentially unsafe git value: [red]{val}[/red]")
            str_kwargs_flattened.pop()
            continue

        str_kwargs_flattened.append(val)

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


def run_git_pull(repo_dir: Path):
    """Run git pull in the specified directory."""
    try:
        subprocess.run(
            ["git", "-C", str(repo_dir), "pull"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to pull in {rel_home(repo_dir)}: {e.stderr.decode()}")
        raise


def is_path_in_harness_dir(path: Path, config) -> str | None:
    resolved_path = path.resolve()
    from ..config import get_all_harnesses

    all_harnesses = get_all_harnesses(config)
    for name, harness in all_harnesses.items():
        for loc in [harness.global_location, harness.local_location]:
            harness_path = Path(loc).expanduser().resolve()
            if resolved_path == harness_path or harness_path in resolved_path.parents:
                return name
    return None
