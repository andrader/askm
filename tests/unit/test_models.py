import pytest
from jup.models import JupConfig, SkillSource, SkillsLock, AgentConfig, SyncMode, ScopeType

def test_jup_config_defaults():
    config = JupConfig()
    assert config.scope == ScopeType.GLOBAL
    assert config.agents == []
    assert config.sync_mode == SyncMode.LINK

def test_jup_config_alias():
    config = JupConfig.model_validate({"sync-mode": "copy"})
    assert config.sync_mode == SyncMode.COPY

def test_skill_source():
    source = SkillSource(repo="owner/repo", category="test", skills=["skill1", "skill2"])
    assert source.repo == "owner/repo"
    assert source.category == "test"
    assert "skill1" in source.skills

def test_skills_lock():
    lock = SkillsLock()
    assert lock.sources == {}
    
    source = SkillSource(repo="owner/repo", category="test", skills=["skill1"])
    lock.sources["owner/repo"] = source
    assert lock.sources["owner/repo"].repo == "owner/repo"

def test_agent_config():
    agent = AgentConfig(name="test", global_location="~/global", local_location="./local")
    assert agent.name == "test"
    assert agent.global_location == "~/global"
    assert agent.local_location == "./local"
