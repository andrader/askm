from jup.models import (
    JupConfig,
    SkillSource,
    SkillsLock,
    HarnessConfig,
    SyncMode,
    ScopeType,
)


def test_jupconfig_default():
    config = JupConfig()
    assert config.scope == ScopeType.USER
    assert config.harnesses == []
    assert config.sync_mode == SyncMode.LINK


def test_jup_config_alias():
    config = JupConfig.model_validate({"sync-mode": "copy"})
    assert config.sync_mode == SyncMode.COPY


def test_skill_source():
    source = SkillSource(
        repo="owner/repo", category="test", skills=["skill1", "skill2"]
    )
    assert source.repo == "owner/repo"
    assert source.category == "test"
    assert "skill1" in source.skills


def test_skills_lock():
    lock = SkillsLock()
    assert lock.sources == {}

    source = SkillSource(repo="owner/repo", category="test", skills=["skill1"])
    lock.sources["owner/repo"] = source
    assert lock.sources["owner/repo"].repo == "owner/repo"


def test_harness_config():
    harness = HarnessConfig(
        name="test", global_location="~/global", local_location="./local"
    )
    assert harness.name == "test"
    assert harness.global_location == "~/global"
    assert harness.local_location == "./local"
