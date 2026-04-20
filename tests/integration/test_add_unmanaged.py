from typer.testing import CliRunner
from jup.main import app
from jup.config import get_config, get_skills_lock
from jup.commands.utils import LOCAL_SOURCE_TYPE

runner = CliRunner()


def test_add_detects_and_moves_harness_dir_source(tmp_path, monkeypatch):
    # Setup mock home and harness dir
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    harness_dir = fake_home / ".agents" / "skills"
    harness_dir.mkdir(parents=True)

    # Create a skill inside the harness dir
    skill_dir = harness_dir / "unmanaged-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    monkeypatch.setenv("HOME", str(fake_home))
    # We also need to point JUP_CONFIG_DIR if it's based on Path.home()
    # In src/jup/config.py: JUP_CONFIG_DIR = Path.home() / ".jup"

    # Mock harness location to our tmp path
    # We need to ensure the config uses our fake_home
    # Since jup.config.JUP_CONFIG_DIR is defined at module level,
    # we might need to monkeypatch it if it was already imported.
    import jup.config

    monkeypatch.setattr(jup.config, "JUP_CONFIG_DIR", fake_home / ".jup")

    # Set up config with the harness dir
    config = get_config()
    from jup.models import HarnessConfig

    config.custom_harnesses[".agents"] = HarnessConfig(
        name=".agents",
        global_location=str(harness_dir),
        local_location="./.agents/skills",
    )
    jup.config.save_config(config)

    # Run jup add <path>
    # Mocking typer.confirm to return True (Yes, move it)
    # CliRunner.invoke allows providing input for prompts
    result = runner.invoke(app, ["add", str(skill_dir)], input="y\n")

    assert result.exit_code == 0
    assert "Source is inside a harness directory" in result.stdout
    assert "Moving to" in result.stdout

    # Verify it moved
    storage_dir = fake_home / ".jup" / "skills" / "misc" / "unmanaged-skill"
    assert storage_dir.exists()
    assert (storage_dir / "SKILL.md").exists()
    assert skill_dir.is_symlink()  # Should be a symlink now

    # Verify it's in the lock file with the NEW path
    lock = get_skills_lock(config)
    assert str(storage_dir) in lock.sources
    assert lock.sources[str(storage_dir)].source_type == LOCAL_SOURCE_TYPE


def test_add_detects_but_keeps_harness_dir_source(tmp_path, monkeypatch):
    # Setup mock home and harness dir
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    harness_dir = fake_home / ".agents" / "skills"
    harness_dir.mkdir(parents=True)

    # Create a skill inside the harness dir
    skill_dir = harness_dir / "unmanaged-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    monkeypatch.setenv("HOME", str(fake_home))
    import jup.config

    monkeypatch.setattr(jup.config, "JUP_CONFIG_DIR", fake_home / ".jup")

    config = get_config()
    from jup.models import HarnessConfig

    config.custom_harnesses[".agents"] = HarnessConfig(
        name=".agents",
        global_location=str(harness_dir),
        local_location="./.agents/skills",
    )
    jup.config.save_config(config)

    # Run jup add <path>
    # Mocking typer.confirm to return False (No, keep it)
    result = runner.invoke(app, ["add", str(skill_dir)], input="n\n")

    assert result.exit_code == 0
    assert "Source is inside a harness directory" in result.stdout

    # Verify it did NOT move
    assert skill_dir.exists()
    storage_dir = fake_home / ".jup" / "skills" / "misc" / "unmanaged-skill"
    assert not storage_dir.exists()

    # Verify it's in the lock file with the ORIGINAL path
    lock = get_skills_lock(config)
    assert str(skill_dir.resolve()) in lock.sources
