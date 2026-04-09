import pytest
import shutil
from pathlib import Path
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
            local_location=str(tmp_path / "local")
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

def test_add_skill(mock_jup_dir, mock_repo_structure):
    # Mocking run_git_clone in commands.py
    with patch("jup.commands.run_git_clone") as mock_clone:
        # Side effect to copy our mock repo structure to the temp destination
        def side_effect(repo_url, dest_dir, **kwargs):
            shutil.copytree(mock_repo_structure, dest_dir, dirs_exist_ok=True)
            return MagicMock()
        
        mock_clone.side_effect = side_effect
        
        result = runner.invoke(app, ["add", "owner/repo"])
        assert result.exit_code == 0
        assert "Successfully added 2 skills from owner/repo" in result.stdout
        
        # Verify it was added to lockfile
        from jup.config import get_skills_lock, JupConfig
        lock = get_skills_lock(JupConfig())
        assert "owner/repo" in lock.sources
        assert sorted(lock.sources["owner/repo"].skills) == ["skill1", "skill2"]

def test_list_skills(mock_jup_dir):
    # First add a skill (programmatically to lockfile)
    from jup.config import get_skills_lock, save_skills_lock, JupConfig
    from jup.models import SkillSource
    config = JupConfig()
    lock = get_skills_lock(config)
    lock.sources["owner/repo"] = SkillSource(repo="owner/repo", category="test", skills=["skill1"])
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
    lock.sources["owner/repo"] = SkillSource(repo="owner/repo", category="test", skills=["skill1", "skill2"])
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
    lock.sources["owner/repo"] = SkillSource(repo="owner/repo", category="test", skills=["skill1", "skill2"])
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
    lock.sources["owner/repo"] = SkillSource(repo="owner/repo", category="test", skills=["skill1"])
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
