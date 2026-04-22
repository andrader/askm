import subprocess
import concurrent.futures
import os
import shutil
from pathlib import Path
import json

def run_jup_config(key, value, home_dir):
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    cmd = ["uv", "run", "jup", "config", "set", key, value]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return result

def main():
    home_dir = Path.cwd() / "tmp_config_home"
    if home_dir.exists():
        shutil.rmtree(home_dir)
    home_dir.mkdir()
    
    # Initialize config
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    subprocess.run(["uv", "run", "jup", "config", "set", "sync_mode", "link"], env=env)

    print(f"Running 10 concurrent 'jup config set' commands...")
    # Each command sets a different custom harness (if supported) or just different keys if available
    # Actually let's just try to set the same key to different values and see if it crashes or something
    # But better: try to set different keys to see if one is LOST.
    
    # Wait, jup config set only supports known keys? 
    # Let's see src/jup/commands/config_cli.py
    
    keys_values = [(f"harness_path_{i}", f"path_{i}") for i in range(10)]
    
    # Actually jup config set sync_mode is a good one.
    # But let's see if it supports arbitrary config? No, it's based on Pydantic model.
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_jup_config, "sync_mode", "copy" if i%2==0 else "link", home_dir) for i in range(10)]
        results = [f.result() for f in futures]
    
    for i, r in enumerate(results):
        if r.returncode != 0:
            print(f"Command {i} failed: {r.stderr}")

    print("Checking config file integrity...")
    config_file = home_dir / ".jup" / "config.json"
    if config_file.exists():
        try:
            content = config_file.read_text()
            json.loads(content)
            print("Config is valid JSON.")
        except Exception as e:
            print(f"Config is CORRUPTED: {e}")
    else:
        print("Config file not found!")

if __name__ == "__main__":
    main()
