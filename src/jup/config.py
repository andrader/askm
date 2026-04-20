from pathlib import Path
from .models import DEFAULT_HARNESSES, HarnessConfig, JupConfig, SkillsLock

JUP_CONFIG_DIR = Path.home() / ".jup"
CONFIG_FILE = JUP_CONFIG_DIR / "config.json"


def get_config() -> JupConfig:
    if not CONFIG_FILE.exists():
        return JupConfig()
    try:
        json_bytes = CONFIG_FILE.read_bytes()
        return JupConfig.model_validate_json(json_bytes)
    except Exception:
        # Default config if corrupted
        return JupConfig()


def save_config(config: JupConfig):
    JUP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        f.write(config.model_dump_json(indent=4, by_alias=True))


def get_all_harnesses(config: JupConfig) -> dict[str, HarnessConfig]:
    """Merge default harnesses with custom providers from config."""
    all_harnesses = DEFAULT_HARNESSES.copy()
    if config.custom_harnesses:
        all_harnesses.update(config.custom_harnesses)
    return all_harnesses


def get_scope_dir(config: JupConfig, harness_name: str | None = None) -> Path:
    """
    Return the skills directory for the given config and optional harness.
    """
    all_harnesses = get_all_harnesses(config)
    harness_key = (
        harness_name if harness_name and harness_name in all_harnesses else ".agents"
    )
    harness_config = all_harnesses[harness_key]

    if config.scope == "local":
        return Path(harness_config.local_location).expanduser().resolve()

    return Path(harness_config.global_location).expanduser().resolve()


def get_skills_storage_dir() -> Path:
    """Internal storage for all downloaded skills globally."""
    storage = JUP_CONFIG_DIR / "skills"
    storage.mkdir(parents=True, exist_ok=True)
    return storage


def get_lockfile_path(config: JupConfig) -> Path:
    scope_dir = get_scope_dir(config)
    scope_dir.mkdir(parents=True, exist_ok=True)
    return scope_dir / "skills.lock"


def get_skills_lock(config: JupConfig) -> SkillsLock:
    lock_file = get_lockfile_path(config)
    if not lock_file.exists():
        return SkillsLock()
    try:
        json_bytes = lock_file.read_bytes()
        return SkillsLock.model_validate_json(json_bytes)
    except Exception:
        return SkillsLock()


def save_skills_lock(config: JupConfig, lock: SkillsLock):
    lock_file = get_lockfile_path(config)
    with open(lock_file, "w") as f:
        f.write(lock.model_dump_json(indent=4))
