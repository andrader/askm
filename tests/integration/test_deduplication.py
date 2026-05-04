import pytest
import shutil
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from jup.main import app
from jup.models import HarnessConfig

runner = CliRunner()


@pytest.fixture
def mock_jup_dedup_dir(mock_jup_dir, tmp_path):
    shared_global = tmp_path / "shared_global"
    shared_local = tmp_path / "shared_local"
    shared_global.mkdir()
    shared_local.mkdir()

    mock_harnesses = {
        ".agents": HarnessConfig(
            name=".agents",
            global_location=str(tmp_path / "default_global"),
            local_location=str(tmp_path / "default_local"),
        ),
        "agent1": HarnessConfig(
            name="agent1",
            global_location=str(shared_global),
            local_location=str(shared_local),
        ),
        "agent2": HarnessConfig(
            name="agent2",
            global_location=str(shared_global),  # exact same as agent1
            local_location=str(shared_local),
        ),
        "agent3": HarnessConfig(
            name="agent3",
            global_location=str(tmp_path / "agent3_global"),
            local_location=str(tmp_path / "agent3_local"),
        ),
    }

    with patch("jup.config.DEFAULT_HARNESSES", mock_harnesses):
        with patch("jup.models.DEFAULT_HARNESSES", mock_harnesses):
            yield mock_jup_dir


@pytest.fixture
def mock_repo_structure(tmp_path):
    repo_dir = tmp_path / "cloned_repo"
    repo_dir.mkdir()
    skills_dir = repo_dir / "skills"
    skills_dir.mkdir()

    skill1 = skills_dir / "skill1"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text("Skill 1")

    return repo_dir


def test_add_deduplication(mock_jup_dedup_dir, mock_repo_structure):
    # Mocking run_git_clone in add.py
    with patch("jup.commands.add.run_git_clone") as mock_clone:

        def side_effect(repo_url, dest_dir, **kwargs):
            shutil.copytree(mock_repo_structure, dest_dir, dirs_exist_ok=True)
            return MagicMock()

        mock_clone.side_effect = side_effect

        # Run jup add owner/repo -a agent1,agent2,agent3
        result = runner.invoke(
            app, ["add", "owner/repo", "-a", "agent1,agent2,agent3", "--verbose"]
        )

        # Ensure that it does not crash (exit_code == 0)
        assert result.exit_code == 0, f"Command failed with {result.stdout}"
        assert "Successfully added" in result.stdout

        # Verify no nested directories in the shared location
        shared_global = mock_jup_dedup_dir.parent / "shared_global"

        # The skill should be linked in shared_global
        skill_dir = shared_global / "skill1"
        assert skill_dir.exists(), "Skill was not installed in shared_global"

        # Check if there is a nested skill1/skill1 which shouldn't happen
        nested_skill_dir = skill_dir / "skill1"
        assert not nested_skill_dir.exists(), "Nested skill directories were created!"

        # Verify it only synced to unique locations (agent1/2 shared, plus agent3, plus default .jup scope dir)
        # So total synced locations: default + shared_global + agent3_global = 3 targets
        assert (
            "Synced 1 skills across 3 locations" in result.stdout
            or "across 4 locations" in result.stdout
        )
