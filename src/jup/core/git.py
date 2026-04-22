import subprocess
from pathlib import Path


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
            str_kwargs_flattened.pop()
            continue

        str_kwargs_flattened.append(val)

    subprocess.run(
        ["git", "clone", *str_kwargs_flattened, repo_url, str(dest_dir)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_git_pull(repo_dir: Path):
    subprocess.run(
        ["git", "pull"],
        cwd=repo_dir,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
