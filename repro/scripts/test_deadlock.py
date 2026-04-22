import fcntl
import os
from pathlib import Path

def test_deadlock():
    lock_path = Path("test.lock.lck")
    if lock_path.exists():
        lock_path.unlink()
    
    print("Acquiring lock first time...")
    f1 = open(lock_path, "w")
    fcntl.flock(f1.fileno(), fcntl.LOCK_EX)
    print("Acquired first lock.")
    
    print("Attempting to acquire lock second time (different FD)...")
    # This should block if flock is not re-entrant on different FDs
    # We use a timeout to not hang forever
    import signal
    def handler(signum, frame):
        raise TimeoutError("Deadlock detected!")
    
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(2)
    
    try:
        f2 = open(lock_path, "w")
        fcntl.flock(f2.fileno(), fcntl.LOCK_EX)
        print("Acquired second lock (Surprise!)")
    except TimeoutError as e:
        print(f"FAILED: {e}")
    finally:
        signal.alarm(0)

if __name__ == "__main__":
    test_deadlock()
