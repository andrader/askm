import subprocess
import concurrent.futures
import os
import shutil
from pathlib import Path
import json

def run_jup_add(skill_path, home_dir):
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    # Use --verbose to see details if it fails
    cmd = ["uv", "run", "jup", "add", skill_path, "--scope", "user", "--category", "chaos", "--verbose"]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    return result

def main():
    home_dir = Path.cwd() / "tmp_chaos_home"
    if home_dir.exists():
        shutil.rmtree(home_dir)
    home_dir.mkdir()
    
    # Pre-initialize jup to avoid race on directory creation
    env = os.environ.copy()
    env["HOME"] = str(home_dir)
    subprocess.run(["uv", "run", "jup", "--version"], env=env, capture_output=True)

    skill_paths = [str(Path.cwd() / f"repro/race_skills/skill{i}") for i in range(1, 11)]
    
    print(f"Running 10 concurrent 'jup add' commands...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_jup_add, p, home_dir) for p in skill_paths]
        results = [f.result() for f in futures]
    
    success_count = 0
    for i, r in enumerate(results):
        if r.returncode != 0:
            print(f"Command {i} failed with return code {r.returncode}")
            print(f"STDERR snippet: {r.stderr[-200:]}")
        else:
            success_count += 1
    
    print(f"Success count: {success_count}/10")

    # Find the lockfile
    lock_files = list(home_dir.glob("**/skills.lock"))
    if lock_files:
        lock_file = lock_files[0]
        print(f"Found lockfile at: {lock_file}")
        content = lock_file.read_text()
        data = json.loads(content)
        sources = data.get("sources", {})
        print(f"Number of sources in lockfile: {len(sources)}")
        if len(sources) < success_count:
            print(f"DATA LOSS DETECTED! Expected {success_count} sources, found {len(sources)}")
        elif len(sources) == 10:
            print("Perfect! All 10 sources accounted for.")
        else:
            print(f"Found {len(sources)} sources.")
    else:
        print("Lockfile NOT FOUND")

if __name__ == "__main__":
    main()
