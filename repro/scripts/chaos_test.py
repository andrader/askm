import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

# Add src to sys.path
sys.path.insert(0, str(Path.cwd() / "src"))

from jup.config import get_config, save_config
from jup.models import JupConfig, ScopeType

class ChaosTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path.cwd() / "tmp_chaos"
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        self.jup_dir = self.test_dir / ".jup"
        self.jup_dir.mkdir()
        
    def tearDown(self):
        if self.test_dir.exists():
            # Fix permissions if we broke them
            os.chmod(self.jup_dir, 0o755)
            shutil.rmtree(self.test_dir)

    def test_corrupted_config(self):
        print("\n--- Testing Corrupted Config ---")
        config_file = self.jup_dir / "config.json"
        config_file.write_text("{ invalid json")
        
        with patch("jup.config.JUP_CONFIG_DIR", self.jup_dir):
            config = get_config()
            print(f"Config after corruption: {config}")
            self.assertIsInstance(config, JupConfig)
            # Should be default
            self.assertEqual(config.scope, ScopeType.USER)

    def test_unwritable_config_dir(self):
        print("\n--- Testing Unwritable Config Dir ---")
        os.chmod(self.jup_dir, 0o555) # Read and execute, no write
        
        with patch("jup.config.JUP_CONFIG_DIR", self.jup_dir):
            try:
                # get_config should still work (read-only)
                config = get_config()
                print("get_config worked on unwritable dir")
                
                # save_config should fail
                print("Attempting save_config on unwritable dir...")
                save_config(config)
                print("save_config unexpectedly worked!")
            except Exception as e:
                print(f"Caught expected exception in save_config: {type(e).__name__}: {e}")

    def test_missing_home(self):
        print("\n--- Testing Missing HOME ---")
        # JUP_CONFIG_DIR is defined at module level:
        # JUP_CONFIG_DIR = Path.home() / ".jup"
        # So we need to re-import or patch it before it's used.
        # But wait, it's already imported.
        
        with patch.dict(os.environ, {}, clear=True):
            try:
                # Path.home() might fail if HOME is missing
                home = Path.home()
                print(f"Path.home() returned {home} even with empty env")
            except Exception as e:
                print(f"Path.home() failed as expected: {e}")

    def test_invalid_harness_location(self):
        print("\n--- Testing Invalid Harness Location ---")
        from jup.config import get_scope_dir
        config = JupConfig(scope=ScopeType.USER)
        # Mock a harness with a path that can't be expanded (e.g. ~nonexistentuser)
        # Actually expanduser just returns it if it can't expand.
        
        with patch("jup.config.DEFAULT_HARNESSES", {
            ".agents": type('Harness', (), {'global_location': '~nonexistentuser/skills', 'local_location': './skills'})
        }):
            try:
                scope_dir = get_scope_dir(config)
                print(f"Scope dir: {scope_dir}")
            except Exception as e:
                print(f"get_scope_dir failed: {e}")

if __name__ == "__main__":
    unittest.main()
