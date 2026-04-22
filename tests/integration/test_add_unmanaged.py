from pathlib import Path
from typer.testing import CliRunner
from jup.main import app
from jup.config import get_config, get_skills_lock
from jup.core.constants import LOCAL_SOURCE_TYPE

runner = CliRunner()


def test_add_detects_and_moves_harness_dir_source(isolated_env):
    # isolated_env already mocks JUP_CONFIG_DIR and HOME
    harness_dir = Path("harness_global").resolve()
    harness_dir.mkdir(parents=True)

    local_harness_dir = Path("harness_local").resolve()
    local_harness_dir.mkdir(parents=True)

    # Create a skill inside the harness dir
    skill_dir = harness_dir / "unmanaged-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    # Set up config with the harness dir
    config = get_config()
    from jup.models import HarnessConfig

    config.custom_harnesses[".agents"] = HarnessConfig(
        name=".agents",
        global_location=str(harness_dir),
        local_location=str(local_harness_dir),
    )
    import jup.config

    jup.config.save_config(config)

    # Run jup add <path>
    result = runner.invoke(app, ["add", str(skill_dir)], input="y\n")

    assert result.exit_code == 0
    assert "Source is inside a harness directory" in result.stdout
    assert "Moving to" in result.stdout

    # Verify it moved
    storage_dir = isolated_env / "skills" / "misc" / "unmanaged-skill"
    assert storage_dir.exists()
    assert (storage_dir / "SKILL.md").exists()
    assert skill_dir.is_symlink()  # Should be a symlink now

    # Verify it's in the lock file with the NEW path
    lock = get_skills_lock(config)
    assert str(storage_dir) in lock.sources
    assert lock.sources[str(storage_dir)].source_type == LOCAL_SOURCE_TYPE


def test_add_detects_but_keeps_harness_dir_source(isolated_env):
    harness_dir = Path("harness_global").resolve()
    harness_dir.mkdir(parents=True)

    local_harness_dir = Path("harness_local").resolve()
    local_harness_dir.mkdir(parents=True)

    # Create a skill inside the harness dir
    skill_dir = harness_dir / "unmanaged-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    config = get_config()
    from jup.models import HarnessConfig

    config.custom_harnesses[".agents"] = HarnessConfig(
        name=".agents",
        global_location=str(harness_dir),
        local_location=str(local_harness_dir),
    )
    import jup.config

    jup.config.save_config(config)

    # Run jup add <path>
    result = runner.invoke(app, ["add", str(skill_dir)], input="n\n")

    assert result.exit_code == 0
    assert "Source is inside a harness directory" in result.stdout

    # Verify it did NOT move
    assert skill_dir.exists()
    storage_dir = isolated_env / "skills" / "misc" / "unmanaged-skill"
    assert not storage_dir.exists()

    # Verify it's in the lock file with the ORIGINAL path
    lock = get_skills_lock(config)
    assert str(skill_dir.resolve()) in lock.sources
