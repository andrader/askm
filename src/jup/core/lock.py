import fcntl
import contextlib
from pathlib import Path
from .filesystem import rel_home


class LockFileManager:
    def __init__(self, lock_file_path: Path):
        self.lock_file_path = lock_file_path
        self._lock_file = None

    @contextlib.contextmanager
    def lock(self, write: bool = True):
        """
        Context manager for file locking.
        Uses fcntl for Unix-based systems.
        """
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)
        # We need a separate file for the lock to avoid issues with reading/writing the actual JSON
        lock_path = self.lock_file_path.with_suffix(".lock.lck")

        mode = "w" if write else "r"
        try:
            with open(lock_path, mode) as f:
                lock_type = fcntl.LOCK_EX if write else fcntl.LOCK_SH
                try:
                    fcntl.flock(f.fileno(), lock_type)
                    yield f
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except IOError as e:
            raise RuntimeError(f"Could not acquire lock on {rel_home(lock_path)}: {e}")
