import pytest
from unittest.mock import patch
from jup.models import JupConfig, SkillsLock, ScopeType, SyncMode, HarnessConfig
from jup.config import (
    get_config,
    save_config,
    get_scope_dir,
    get_skills_storage_dir,
    get_lockfile_path,
    get_skills_lock,
    save_skills_lock,
)


@pytest.fixture
def mock_jup_dir(tmp_path):
    jup_dir = tmp_path / ".jup"
    jup_dir.mkdir()

    # Mock harnesses to use tmp_path
    mock_harnesses = {
        ".agents": HarnessConfig(
            name=".agents",
            global_location=str(tmp_path / "global"),
            local_location=str(tmp_path / "local"),
        )
    }

    with patch("jup.config.JUP_CONFIG_DIR", jup_dir):
        with patch("jup.config.DEFAULT_HARNESSES", mock_harnesses):
            with patch("jup.models.DEFAULT_HARNESSES", mock_harnesses):
                yield jup_dir


def test_get_config_default(mock_jup_dir):
    config = get_config()
    assert isinstance(config, JupConfig)
    assert config.scope == ScopeType.GLOBAL


def test_save_and_get_config(mock_jup_dir):
    config = JupConfig(
        scope=ScopeType.LOCAL, harnesses=["gemini"], sync_mode=SyncMode.COPY
    )
    save_config(config)

    loaded_config = get_config()
    assert loaded_config.scope == ScopeType.LOCAL
    assert loaded_config.harnesses == ["gemini"]
    assert loaded_config.sync_mode == SyncMode.COPY


def test_get_scope_dir(mock_jup_dir, tmp_path):
    config_global = JupConfig(scope=ScopeType.GLOBAL)
    assert get_scope_dir(config_global) == tmp_path / "global"

    config_local = JupConfig(scope=ScopeType.LOCAL)
    assert get_scope_dir(config_local) == tmp_path / "local"


def test_get_skills_storage_dir(mock_jup_dir):
    storage_dir = get_skills_storage_dir()
    assert storage_dir == mock_jup_dir / "skills"
    assert storage_dir.exists()


def test_get_lockfile_path(mock_jup_dir, tmp_path):
    config_global = JupConfig(scope=ScopeType.GLOBAL)
    assert get_lockfile_path(config_global) == tmp_path / "global" / "skills.lock"

    config_local = JupConfig(scope=ScopeType.LOCAL)
    assert get_lockfile_path(config_local) == tmp_path / "local" / "skills.lock"


def test_get_skills_lock_default(mock_jup_dir):
    config = JupConfig()
    lock = get_skills_lock(config)
    assert isinstance(lock, SkillsLock)
    assert lock.sources == {}


def test_save_and_get_skills_lock(mock_jup_dir):
    config = JupConfig()
    lock = SkillsLock()
    from jup.models import SkillSource

    lock.sources["owner/repo"] = SkillSource(
        repo="owner/repo", category="test", skills=["skill1"]
    )

    save_skills_lock(config, lock)
    loaded_lock = get_skills_lock(config)
    assert "owner/repo" in loaded_lock.sources
    assert loaded_lock.sources["owner/repo"].skills == ["skill1"]
