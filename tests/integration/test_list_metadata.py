import json
import pytest
from typer.testing import CliRunner
from unittest.mock import patch

from jup.main import app
from jup.models import HarnessConfig, SkillSource, ScopeType
from jup.config import get_skills_lock, save_skills_lock, JupConfig

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
        with patch("jup.config.DEFAULT_HARNESSES", mock_harnesses):
            with patch("jup.models.DEFAULT_HARNESSES", mock_harnesses):
                yield jup_dir


def test_list_metadata_table_and_json(mock_jup_dir):
    config = JupConfig(scope=ScopeType.USER)
    lock = get_skills_lock(config)

    # 1. No version, missing source
    lock.sources["owner/repo-no-version"] = SkillSource(
        repo="owner/repo-no-version", category="test", skills=["skill-no-version"]
    )

    # 2. Valid version, invalid/empty source string
    lock.sources["owner/repo-empty-source"] = SkillSource(
        repo="owner/repo-empty-source",
        category="test",
        skills=["skill-empty-source"],
        version="1.0.0",
        source="",
    )

    # 3. Very long version string
    long_version = (
        "v1.2.3"
        + "-alpha.beta.gamma.delta.epsilon.zeta.eta.theta.iota.kappa.lambda.mu.nu.xi.omicron.pi.rho.sigma.tau.upsilon.phi.chi.psi.omega"
        * 3
    )
    lock.sources["owner/repo-long-version"] = SkillSource(
        repo="owner/repo-long-version",
        category="test",
        skills=["skill-long-version"],
        version=long_version,
        source="https://example.com/long-version",
    )

    save_skills_lock(config, lock)

    # Test Standard Table Output
    with patch.dict("os.environ", {"COLUMNS": "200"}):
        result = runner.invoke(app, ["list"])
    assert result.exit_code == 0, f"Command failed: {result.stdout}"

    # Verify elements are printed in the table without breaking rich
    assert "skill-no-version" in result.stdout
    assert "skill-empty-source" in result.stdout
    assert "1.0.0" in result.stdout
    assert "skill-long-version" in result.stdout
    # Check for at least the start of the long version
    assert "v1.2.3" in result.stdout
    assert "owner/repo-long-version" in result.stdout

    # Test JSON Output
    result_json = runner.invoke(app, ["list", "--json"])
    assert result_json.exit_code == 0, f"JSON Command failed: {result_json.stdout}"

    data = json.loads(result_json.stdout)
    installed = data.get("installed", [])

    # Verify JSON structure contains metadata
    skill_no_version = next(
        (s for s in installed if s["name"] == "skill-no-version"), None
    )
    assert skill_no_version is not None
    # No version should be None or not present
    assert skill_no_version.get("version") is None

    skill_empty_source = next(
        (s for s in installed if s["name"] == "skill-empty-source"), None
    )
    assert skill_empty_source is not None
    assert skill_empty_source.get("version") == "1.0.0"
    assert skill_empty_source.get("source") == ""

    skill_long_version = next(
        (s for s in installed if s["name"] == "skill-long-version"), None
    )
    assert skill_long_version is not None
    assert skill_long_version.get("version") == long_version
    assert skill_long_version.get("source") == "https://example.com/long-version"
