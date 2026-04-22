from unittest.mock import patch
from pathlib import Path
from jup.core.git import run_git_clone


@patch("subprocess.run")
def test_run_git_clone_whitelisting(mock_run):
    dest_dir = Path("/tmp/dummy")

    # Try an un-whitelisted kwarg
    run_git_clone("https://github.com/owner/repo", dest_dir, upload_pack="--help")

    # Verify subprocess.run was called WITHOUT --upload-pack
    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert "--upload-pack" not in cmd


@patch("subprocess.run")
def test_run_git_clone_value_sanitization(mock_run):
    dest_dir = Path("/tmp/dummy")

    # Try whitelisted kwarg but with flag injection in value
    run_git_clone("https://github.com/owner/repo", dest_dir, branch="--help")

    # Verify subprocess.run was called WITHOUT --help after --branch
    args, kwargs = mock_run.call_args
    cmd = args[0]
    # It should be ['git', 'clone', 'https://github.com/owner/repo', '/tmp/dummy']
    # OR it might have '--branch' but without the value if we only popped the value.
    # Actually, my implementation pops BOTH if the value starts with '-'.
    assert "--branch" not in cmd
    assert "--help" not in cmd


@patch("subprocess.run")
def test_run_git_clone_valid_args(mock_run):
    dest_dir = Path("/tmp/dummy")

    run_git_clone("https://github.com/owner/repo", dest_dir, branch="main", depth=1)

    args, kwargs = mock_run.call_args
    cmd = args[0]
    assert "--branch" in cmd
    assert "main" in cmd
    assert "--depth" in cmd
    assert "1" in cmd
