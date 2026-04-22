from typer.testing import CliRunner
from jup.main import app

runner = CliRunner()


def test_ls_alias(mock_jup_dir):
    result = runner.invoke(app, ["ls"])
    assert result.exit_code == 0
    assert (
        "Installed Skills" in result.stdout
        or "No skills installed." in result.stdout
        or "No managed skills installed." in result.stdout
    )


def test_ls_skills_alias(mock_jup_dir):
    result = runner.invoke(app, ["ls", "skills"])
    assert result.exit_code == 0


def test_agent_alias(mock_jup_dir):
    result = runner.invoke(app, ["agent", "list"])
    assert result.exit_code == 0
    assert "Harness Providers" in result.stdout


def test_agents_alias(mock_jup_dir):
    result = runner.invoke(app, ["agents", "list"])
    assert result.exit_code == 0
    assert "Harness Providers" in result.stdout


def test_ls_agents_alias(mock_jup_dir):
    result = runner.invoke(app, ["ls", "agents"])
    assert result.exit_code == 0
    assert "Harness Providers" in result.stdout


def test_ls_agent_alias(mock_jup_dir):
    result = runner.invoke(app, ["ls", "agent"])
    assert result.exit_code == 0
    assert "Harness Providers" in result.stdout


def test_ls_config_alias(mock_jup_dir):
    result = runner.invoke(app, ["ls", "config"])
    assert result.exit_code == 0
    assert "Current Configuration" in result.stdout


def test_ls_invalid_target(mock_jup_dir):
    result = runner.invoke(app, ["ls", "invalid_target"])
    assert result.exit_code == 1
    assert "Unknown list target: invalid_target" in result.stdout


def test_ls_agents_conflicting_options(mock_jup_dir):
    result = runner.invoke(app, ["ls", "agents", "--json"])
    assert result.exit_code == 1
    assert "Options like --json" in result.stdout
    assert "are not supported" in result.stdout
