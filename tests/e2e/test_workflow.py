import shutil
from typer.testing import CliRunner
from unittest.mock import patch
from jup.main import app

runner = CliRunner()


def test_full_workflow(mock_jup_dir):
    # Setup repo mock structure (mimic what mock_env was doing)
    repo_dir = mock_jup_dir.parent / "mock_repo"
    repo_dir.mkdir()
    skills_dir = repo_dir / "skills"
    skills_dir.mkdir()
    (skills_dir / "useful-skill").mkdir()
    ((skills_dir / "useful-skill") / "SKILL.md").write_text("Cool skill")

    with patch("jup.commands.add.run_git_clone") as mock_clone:

        def side_effect(repo_url, dest_dir, **kwargs):
            shutil.copytree(repo_dir, dest_dir, dirs_exist_ok=True)

        mock_clone.side_effect = side_effect

        # 1. Config set
        result = runner.invoke(app, ["config", "set", "sync-mode", "copy"])
        assert result.exit_code == 0
        assert "Set sync-mode to copy" in result.stdout

        # 2. Add skill
        result = runner.invoke(app, ["add", "myorg/myskills"])
        assert result.exit_code == 0
        assert "Successfully added 1 skills from myorg/myskills" in result.stdout

        # 3. Sync (happens automatically in add, but let's run it explicitly)
        result = runner.invoke(app, ["sync"])
        assert result.exit_code == 0
        assert "Synced 1 skills" in result.stdout

        # Verify copy (since we set sync-mode to copy)
        from jup.config import get_scope_dir, JupConfig

        scope_dir = get_scope_dir(JupConfig())
        target_skill_dir = scope_dir / "useful-skill"
        assert target_skill_dir.exists()
        assert not target_skill_dir.is_symlink()

        # 4. List
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "myorg/myskills" in result.stdout
        assert "useful-skill" in result.stdout

        # 5. Remove
        result = runner.invoke(app, ["remove", "useful-skill", "--yes"])
        assert result.exit_code == 0
        assert "Removed skill 'useful-skill'" in result.stdout

        # After removing the only skill, the repo should be gone from lockfile
        result = runner.invoke(app, ["list"])
        assert "No skills installed" in result.stdout


def test_local_directory_workflow(mock_jup_dir):
    local_skills_dir = mock_jup_dir.parent / "local-skills"
    local_skills_dir.mkdir()
    (local_skills_dir / "skill-a").mkdir()
    (local_skills_dir / "skill-b").mkdir()
    (local_skills_dir / "skill-a" / "SKILL.md").write_text("A")
    (local_skills_dir / "skill-b" / "SKILL.md").write_text("B")

    result = runner.invoke(app, ["add", str(local_skills_dir)])
    assert result.exit_code == 0
    assert "Successfully added 2 local skills" in result.stdout

    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0
    assert "Synced 2 skills" in result.stdout

    from jup.config import get_scope_dir, JupConfig

    scope_dir = get_scope_dir(JupConfig())
    linked_skill_dir = scope_dir / "skill-a"
    assert linked_skill_dir.exists()
    assert linked_skill_dir.is_symlink()

    (local_skills_dir / "skill-a" / "SKILL.md").write_text("A updated")
    assert (linked_skill_dir / "SKILL.md").read_text() == "A updated"
