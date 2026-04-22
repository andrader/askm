from jup.commands.add import parse_repo_arg
from pathlib import Path
from unittest.mock import patch

def test_path_traversal():
    print("Testing Path Traversal vulnerability in parse_repo_arg")
    
    with patch("jup.commands.add.Path") as mock_path_class:
        mock_path_instance = mock_path_class.return_value
        mock_path_instance.expanduser.return_value.exists.return_value = False
        
        # Test shorthand with traversal
        input_arg = "owner/repo/../../../../etc"
        parsed = parse_repo_arg(input_arg)
        print(f"Input: {input_arg}")
        print(f"Parsed: {parsed}")
        
        if parsed:
            owner, repo, subpath, version, is_url = parsed
            temp_path = Path("/tmp/jup-clone-123")
            skills_dir = (temp_path / subpath).resolve()
            print(f"Base temp path: {temp_path}")
            print(f"Resolved skills_dir: {skills_dir}")
            
            if not str(skills_dir).startswith(str(temp_path)):
                print("VULNERABILITY: path traversal detected! skills_dir is outside temp_path")
            else:
                print("OK: skills_dir is within temp_path")

if __name__ == "__main__":
    test_path_traversal()
