import pytest
from unittest.mock import patch
from jup.models import HarnessConfig


@pytest.fixture
def mock_jup_dir(tmp_path):
    """
    Provides a completely isolated environment for jup tests.
    Mocks JUP_CONFIG_DIR and DEFAULT_HARNESSES to use tmp_path.
    """
    jup_dir = tmp_path / ".jup"
    jup_dir.mkdir()

    # Create necessary subdirs in tmp_path to avoid leaks to current working directory
    global_dir = tmp_path / "global"
    local_dir = tmp_path / "local"
    global_dir.mkdir()
    local_dir.mkdir()

    mock_harnesses = {
        ".agents": HarnessConfig(
            name=".agents",
            global_location=str(global_dir),
            local_location=str(local_dir),
        ),
        "copilot": HarnessConfig(
            name="copilot",
            global_location=str(tmp_path / "copilot_global"),
            local_location=str(tmp_path / "copilot_local"),
        ),
        "claude": HarnessConfig(
            name="claude",
            global_location=str(tmp_path / "claude_global"),
            local_location=str(tmp_path / "claude_local"),
        ),
    }

    # IMPORTANT: Patch both config and models because they might have already imported it
    with patch("jup.config.JUP_CONFIG_DIR", jup_dir):
        with patch("jup.config.DEFAULT_HARNESSES", mock_harnesses):
            with patch("jup.models.DEFAULT_HARNESSES", mock_harnesses):
                # Ensure we also mock the home directory for expanduser calls if needed
                # monkeypatching HOME is often safer for expanduser
                yield jup_dir


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """
    More aggressive isolation by monkeypatching HOME.
    """
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()

    monkeypatch.setenv("HOME", str(fake_home))

    # We still need to patch JUP_CONFIG_DIR because it is initialized at module load
    jup_dir = fake_home / ".jup"
    jup_dir.mkdir()

    # Redirect default harnesses to fake home
    mock_harnesses = {
        ".agents": HarnessConfig(
            name=".agents",
            global_location="~/.agents/skills",
            local_location="./.agents/skills",
        )
    }

    with patch("jup.config.JUP_CONFIG_DIR", jup_dir):
        with patch("jup.config.DEFAULT_HARNESSES", mock_harnesses):
            with patch("jup.models.DEFAULT_HARNESSES", mock_harnesses):
                # Chdir to tmp_path to ensure ./ refers to a safe place
                monkeypatch.chdir(tmp_path)
                yield jup_dir
