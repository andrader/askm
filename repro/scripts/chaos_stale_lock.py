import os
import fcntl
import subprocess
import time
from pathlib import Path

def main():
    home_dir = Path.cwd() / "tmp_stale_home"
    if home_dir.exists():
        import shutil
        shutil.rmtree(home_dir)
    home_dir.mkdir()
    
    lock_path = home_dir / "test.lock.lck"
    
    print(f"Acquiring lock on {lock_path} and crashing...")
    # Simulate a process that acquires the lock and then SIGKILLs itself
    code = f"""
import fcntl, os, time
f = open('{lock_path}', 'w')
fcntl.flock(f.fileno(), fcntl.LOCK_EX)
print('Locked')
os.kill(os.getpid(), 9)
"""
    proc = subprocess.Popen(["python3", "-c", code], stdout=subprocess.PIPE)
    line = proc.stdout.readline()
    print(f"Child said: {line.decode().strip()}")
    proc.wait()
    
    print(f"Child process ended. Lock file exists: {lock_path.exists()}")
    
    # Now try to run jup add which will try to acquire the same lock path (if we set it up)
    # Actually let's just use a python script that uses the LockFileManager
    
    print("Trying to acquire lock from another process...")
    code2 = f"""
import fcntl, os
from pathlib import Path
import sys
# Add src to path
sys.path.append('src')
from jup.core.lock import LockFileManager

lpath = Path('{home_dir}/test.lock')
lm = LockFileManager(lpath)
print('Attempting lock...')
with lm.lock(write=True):
    print('Lock acquired successfully!')
"""
    result = subprocess.run(["python3", "-c", code2], capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    else:
        print("Stale lock test passed!")

if __name__ == "__main__":
    main()
