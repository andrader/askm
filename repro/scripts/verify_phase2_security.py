import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("src"))

from jup.core.filesystem import validate_path
from jup.commands.add import parse_repo_arg

def test_path_traversal_version():
    print("Testing Scenario 1: Path traversal in @version")
    storage_base = Path("/tmp/jup-test/skills").resolve()
    storage_base.mkdir(parents=True, exist_ok=True)
    
    category = "misc"
    gh_prefix = "gh"
    owner = "owner"
    repo_name = "repo"
    
    # Simulate: jup add owner/repo@../../../etc
    repo_arg = "owner/repo@../../../etc"
    parsed = parse_repo_arg(repo_arg)
    if not parsed:
        print("parse_repo_arg returned None (expected if it thinks it's a local path)")
        # If it returns None, add_skill treats it as a local path.
        # But owner/repo@... doesn't exist locally.
        return

    owner, repo_name, parsed_path, version_resolved, is_url = parsed
    print(f"Parsed: owner={owner}, repo={repo_name}, version={version_resolved}")
    
    target_dir = storage_base / category / gh_prefix / owner / repo_name
    
    print(f"Constructed target_dir: {target_dir}")
    
    try:
        if version_resolved:
            target_dir = target_dir.with_name(f"{repo_name}-{version_resolved}")
        print(f"Target dir after with_name: {target_dir}")
    except ValueError as e:
        print(f"SUCCESS: pathlib.Path.with_name caught the traversal attempt: {e}")
        return

    try:
        validated = validate_path(target_dir, storage_base)
        print(f"Validated path: {validated}")
        if storage_base not in validated.parents and validated != storage_base:
             print("FAILURE: Path escaped storage_base but was validated!")
        else:
             print("SUCCESS: Path stayed within storage_base (as far as validate_path is concerned)")
    except ValueError as e:
        print(f"SUCCESS: Caught expected ValueError: {e}")

def test_validate_path_escaping():
    print("\nTesting Scenario 3: validate_path escaping base_dir")
    base_dir = Path("/tmp/jup-test/base").resolve()
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Try absolute path outside
    try:
        validate_path(Path("/etc/passwd"), base_dir)
        print("FAILURE: Absolute path outside base_dir was validated!")
    except ValueError as e:
        print(f"SUCCESS: Caught absolute path: {e}")
        
    # Try relative path with traversal
    try:
        validate_path(base_dir / ".." / ".." / "etc" / "passwd", base_dir)
        print("FAILURE: Relative traversal outside base_dir was validated!")
    except ValueError as e:
        print(f"SUCCESS: Caught relative traversal: {e}")

    # Try symlink
    secret_dir = Path("/tmp/jup-test/secret").resolve()
    secret_dir.mkdir(parents=True, exist_ok=True)
    (secret_dir / "flag.txt").write_text("SECRET")
    
    symlink_path = base_dir / "evil_link"
    if not symlink_path.exists():
        os.symlink(secret_dir, symlink_path)
    
    try:
        # validate_path(base_dir / "evil_link" / "flag.txt", base_dir)
        # Path("...").resolve() follows symlinks.
        validate_path(symlink_path / "flag.txt", base_dir)
        print("FAILURE: Symlink escaping base_dir was validated!")
    except ValueError as e:
        print(f"SUCCESS: Caught symlink escape: {e}")

def test_path_traversal_owner_repo():
    print("\nTesting Scenario 4: Path traversal in owner/repo shorthand")
    storage_base = Path("/tmp/jup-test/skills").resolve()
    if storage_base.exists():
        import shutil
        shutil.rmtree(storage_base)
    storage_base.mkdir(parents=True, exist_ok=True)
    
    # Create some dummy content to see if it gets deleted
    (storage_base / "misc").mkdir()
    (storage_base / "misc" / "important").mkdir()
    (storage_base / "misc" / "important" / "SKILL.md").write_text("IMPORTANT")
    
    category = "misc"
    gh_prefix = "gh"
    
    # Simulate: jup add ../../repo
    repo_arg = "../../repo"
    parsed = parse_repo_arg(repo_arg)
    if not parsed:
        print("SUCCESS: parse_repo_arg returned None for ../../repo (likely treated as local or invalid)")
    else:
        owner, repo_name, parsed_path, version_resolved, is_url = parsed
        print(f"Parsed: owner={owner}, repo={repo_name}")
        
        target_dir = storage_base / category / gh_prefix / owner / repo_name
        print(f"Constructed target_dir: {target_dir}")
        print(f"Resolved target_dir: {target_dir.resolve()}")
        
        try:
            validate_path(target_dir, storage_base)
            print("WARNING: validate_path allowed ../../repo traversal!")
            if target_dir.resolve() == storage_base / category:
                print("CRITICAL: target_dir resolves to category dir! rmtree would be disastrous.")
        except ValueError as e:
            print(f"SUCCESS: validate_path caught owner/repo traversal: {e}")

if __name__ == "__main__":
    test_path_traversal_version()
    test_validate_path_escaping()
    test_path_traversal_owner_repo()
