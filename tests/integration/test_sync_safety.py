from pathlib import Path
from jup.commands.sync import sync_logic
from jup.config import get_config, get_skills_lock, save_skills_lock
from jup.models import SkillSource
from jup.commands.utils import LOCAL_SOURCE_TYPE


def test_sync_does_not_delete_source_when_in_harness_dir(isolated_env, tmp_path):
    # isolated_env already monkeypatches HOME and JUP_CONFIG_DIR
    # and chdirs to tmp_path

    harness_dir = Path("harness_global").resolve()
    harness_dir.mkdir(parents=True)

    local_harness_dir = Path("harness_local").resolve()
    local_harness_dir.mkdir(parents=True)

    # Create a skill inside the harness dir (the "unmanaged" scenario)
    skill_dir = harness_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    config = get_config()
    config.harnesses = [".agents"]
    # Mock harness location to our tmp path
    from jup.models import HarnessConfig

    config.custom_harnesses[".agents"] = HarnessConfig(
        name=".agents",
        global_location=str(harness_dir),
        local_location=str(local_harness_dir),
    )

    lock = get_skills_lock(config)
    lock.sources[str(skill_dir)] = SkillSource(
        repo=str(skill_dir),
        source_type=LOCAL_SOURCE_TYPE,
        source_path=str(skill_dir),
        source_layout="single",
        skills=["my-skill"],
    )
    save_skills_lock(config, lock)

    # Run sync - it should NOT delete or unlink my-skill/SKILL.md
    sync_logic(verbose=True, config=config)

    assert (skill_dir / "SKILL.md").exists(), "Sync deleted the source file!"
