import os
import shutil
from pathlib import Path
import subprocess

def test_permission_error_read():
    test_home = Path.cwd() / "tmp_test_scenario3"
    if test_home.exists():
        shutil.rmtree(test_home)
    test_home.mkdir(parents=True)
    
    jup_dir = test_home / ".jup"
    jup_dir.mkdir()
    config_file = jup_dir / "config.json"
    config_file.write_text('{"scope": "local"}')
    
    # Make config file unreadable
    config_file.chmod(0o000)
    
    env = os.environ.copy()
    env["HOME"] = str(test_home)
    
    print("Running 'jup list' with unreadable config...")
    res = subprocess.run(
        ["uv", "run", "python", "-m", "jup.main", "list"],
        env=env,
        capture_output=True,
        text=True
    )
    
    print("STDOUT:", res.stdout)
    print("STDERR:", res.stderr)
    
    # Clean up chmod so we can delete the dir later
    config_file.chmod(0o600)

    # Currently it might just return default config silently.
    # The requirement is "rich error message instead of a stack trace".
    # If it is silent, it is not "rich error message".
    
    # Check if "Permission denied" or similar is in stdout/stderr
    has_rich_error = "Permission denied" in res.stdout or "Permission denied" in res.stderr
    print(f"STDOUT: {res.stdout}")
    print(f"STDERR: {res.stderr}")
    print(f"Has rich error message: {has_rich_error}")
    
    assert has_rich_error, "Should have a rich error message for PermissionError"
    print("Scenario 3 verified!")
