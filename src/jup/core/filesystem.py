import shutil
from pathlib import Path


def rel_home(p: Path | str) -> str:
    """Convert path to home-relative string (~/...)."""
    return str(p).replace(str(Path.home()), "~")


def validate_path(path: Path, base_dir: Path) -> Path:
    """
    Ensure that the resolved path is within the base directory.
    Raises ValueError if the path is outside the base directory.
    """
    resolved_path = Path(path).resolve()
    resolved_base = Path(base_dir).resolve()

    if resolved_base not in resolved_path.parents and resolved_path != resolved_base:
        raise ValueError(f"Path {path} is outside the allowed directory {base_dir}")

    return resolved_path


def safe_rmtree(path: Path, base_dir: Path):
    """Safely remove a directory after validating it is within the base directory."""
    validated_path = validate_path(path, base_dir)
    if validated_path.exists():
        shutil.rmtree(validated_path)


def safe_copytree(src: Path, dst: Path, base_dir: Path):
    """Safely copy a directory after validating the destination is within the base directory."""
    validate_path(dst, base_dir)
    shutil.copytree(src, dst, dirs_exist_ok=True)
