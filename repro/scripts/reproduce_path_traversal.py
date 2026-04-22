import urllib.parse
from pathlib import Path

def parse_repo_arg(repo_arg: str):
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
                subpath = None
                if len(path_parts) > 4 and path_parts[2] == "tree":
                    subpath = "/".join(path_parts[4:])
                    if not version:
                        version = path_parts[3]
                return owner, repo, subpath, version, True
    else:
        parts = repo_arg.split("/")
        if len(parts) >= 2 and not Path(repo_arg).expanduser().exists():
            owner = parts[0]
            repo = parts[1]
            subpath = "/".join(parts[2:]) if len(parts) > 2 else None
            return owner, repo, subpath, version, False
    return None

test_repos = [
    "owner/repo",
    "../../..",
    "owner/repo/../../tmp",
    "https://github.com/owner/repo/tree/main/path/to/skill",
    "https://github.com/../../repo"
]

for r in test_repos:
    res = parse_repo_arg(r)
    print(f"Repo: {r} -> Result: {res}")
    if res:
        owner, repo_name, _, _, _ = res
        storage_base = Path("/home/user/.jup/skills")
        category = "misc"
        GH_PREFIX = "gh"
        target_dir = storage_base / category / GH_PREFIX / owner / repo_name
        print(f"  Target Dir: {target_dir}")
