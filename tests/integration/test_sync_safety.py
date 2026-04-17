from jup.commands.sync import sync_skills
from jup.config import get_config, get_skills_lock, save_skills_lock
from jup.models import SkillSource
from jup.commands.utils import LOCAL_SOURCE_TYPE


def test_sync_does_not_delete_source_when_in_agent_dir(tmp_path, monkeypatch):
    # Setup mock home and agent dir
    fake_home = tmp_path / "home"
    agent_dir = fake_home / ".agents" / "skills"
    agent_dir.mkdir(parents=True)

    # Create a skill inside the agent dir (the "unmanaged" scenario)
    skill_dir = agent_dir / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("info")

    monkeypatch.setenv("HOME", str(fake_home))

    config = get_config()
    config.agents = ["default"]
    # Mock agent location to our tmp path
    from jup.models import AgentConfig

    config.custom_agents["default"] = AgentConfig(
        name="default",
        global_location=str(agent_dir),
        local_location="./.agents/skills",
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
    sync_skills(verbose=True)

    assert (skill_dir / "SKILL.md").exists(), "Sync deleted the source file!"
