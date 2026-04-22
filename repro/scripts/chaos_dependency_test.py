import unittest
from unittest.mock import patch
from pathlib import Path
import sys

# Add src to sys.path
sys.path.insert(0, str(Path.cwd() / "src"))

from jup.commands.add import add_skill

class ChaosDependencyTest(unittest.TestCase):
    @patch("subprocess.run")
    def test_add_missing_git(self, mock_run):
        # Simulate git not found
        mock_run.side_effect = FileNotFoundError("[Errno 2] No such file or directory: 'git'")
        
        print("\n--- Testing Add with Missing Git ---")
        try:
            # We need to mock a few more things to get to the git clone part
            with patch("jup.commands.add.get_config"), \
                 patch("jup.commands.add.get_skills_lock"), \
                 patch("jup.commands.add.get_skills_storage_dir"):
                add_skill("owner/repo")
            print("add_skill finished")
        except FileNotFoundError as e:
            print(f"CRASH: Caught FileNotFoundError in add_skill: {e}")
        except Exception as e:
            print(f"Caught other exception in add_skill: {type(e).__name__}: {e}")

if __name__ == "__main__":
    unittest.main()
