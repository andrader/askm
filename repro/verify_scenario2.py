import os
import shutil
from pathlib import Path
import subprocess
import time
import json

def test_list_performance():
    test_home = Path.cwd() / "tmp_test_scenario2"
    if test_home.exists():
        shutil.rmtree(test_home)
    test_home.mkdir(parents=True)
    
    jup_dir = test_home / ".jup"
    agents_dir = test_home / ".agents"
    jup_dir.mkdir()
    agents_dir.mkdir()
    
    env = os.environ.copy()
    env["HOME"] = str(test_home)
    
    num_skills = 200
    print(f"Creating {num_skills} mock skills...")
    
    # Create skills in storage and in lockfile
    skills_storage = jup_dir / "skills" / "misc" / "local"
    skills_storage.mkdir(parents=True)
    
    skills_list = []
    for i in range(num_skills):
        name = f"skill_{i:03d}"
        skill_path = skills_storage / name
        skill_path.mkdir()
        (skill_path / "SKILL.md").write_text(f"# {name}")
        skills_list.append(name)
        
        # Link some of them to .agents to simulate installed status
        if i % 2 == 0:
            (agents_dir / name).symlink_to(skill_path)

    lock_content = {
        "sources": {
            "mock_source": {
                "source_type": "local",
                "source_path": str(skills_storage),
                "source_layout": "collection",
                "skills": skills_list,
                "category": "misc",
                "last_updated": "2023-01-01T00:00:00"
            }
        }
    }
    
    with open(agents_dir / "skills.lock", "w") as f:
        json.dump(lock_content, f)
        
    print("Running 'jup list'...")
    start_time = time.time()
    res = subprocess.run(
        ["uv", "run", "python", "-m", "jup.main", "list"],
        env=env,
        capture_output=True,
        text=True
    )
    end_time = time.time()
    
    print(f"Time taken for {num_skills} skills: {end_time - start_time:.4f}s")
    # print("STDOUT:", res.stdout)
    
    assert res.returncode == 0
    # For O(N), 200 skills should be very fast (usually < 1s even with uv run overhead)
    assert end_time - start_time < 5.0 # Loose bound considering CI overhead
    print("Scenario 2 verified!")

if __name__ == "__main__":
    test_list_performance()
