import os
import shutil
from pathlib import Path
import subprocess

def run_jup(args):
    return subprocess.run(["uv", "run", "jup"] + args, capture_output=True, text=True)

def test_add_custom_dir():
    # Setup
    test_home = Path.cwd() / "tmp_test_scenario1"
    if test_home.exists():
        shutil.rmtree(test_home)
    test_home.mkdir(parents=True)
    
    jup_dir = test_home / ".jup"
    agents_dir = test_home / ".agents"
    custom_dir = test_home / "custom_skills"
    
    jup_dir.mkdir()
    agents_dir.mkdir()
    custom_dir.mkdir()
    
    env = os.environ.copy()
    env["HOME"] = str(test_home)
    # We need to make sure jup uses this HOME
    
    # Create a dummy local skill
    skill_src = test_home / "my_skill"
    skill_src.mkdir()
    (skill_src / "SKILL.md").write_text("# My Skill")
    
    print(f"Adding skill with --dir {custom_dir}...")
    # Use jup add --dir
    # Note: we need to run it in a way that respects the new HOME
    # We'll use a script to run jup with mocked HOME if needed, 
    # but since I'm running in this environment, I'll just point to it.
    
    # Actually, jup's JUP_CONFIG_DIR is Path.home() / ".jup"
    # I'll use a python script to run the command with monkeypatched home if possible,
    # or just trust the current environment if I can control it.
    
    # Let's try to run it via subprocess with HOME env var
    res = subprocess.run(
        ["uv", "run", "python", "-m", "jup.main", "add", str(skill_src), "--dir", str(custom_dir)],
        env=env,
        capture_output=True,
        text=True
    )
    
    print("STDOUT:", res.stdout)
    print("STDERR:", res.stderr)
    
    # Check results
    installed_in_custom = (custom_dir / "my_skill").exists()
    installed_in_agents = (agents_dir / "my_skill").exists()
    
    print(f"Installed in custom: {installed_in_custom}")
    print(f"Installed in agents: {installed_in_agents}")
    
    assert installed_in_custom, "Skill should be in custom_dir"
    assert not installed_in_agents, "Skill should NOT be in default .agents dir when --dir is used"
    print("Scenario 1 verified!")

if __name__ == "__main__":
    test_add_custom_dir()
