import json
import pytest
import shutil
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
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


@pytest.fixture
def mock_repo_structure(tmp_path):
    # This simulates what run_git_clone would create in temp_dir
    repo_dir = tmp_path / "cloned_repo"
    repo_dir.mkdir()
    skills_dir = repo_dir / "skills"
    skills_dir.mkdir()

    skill1 = skills_dir / "skill1"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text("Skill 1")

    skill2 = skills_dir / "skill2"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text("Skill 2")

    # Also create a fallback .claude/skills/ with a unique skill
    claude_skills_dir = repo_dir / ".claude" / "skills"
    claude_skills_dir.mkdir(parents=True)
    fallback_skill = claude_skills_dir / "fallback-skill"
    fallback_skill.mkdir()
    (fallback_skill / "SKILL.md").write_text("Fallback Skill")

    return repo_dir


@pytest.fixture
def mock_local_skills_collection(tmp_path):
    local_dir = tmp_path / "local-skills"
    local_dir.mkdir()

    for skill_name in ["local1", "local2"]:
        skill_dir = local_dir / skill_name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"{skill_name} skill")

    return local_dir


@pytest.fixture
def mock_local_single_skill(tmp_path):
    skill_dir = tmp_path / "single-local-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("single skill")
    return skill_dir


def test_add_skill_with_path_and_skills_options(mock_jup_dir, mock_repo_structure):
    # Mocking run_git_clone in commands.py
    with patch("jup.commands.run_git_clone") as mock_clone:

        def side_effect(repo_url, dest_dir, **kwargs):
            shutil.copytree(mock_repo_structure, dest_dir, dirs_exist_ok=True)
            return MagicMock()

        mock_clone.side_effect = side_effect

        # (1) Add a single skill from a subdirectory using --skills
        result = runner.invoke(app, ["add", "owner/repo", "--skills", "skill1"])
        assert result.exit_code == 0
        assert "Successfully added 1 skills from owner/repo" in result.stdout
        from jup.config import get_skills_lock, JupConfig

        lock = get_skills_lock(JupConfig())
        assert "owner/repo" in lock.sources
        assert lock.sources["owner/repo"].skills == ["skill1"]

        # Remove for next test
        runner.invoke(app, ["remove", "owner/repo", "--yes"])

        # (2) Add multiple skills using --skills
        result = runner.invoke(app, ["add", "owner/repo", "--skills", "skill1,skill2"])
        assert result.exit_code == 0
        assert "Successfully added 2 skills from owner/repo" in result.stdout
        lock = get_skills_lock(JupConfig())
        assert sorted(lock.sources["owner/repo"].skills) == ["skill1", "skill2"]

        # Remove for next test
        runner.invoke(app, ["remove", "owner/repo", "--yes"])

        # (3) Omit --skills to add all
        result = runner.invoke(app, ["add", "owner/repo"])
        assert result.exit_code == 0
        assert "Successfully added 2 skills from owner/repo" in result.stdout
        lock = get_skills_lock(JupConfig())
        assert sorted(lock.sources["owner/repo"].skills) == ["skill1", "skill2"]

        # Remove for next test
        runner.invoke(app, ["remove", "owner/repo", "--yes"])

        # (3b) Remove skills/ and test fallback to .claude/skills/
        import shutil as _shutil

        skills_dir = mock_repo_structure / "skills"
        _shutil.rmtree(skills_dir)
        result = runner.invoke(app, ["add", "owner/repo"])
        assert result.exit_code == 0
        assert "Successfully added 1 skills from owner/repo" in result.stdout
        lock = get_skills_lock(JupConfig())
        assert lock.sources["owner/repo"].skills == ["fallback-skill"]
        runner.invoke(app, ["remove", "owner/repo", "--yes"])

        # (4) Error if --skills or --path is used with a local source
        local_path = str(mock_repo_structure)
        result = runner.invoke(app, ["add", local_path, "--skills", "skill1"])
        assert result.exit_code != 0
        # Accept any error output for local + --skills, since CLI ignores these options for local
        assert result.stdout.strip() != ""

        result = runner.invoke(app, ["add", local_path, "--path", "skills"])
        assert result.exit_code != 0
        assert result.stdout.strip() != ""


def test_list_skills(mock_jup_dir):
    # First add a skill (programmatically to lockfile)
    from jup.config import get_skills_lock, save_skills_lock, JupConfig
    from jup.models import SkillSource

    config = JupConfig()
    lock = get_skills_lock(config)
    lock.sources["owner/repo"] = SkillSource(
        repo="owner/repo", category="test", skills=["skill1"]
    )
    save_skills_lock(config, lock)

    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "owner/repo" in result.stdout
    assert "skill1" in result.stdout


def test_remove_skill_by_repo(mock_jup_dir):
    from jup.config import get_skills_lock, save_skills_lock, JupConfig
    from jup.models import SkillSource

    config = JupConfig()
    lock = get_skills_lock(config)
    lock.sources["owner/repo"] = SkillSource(
        repo="owner/repo", category="test", skills=["skill1", "skill2"]
    )
    save_skills_lock(config, lock)

    result = runner.invoke(app, ["remove", "owner/repo", "--yes"])
    assert result.exit_code == 0
    assert "Removed repository 'owner/repo' and all its skills." in result.stdout

    lock = get_skills_lock(config)
    assert "owner/repo" not in lock.sources


def test_remove_specific_skill(mock_jup_dir):
    from jup.config import get_skills_lock, save_skills_lock, JupConfig
    from jup.models import SkillSource

    config = JupConfig()
    lock = get_skills_lock(config)
    lock.sources["owner/repo"] = SkillSource(
        repo="owner/repo", category="test", skills=["skill1", "skill2"]
    )
    save_skills_lock(config, lock)

    result = runner.invoke(app, ["remove", "skill1", "--yes"])
    assert result.exit_code == 0
    assert "Removed skill 'skill1' from owner/repo" in result.stdout

    lock = get_skills_lock(config)
    assert "owner/repo" in lock.sources
    assert lock.sources["owner/repo"].skills == ["skill2"]


def test_sync_skills(mock_jup_dir, mock_repo_structure):
    # Setup: Add a skill manually to storage
    storage_dir = mock_jup_dir / "skills" / "test" / "gh" / "owner" / "repo"
    storage_dir.mkdir(parents=True)
    skill_dir = storage_dir / "skill1"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("Skill 1 content")

    from jup.config import get_skills_lock, save_skills_lock, JupConfig
    from jup.models import SkillSource

    config = JupConfig()
    lock = get_skills_lock(config)
    lock.sources["owner/repo"] = SkillSource(
        repo="owner/repo", category="test", skills=["skill1"]
    )
    save_skills_lock(config, lock)

    # Run sync
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
    assert "Synced 1 skills across 1 locations." in result.stdout

    # Check if link was created in scope_dir/skills (default target)
    from jup.config import get_scope_dir

    scope_dir = get_scope_dir(config)
    target_skill_dir = scope_dir / "skills" / "skill1"
    assert target_skill_dir.exists()
    assert target_skill_dir.is_symlink()
    assert target_skill_dir.resolve() == skill_dir.resolve()


def test_add_local_skills_directory(mock_jup_dir, mock_local_skills_collection):
    result = runner.invoke(app, ["add", str(mock_local_skills_collection)])
    assert result.exit_code == 0
    assert "Successfully added 2 local skills" in result.stdout

    from jup.config import get_skills_lock, get_scope_dir, JupConfig

    lock = get_skills_lock(JupConfig())
    source_key = str(mock_local_skills_collection.resolve())
    assert source_key in lock.sources
    assert lock.sources[source_key].source_type == "local"
    assert lock.sources[source_key].source_layout == "collection"
    assert sorted(lock.sources[source_key].skills) == ["local1", "local2"]

    scope_dir = get_scope_dir(JupConfig())
    linked_skill = scope_dir / "skills" / "local1"
    assert linked_skill.is_symlink()
    assert linked_skill.resolve() == (mock_local_skills_collection / "local1").resolve()


def test_add_local_single_skill_directory(mock_jup_dir, mock_local_single_skill):
    result = runner.invoke(app, ["add", str(mock_local_single_skill)])
    assert result.exit_code == 0
    assert "Successfully added 1 local skills" in result.stdout

    from jup.config import get_skills_lock, get_scope_dir, JupConfig

    lock = get_skills_lock(JupConfig())
    source_key = str(mock_local_single_skill.resolve())
    assert source_key in lock.sources
    assert lock.sources[source_key].source_type == "local"
    assert lock.sources[source_key].source_layout == "single"
    assert lock.sources[source_key].skills == ["single-local-skill"]

    scope_dir = get_scope_dir(JupConfig())
    linked_skill = scope_dir / "skills" / "single-local-skill"
    assert linked_skill.is_symlink()
    assert linked_skill.resolve() == mock_local_single_skill.resolve()


def test_local_add_relative_path_uses_absolute_lock_key(
    mock_jup_dir, mock_local_single_skill, monkeypatch
):
    monkeypatch.chdir(mock_local_single_skill.parent)
    result = runner.invoke(app, ["add", "./single-local-skill"])
    assert result.exit_code == 0

    from jup.config import get_skills_lock, JupConfig

    lock = get_skills_lock(JupConfig())
    assert str(mock_local_single_skill.resolve()) in lock.sources


def test_local_link_mode_reflects_source_changes(mock_jup_dir, mock_local_single_skill):
    result = runner.invoke(app, ["add", str(mock_local_single_skill)])
    assert result.exit_code == 0

    from jup.config import get_scope_dir, JupConfig

    scope_dir = get_scope_dir(JupConfig())
    linked_skill_md = scope_dir / "skills" / "single-local-skill" / "SKILL.md"
    assert linked_skill_md.read_text() == "single skill"

    (mock_local_single_skill / "SKILL.md").write_text("updated skill")
    assert linked_skill_md.read_text() == "updated skill"


def test_sync_skips_missing_sources_in_summary(mock_jup_dir, mock_local_single_skill):
    from jup.config import get_skills_lock, save_skills_lock, JupConfig
    from jup.models import SkillSource

    config = JupConfig()
    lock = get_skills_lock(config)
    lock.sources["owner/repo"] = SkillSource(
        repo="owner/repo", category="test", skills=["missing-skill"]
    )
    lock.sources[str(mock_local_single_skill.resolve())] = SkillSource(
        repo=str(mock_local_single_skill.resolve()),
        source_type="local",
        source_path=str(mock_local_single_skill.resolve()),
        source_layout="single",
        category="misc",
        skills=["single-local-skill"],
    )
    save_skills_lock(config, lock)

    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
    assert "Skipped 1 missing skills" in result.stdout
    assert "Synced 1 skills across 1 locations." in result.stdout


def test_find_skills(mock_jup_dir):
    mock_data = {
        "query": "python",
        "skills": [
            {
                "id": "github/owner/repo1",
                "name": "Skill 1",
                "installs": 100,
                "skillId": "repo1",
            }
        ],
    }
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_data).encode()
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        with patch("jup.commands.add_skill") as mock_add_skill:
            # Select 1 to install
            result = runner.invoke(app, ["find", "python"], input="1\n")
            assert result.exit_code == 0
            assert "Skill 1" in result.stdout
            assert "owner/repo1" in result.stdout
            mock_add_skill.assert_called_once_with(repo="owner/repo1", verbose=False)


def test_find_skills_cancel(mock_jup_dir):
    mock_data = {
        "query": "python",
        "skills": [{"id": "github/owner/repo1", "name": "Skill 1"}],
    }
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_data).encode()
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        # Select 0 to cancel
        result = runner.invoke(app, ["find", "python"], input="0\n")
        assert result.exit_code == 0
        assert "Cancelled" in result.stdout


def test_find_skills_nested_path(mock_jup_dir):
    mock_data = {
        "query": "python",
        "skills": [
            {
                "id": "github/owner/repo1/nested/path",
                "name": "Nested Skill",
                "installs": 100,
                "skillId": "path",
            }
        ],
    }
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(mock_data).encode()
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        with patch("jup.commands.add_skill") as mock_add_skill:
            # Select 1 to install
            result = runner.invoke(app, ["find", "python"], input="1\n")
            assert result.exit_code == 0
            assert "Nested Skill" in result.stdout
            assert "owner/repo1" in result.stdout
            mock_add_skill.assert_called_once_with(
                repo="owner/repo1", path="nested/path", verbose=False
            )
