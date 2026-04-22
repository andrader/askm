import time
from concurrent.futures import ProcessPoolExecutor
from jup.core.lock import LockFileManager


def acquire_lock_and_hold(lock_path, duration):
    lm = LockFileManager(lock_path)
    with lm.lock(write=True):
        time.sleep(duration)
        return True


def test_lock_file_exclusive(tmp_path):
    lock_file = tmp_path / "test.lock"

    # Start a process that holds the lock
    with ProcessPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(acquire_lock_and_hold, lock_file, 0.5)

        # Give it a moment to acquire the lock
        time.sleep(0.1)

        # Try to acquire it again - this should block
        start_time = time.time()
        f2 = executor.submit(acquire_lock_and_hold, lock_file, 0.1)

        assert f1.result() is True
        assert f2.result() is True

        end_time = time.time()
        # The total time should be at least f1 duration + f2 duration (approx)
        # because f2 had to wait for f1 to finish.
        assert end_time - start_time >= 0.5


def test_atomic_write_simulation(tmp_path):
    import os

    # Manually test the os.replace logic
    target_file = tmp_path / "config.json"
    temp_file = tmp_path / "config.json.tmp"

    target_file.write_text("OLD")
    temp_file.write_text("NEW")

    os.replace(temp_file, target_file)

    assert target_file.read_text() == "NEW"
    assert not temp_file.exists()
