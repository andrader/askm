import os
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

# Add src to sys.path
sys.path.insert(0, str(Path.cwd() / "src"))

from jup.commands.sync import sync_logic
from jup.models import JupConfig, ScopeType, SkillsLock, SkillSource

class ChaosSyncTest(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path.cwd() / "tmp_chaos_sync"
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        
        self.fake_home = self.test_dir / "home"
        self.fake_home.mkdir()
        self.jup_dir = self.fake_home / ".jup"
        self.jup_dir.mkdir()
        
        self.global_skills = self.fake_home / ".agents" / "skills"
        self.global_skills.parent.mkdir(parents=True)
        
        self.storage_dir = self.jup_dir / "skills"
        self.storage_dir.mkdir()

    def tearDown(self):
        if self.test_dir.exists():
            # Fix permissions
            for root, dirs, files in os.walk(self.test_dir):
                for d in dirs:
                    os.chmod(os.path.join(root, d), 0o755)
            shutil.rmtree(self.test_dir)

    @patch("jup.config.JUP_CONFIG_DIR")
    @patch("jup.config.DEFAULT_HARNESSES")
    def test_sync_unwritable_target(self, mock_harnesses, mock_jup_dir):
        from jup.models import HarnessConfig
        mock_jup_dir.return_value = self.jup_dir # Wait, JUP_CONFIG_DIR is a Path object in the module
        
        # Need to patch the actual objects in jup.config
        with patch("jup.config.JUP_CONFIG_DIR", self.jup_dir), \
             patch("jup.config.get_skills_storage_dir", return_value=self.storage_dir), \
             patch("jup.config.DEFAULT_HARNESSES", {
                 ".agents": HarnessConfig(name=".agents", global_location=str(self.global_skills), local_location="./skills")
             }), \
             patch("jup.commands.sync.get_scope_dir", return_value=self.global_skills):
            
            # Setup a skill in storage
            skill_dir = self.storage_dir / "misc" / "test-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("Test Skill")
            
            # Setup lockfile
            lock = SkillsLock(sources={
                "test-source": SkillSource(
                    source_type="local",
                    source_path=str(skill_dir),
                    skills=["test-skill"],
                    source_layout="single"
                )
            })
            from jup.config import save_skills_lock
            config = JupConfig(scope=ScopeType.USER)
            save_skills_lock(config, lock)
            
            # Make target dir unwritable
            self.global_skills.mkdir(parents=True, exist_ok=True)
            os.chmod(self.global_skills, 0o555)
            
            print("\n--- Testing Sync to Unwritable Target ---")
            try:
                sync_logic(config=config)
                print("sync_logic unexpectedly finished without error!")
            except Exception as e:
                print(f"Caught expected crash in sync_logic: {type(e).__name__}: {e}")

    @patch("jup.config.JUP_CONFIG_DIR")
    def test_sync_target_is_file(self, mock_jup_dir):
        # If the target skills directory is actually a file
        with patch("jup.config.JUP_CONFIG_DIR", self.jup_dir), \
             patch("jup.config.get_skills_storage_dir", return_value=self.storage_dir), \
             patch("jup.commands.sync.get_scope_dir", return_value=self.global_skills):
            
            # Make global_skills a file
            self.global_skills.parent.mkdir(parents=True, exist_ok=True)
            self.global_skills.write_text("I am a file, not a directory")
            
            config = JupConfig(scope=ScopeType.USER)
            
            print("\n--- Testing Sync when Target is a File ---")
            try:
                sync_logic(config=config)
                print("sync_logic unexpectedly finished without error!")
            except Exception as e:
                print(f"Caught expected crash in sync_logic: {type(e).__name__}: {e}")

if __name__ == "__main__":
    unittest.main()
