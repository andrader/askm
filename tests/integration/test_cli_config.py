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
            local_location=str(tmp_path / "local")
        )
    }

    with patch("jup.config.JUP_CONFIG_DIR", jup_dir):
        with patch("jup.config.CONFIG_FILE", jup_dir / "config.json"):
            with patch("jup.config.DEFAULT_AGENTS", mock_agents):
                with patch("jup.models.DEFAULT_AGENTS", mock_agents):
                    yield jup_dir

def test_config_get_default(mock_jup_dir):
    result = runner.invoke(app, ["config", "get", "scope"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "global"

def test_config_set_scope(mock_jup_dir):
    result = runner.invoke(app, ["config", "set", "scope", "local"])
    assert result.exit_code == 0
    assert "Set scope to local" in result.stdout
    
    result = runner.invoke(app, ["config", "get", "scope"])
    assert result.stdout.strip() == "local"

def test_config_set_agents(mock_jup_dir):
    result = runner.invoke(app, ["config", "set", "agents", "gemini,copilot"])
    assert result.exit_code == 0
    assert "Set agents to gemini,copilot" in result.stdout
    
    result = runner.invoke(app, ["config", "get", "agents"])
    assert result.stdout.strip() == "gemini,copilot"

def test_config_unset_agents(mock_jup_dir):
    runner.invoke(app, ["config", "set", "agents", "gemini"])
    result = runner.invoke(app, ["config", "unset", "agents"])
    assert result.exit_code == 0
    
    result = runner.invoke(app, ["config", "get", "agents"])
    assert result.stdout.strip() == "none"

def test_config_set_sync_mode(mock_jup_dir):
    result = runner.invoke(app, ["config", "set", "sync-mode", "copy"])
    assert result.exit_code == 0
    
    result = runner.invoke(app, ["config", "get", "sync-mode"])
    assert result.stdout.strip() == "copy"

def test_config_set_invalid_key(mock_jup_dir):
    result = runner.invoke(app, ["config", "set", "invalid", "value"])
    assert result.exit_code == 1
    assert "Unknown config key: invalid" in result.stdout

def test_config_set_invalid_value(mock_jup_dir):
    result = runner.invoke(app, ["config", "set", "scope", "invalid"])
    assert result.exit_code == 1
    assert "Invalid value for scope: invalid" in result.stdout
