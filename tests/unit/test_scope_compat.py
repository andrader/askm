import json
from src.jup.config import get_config
from src.jup.models import JupConfig, ScopeType


def test_global_scope_backward_compatibility(monkeypatch, tmp_path):
    # Setup a mock config directory
    monkeypatch.setattr("src.jup.config.JUP_CONFIG_DIR", tmp_path)

    config_file = tmp_path / "config.json"

    # Write an old-style config with scope='global' and some other settings to verify they aren't lost
    old_config = {
        "scope": "global",
        "harnesses": ["custom-harness"],
        "sync-mode": "copy",
    }
    config_file.write_text(json.dumps(old_config))

    config = get_config()

    # Verify it mapped 'global' to 'user' without losing other settings
    assert config.scope == ScopeType.USER
    assert config.harnesses == ["custom-harness"]
    assert config.sync_mode == "copy"


def test_jup_config_model_validation():
    # Directly test the model
    old_json = '{"scope": "global", "harnesses": ["custom"]}'
    config = JupConfig.model_validate_json(old_json)

    assert config.scope == ScopeType.USER
    assert config.harnesses == ["custom"]
