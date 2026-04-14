import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from jup.main import app
from jup.models import AgentConfig

runner = CliRunner()


@pytest.fixture
def mock_jup_dir(tmp_path):
    jup_dir = tmp_path / ".jup"
    jup_dir.mkdir()

    mock_agents = {
        "default": AgentConfig(
            name="default",
            global_location=str(tmp_path / "global"),
            local_location=str(tmp_path / "local"),
        )
    }

    with patch("jup.config.JUP_CONFIG_DIR", jup_dir):
        with patch("jup.config.CONFIG_FILE", jup_dir / "config.json"):
            with patch("jup.config.DEFAULT_AGENTS", mock_agents):
                with patch("jup.models.DEFAULT_AGENTS", mock_agents):
                    yield jup_dir


def test_agent_list_default(mock_jup_dir):
    result = runner.invoke(app, ["agent", "list"])
    assert result.exit_code == 0
    assert "default" in result.stdout
    assert "default" in result.stdout


def test_agent_add_custom(mock_jup_dir):
    result = runner.invoke(
        app,
        [
            "agent",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    assert result.exit_code == 0
    assert "Added custom agent provider: custom" in result.stdout

    result = runner.invoke(app, ["agent", "list"])
    assert "custom" in result.stdout
    assert "custom" in result.stdout


def test_agent_add_duplicate(mock_jup_dir):
    runner.invoke(
        app,
        [
            "agent",
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
            "agent",
            "add",
            "custom",
            "--global-location",
            "/tmp/global2",
            "--local-location",
            "/tmp/local2",
        ],
    )
    assert result.exit_code == 1
    assert "Agent 'custom' already exists." in result.stdout


def test_agent_edit_custom(mock_jup_dir):
    runner.invoke(
        app,
        [
            "agent",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    result = runner.invoke(
        app, ["agent", "edit", "custom", "--local-location", "/tmp/new-local"]
    )
    assert result.exit_code == 0
    assert "Updated custom agent provider: custom" in result.stdout

    result = runner.invoke(app, ["agent", "list"])
    assert "/tmp/new-local" in result.stdout


def test_agent_edit_default_fails(mock_jup_dir):
    result = runner.invoke(
        app, ["agent", "edit", "default", "--local-location", "/tmp/new-local"]
    )
    assert result.exit_code == 1
    assert "Cannot edit default agent 'default'." in result.stdout


def test_agent_remove_custom(mock_jup_dir):
    runner.invoke(
        app,
        [
            "agent",
            "add",
            "custom",
            "--global-location",
            "/tmp/global",
            "--local-location",
            "/tmp/local",
        ],
    )
    result = runner.invoke(app, ["agent", "remove", "custom"])
    assert result.exit_code == 0
    assert "Removed custom agent provider: custom" in result.stdout

    result = runner.invoke(app, ["agent", "list"])
    assert "custom" not in result.stdout


def test_agent_remove_default_fails(mock_jup_dir):
    result = runner.invoke(app, ["agent", "remove", "default"])
    assert result.exit_code == 1
    assert "Cannot remove default agent 'default'." in result.stdout
