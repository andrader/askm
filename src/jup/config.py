from pathlib import Path
import contextlib
import tempfile
import os
from rich import print
from .models import DEFAULT_HARNESSES, HarnessConfig, JupConfig, SkillsLock
from .core.lock import LockFileManager

JUP_CONFIG_DIR = Path(os.getenv("JUP_CONFIG_DIR", Path.home() / ".jup"))


def get_config() -> JupConfig:
    config_file = JUP_CONFIG_DIR / "config.json"
    if not config_file.exists():
        return JupConfig()
    try:
        json_bytes = config_file.read_bytes()
        return JupConfig.model_validate_json(json_bytes)
    except PermissionError:
        print(
            f"[red]Error: Permission denied when reading config from {config_file}[/red]"
        )
        raise
    except Exception:
        # Default config if corrupted
        return JupConfig()


def save_config(config: JupConfig):
    try:
        JUP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_file = JUP_CONFIG_DIR / "config.json"

        # Atomic write: write to temp file then rename
        with tempfile.NamedTemporaryFile("w", dir=JUP_CONFIG_DIR, delete=False) as tf:
            tf.write(config.model_dump_json(indent=4, by_alias=True))
            temp_name = tf.name
        os.replace(temp_name, config_file)
    except PermissionError:
        print(
            f"[red]Error: Permission denied when saving config to {JUP_CONFIG_DIR}[/red]"
        )
    except Exception as e:
        print(f"[red]Error: Failed to save config: {e}[/red]")


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
    return scope_dir / "skills.lock"


def get_lock_manager(config: JupConfig) -> LockFileManager:
    return LockFileManager(get_lockfile_path(config))


def get_skills_lock(config: JupConfig) -> SkillsLock:
    lock_file = get_lockfile_path(config)
    if not lock_file.exists():
        return SkillsLock()
    try:
        json_bytes = lock_file.read_bytes()
        return SkillsLock.model_validate_json(json_bytes)
    except PermissionError:
        print(
            f"[red]Error: Permission denied when reading skills lock from {lock_file}[/red]"
        )
        raise
    except Exception:
        return SkillsLock()


@contextlib.contextmanager
def skills_lock_session(config: JupConfig):
    """
    Context manager that yields a SkillsLock and automatically saves it on exit.
    Handles file locking for the entire session.
    """
    try:
        lm = get_lock_manager(config)
        with lm.lock(write=True):
            lock = get_skills_lock(config)
            yield lock
            save_skills_lock(config, lock)
    except Exception:
        raise


def save_skills_lock(config: JupConfig, lock: SkillsLock):
    try:
        lock_file = get_lockfile_path(config)
        lock_file.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write: write to temp file then rename
        with tempfile.NamedTemporaryFile("w", dir=lock_file.parent, delete=False) as tf:
            tf.write(lock.model_dump_json(indent=4))
            temp_name = tf.name
        os.replace(temp_name, lock_file)
    except PermissionError:
        print(
            f"[red]Error: Permission denied when saving skills lock to {lock_file}[/red]"
        )
    except Exception as e:
        print(f"[red]Error: Failed to save skills lock: {e}[/red]")
