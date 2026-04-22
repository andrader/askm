
import urllib.parse
from pathlib import Path
from typing import Optional

def parse_repo_arg(repo_arg: str):
    """
    Parses the repo argument.
    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo/tree/main/path/to/skill
    - owner/repo
    - owner/repo/path/to/skill
    - @version suffix on any of the above
    Returns (owner, repo, path, version, is_url) or None if local.
    """
    version = None
    if "@" in repo_arg and not repo_arg.startswith("@"):
        parts = repo_arg.rsplit("@", 1)
        repo_arg = parts[0]
        version = parts[1]

    if repo_arg.startswith("http://") or repo_arg.startswith("https://"):
        parsed = urllib.parse.urlparse(repo_arg)
        if parsed.netloc == "github.com":
            path_parts = [p for p in parsed.path.split("/") if p]
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1]
                if repo.endswith(".git"):
                    repo = repo[:-4]
                subpath = None
                if len(path_parts) > 4 and path_parts[2] == "tree":
                    # We ignore the branch part (path_parts[3]) for the subpath itself
                    # but if version is not provided, we could use it. For now just extract path.
                    subpath = "/".join(path_parts[4:])
                    if not version:
                        version = path_parts[3]
                return owner, repo, subpath, version, True
    else:
        # Check if it's owner/repo format
        # Normalize: strip only trailing slashes
        repo_arg_norm = repo_arg.rstrip("/")
        parts = repo_arg_norm.split("/")

        # If it starts with /, it's an absolute path, so it's local
        if repo_arg.startswith("/"):
            return None

        if len(parts) >= 2 and not Path(repo_arg).expanduser().exists():
            owner = parts[0]
            repo = parts[1]
            subpath = "/".join(parts[2:]) if len(parts) > 2 else None
            return owner, repo, subpath, version, False
    return None

test_cases = [
    # 1. URLs with complex fragments, query params, or multiple slashes
    "https://github.com/owner/repo//",
    "https://github.com/owner/repo?query=1",
    "https://github.com/owner/repo#fragment",
    "https://github.com/owner/repo/tree/main/path//to/skill",
    
    # 2. SSH-style git URLs vs HTTPS URLs
    "git@github.com:owner/repo.git",
    "ssh://git@github.com/owner/repo.git",
    
    # 3. Redundant @version suffixes
    "owner/repo@v1@v2",
    "https://github.com/owner/repo@v1@v2",
    
    # 4. Interaction between local paths and GitHub shorthand
    "owner/repo", # will test with and without local dir
    
    # Extra: multiple slashes in shorthand
    "owner//repo",
    "owner/repo//path",
]

for tc in test_cases:
    res = parse_repo_arg(tc)
    print(f"Input: {tc} => Result: {res}")

# Test local path interaction
import os
os.makedirs("owner/repo", exist_ok=True)
print(f"Input (local dir exists): owner/repo => Result: {parse_repo_arg('owner/repo')}")
os.removedirs("owner/repo")
