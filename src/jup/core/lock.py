import contextlib
from pathlib import Path

import portalocker

from .filesystem import rel_home


class LockFileManager:
    def __init__(self, lock_file_path: Path):
        self.lock_file_path = lock_file_path
        self._lock_file = None

    @contextlib.contextmanager
    def lock(self, write: bool = True):
        """
        Context manager for file locking.
        Uses portalocker so the same advisory-locking semantics work on both
        POSIX (fcntl backend) and Windows (msvcrt backend).
        """
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        # We need a separate file for the lock to avoid issues with reading/writing the actual JSON
        lock_path = self.lock_file_path.with_suffix(".lock.lck")

        mode = "w" if write else "r"
        try:
            with open(lock_path, mode) as f:
                lock_type = portalocker.LOCK_EX if write else portalocker.LOCK_SH
                try:
                    portalocker.lock(f, lock_type)
                    yield f
                finally:
                    portalocker.unlock(f)
        except (OSError, portalocker.exceptions.LockException) as e:
            raise RuntimeError(f"Could not acquire lock on {rel_home(lock_path)}: {e}")
