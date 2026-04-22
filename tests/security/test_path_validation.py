import pytest
import os
from pathlib import Path
from jup.core.filesystem import validate_path
from jup.commands.add import parse_repo_arg


def test_validate_path_absolute_outside(tmp_path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    # Use /etc/passwd as an example of an absolute path outside
    outside_path = Path("/etc/passwd")

    with pytest.raises(ValueError, match="is outside the allowed directory"):
        validate_path(outside_path, base_dir)


def test_validate_path_relative_traversal(tmp_path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    traversal_path = base_dir / ".." / ".." / "etc" / "passwd"

    with pytest.raises(ValueError, match="is outside the allowed directory"):
        validate_path(traversal_path, base_dir)


def test_validate_path_symlink_escape(tmp_path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()

    secret_dir = tmp_path / "secret"
    secret_dir.mkdir()
    secret_file = secret_dir / "flag.txt"
    secret_file.write_text("SECRET")

    symlink_path = base_dir / "evil_link"
    os.symlink(secret_dir, symlink_path)

    # Path.resolve() follows symlinks, so this should fail
    with pytest.raises(ValueError, match="is outside the allowed directory"):
        validate_path(symlink_path / "flag.txt", base_dir)


def test_parse_repo_arg_path_traversal():
    # Test that owner/repo/../../etc/passwd is normalized or rejected
    # Current implementation collapses slashes and checks for local existence
    repo_arg = "owner/repo/../../../../etc/passwd"
    parsed = parse_repo_arg(repo_arg)

    if parsed:
        owner, repo, subpath, version, is_url = parsed
        # If it parsed, the subpath should not contain traversal components
        # OR it should be handled correctly by validate_path later
        assert ".." not in subpath
