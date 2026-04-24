import shutil
import os
from pathlib import Path


def rel_home(p: Path | str) -> str:
    """Convert path to home-relative string (~/...)."""
    return str(p).replace(str(Path.home()), "~")


def validate_path(path: Path, base_dir: Path, follow_symlinks: bool = True) -> Path:
    """
    Ensure that the path is within the base directory.
    If follow_symlinks is True (default), it resolves the path to its real location.
    If follow_symlinks is False, it only checks the logical path (no symlink resolution).
    Raises ValueError if the path is outside the base directory.
    """
    if follow_symlinks:
        resolved_path = Path(path).resolve()
        resolved_base = Path(base_dir).resolve()
    else:
        # Use abspath + normpath to perform logical path validation without following symlinks
        resolved_path = Path(os.path.normpath(os.path.abspath(path)))
        resolved_base = Path(os.path.normpath(os.path.abspath(base_dir)))

    if resolved_base not in resolved_path.parents and resolved_path != resolved_base:
        raise ValueError(f"Path {path} is outside the allowed directory {base_dir}")

    return resolved_path


def safe_rmtree(path: Path, base_dir: Path):
    """Safely remove a directory after validating it is within the base directory."""
    validated_path = validate_path(path, base_dir, follow_symlinks=True)
    if validated_path.exists():
        shutil.rmtree(validated_path)


def safe_copytree(src: Path, dst: Path, base_dir: Path):
    """Safely copy a directory after validating the destination is within the base directory."""
    validate_path(dst, base_dir, follow_symlinks=True)
    shutil.copytree(src, dst, dirs_exist_ok=True)
