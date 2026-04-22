import subprocess
from pathlib import Path

def run_jup_add(skill_path):
    # Use -y or similar if needed, but 'add' for local doesn't seem to prompt unless in harness dir
    return subprocess.Popen(["uv", "run", "jup", "add", skill_path, "--category", "repro"])

if __name__ == "__main__":
    p1 = Path("repro/skill1").resolve()
    p2 = Path("repro/skill2").resolve()
    
    # Clean up old lock if any
    lock_file = Path.home() / ".agents/skills/skills.lock" # Default for .agents harness in user scope
    # Wait, let's check where the lock file actually is.
    # get_scope_dir returns global_location if scope is user.
    # DEFAULT_HARNESSES['.agents'].global_location = "~/.agents/skills"
    if lock_file.exists():
        lock_file.unlink()

    print(f"Starting parallel jup add for {p1} and {p2}")
    proc1 = run_jup_add(str(p1))
    proc2 = run_jup_add(str(p2))
    
    proc1.wait()
    proc2.wait()
    
    if lock_file.exists():
        content = lock_file.read_text()
        print("Lock file content:")
        print(content)
        
        count = 0
        if str(p1) in content:
            count += 1
            print("Skill 1 found")
        if str(p2) in content:
            count += 1
            print("Skill 2 found")
            
        if count == 1:
            print("SUCCESS: Race condition reproduced! One skill is missing.")
        elif count == 2:
            print("FAILURE: Both skills found. Race condition not reproduced (luck or timing).")
        else:
            print("FAILURE: No skills found.")
    else:
        print("FAILURE: Lock file not created.")
