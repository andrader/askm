import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from jup.main import app
from jup.models import HarnessConfig

runner = CliRunner()


@pytest.fixture
def mock_jup_dir(tmp_path):
    jup_dir = tmp_path / ".jup"
    jup_dir.mkdir()

    mock_harnesses = {
        ".agents": HarnessConfig(
            name=".agents",
            global_location=str(tmp_path / "global"),
            local_location=str(tmp_path / "local"),
        )
    }

    with patch("jup.config.JUP_CONFIG_DIR", jup_dir):
        with patch("jup.config.CONFIG_FILE", jup_dir / "config.json"):
            with patch("jup.config.DEFAULT_HARNESSES", mock_harnesses):
                with patch("jup.models.DEFAULT_HARNESSES", mock_harnesses):
                    yield jup_dir


def test_harness_list_default(mock_jup_dir):
    result = runner.invoke(app, ["harness", "list"])
    assert result.exit_code == 0
    assert ".agents" in result.stdout


def test_harness_add_custom(mock_jup_dir):
    result = runner.invoke(
        app,
        [
            "harness",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    assert result.exit_code == 0
    assert "Added custom harness provider: custom" in result.stdout

    result = runner.invoke(app, ["harness", "list"])
    assert "custom" in result.stdout


def test_harness_add_duplicate(mock_jup_dir):
    runner.invoke(
        app,
        [
            "harness",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    result = runner.invoke(
        app,
        [
            "harness",
            "add",
            "custom",
            "--global-location",
            "/tmp/global2",
            "--local-location",
            "/tmp/local2",
        ],
    )
    assert result.exit_code == 1
    assert "Harness 'custom' already exists." in result.stdout


def test_harness_edit_custom(mock_jup_dir):
    runner.invoke(
        app,
        [
            "harness",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    result = runner.invoke(
        app, ["harness", "edit", "custom", "--local-location", "/tmp/new-local"]
    )
    assert result.exit_code == 0
    assert "Updated custom harness provider: custom" in result.stdout

    result = runner.invoke(app, ["harness", "list"])
    assert "/tmp/new-local" in result.stdout


def test_harness_edit_default_fails(mock_jup_dir):
    result = runner.invoke(
        app, ["harness", "edit", ".agents", "--local-location", "/tmp/new-local"]
    )
    assert result.exit_code == 1
    assert "Cannot edit default harness '.agents'." in result.stdout


def test_harness_remove_custom(mock_jup_dir):
    runner.invoke(
        app,
        [
            "harness",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    result = runner.invoke(app, ["harness", "remove", "custom"])
    assert result.exit_code == 0
    assert "Removed custom harness provider: custom" in result.stdout

    result = runner.invoke(app, ["harness", "list"])
    assert "custom" not in result.stdout


def test_harness_remove_default_fails(mock_jup_dir):
    result = runner.invoke(app, ["harness", "remove", ".agents"])
    assert result.exit_code == 1
    assert "Cannot remove default harness '.agents'." in result.stdout
