import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("src"))

from jup.commands.utils import run_git_clone

def test_git_injection():
    print("Testing Scenario 2: Git argument injection in run_git_clone")
    dest_dir = Path("/tmp/jup-test/git-clone-test")
    if dest_dir.exists():
        import shutil
        shutil.rmtree(dest_dir)
    
    # Try un-whitelisted kwarg
    print("\nAttempting un-whitelisted kwarg: upload_pack='--help'")
    try:
        # This should ignore upload_pack
        run_git_clone("https://github.com/octocat/Spoon-Knife", dest_dir, upload_pack="--help")
        print("Completed (upload_pack should have been ignored)")
    except Exception as e:
        print(f"Error: {e}")

    if dest_dir.exists():
        import shutil
        shutil.rmtree(dest_dir)

    # Try whitelisted kwarg but with flag injection in value
    print("\nAttempting flag injection in whitelisted kwarg: branch='--help'")
    try:
        # This should ignore the value if it starts with '-'
        run_git_clone("https://github.com/octocat/Spoon-Knife", dest_dir, branch="--help")
        print("Completed (branch value '--help' should have been ignored)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_git_injection()
