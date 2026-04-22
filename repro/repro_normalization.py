from jup.commands.add import parse_repo_arg
from unittest.mock import patch

def test_scenario_1():
    print("Testing Scenario 1: Redundant slashes, trailing .git, and SSH URLs (ssh://)")
    
    with patch("jup.commands.add.Path") as mock_path_class:
        mock_path_instance = mock_path_class.return_value
        mock_path_instance.expanduser.return_value.exists.return_value = False
        
        cases = [
            ("https://github.com/owner//repo///", ("owner", "repo", None, None, True)),
            ("https://github.com/owner/repo.git", ("owner", "repo", None, None, True)),
            ("ssh://github.com/owner/repo", ("owner", "repo", None, None, True)),
            ("ssh://github.com/owner/repo.git", ("owner", "repo", None, None, True)),
            ("ssh://git@github.com/owner/repo", ("owner", "repo", None, None, True)),
            ("https://github.com:443/owner/repo", ("owner", "repo", None, None, True)),
            ("owner//repo//", ("owner", "repo", None, None, False)),
        ]
        
        for input_arg, expected in cases:
            actual = parse_repo_arg(input_arg)
            print(f"Input: {input_arg}")
            print(f"Expected: {expected}")
            print(f"Actual:   {actual}")
            assert actual == expected, f"Failed for {input_arg}"
            print("OK")

def test_scenario_2():
    print("\nTesting Scenario 2: owner/repo vs https://github.com/owner/repo.git")
    
    with patch("jup.commands.add.Path") as mock_path_class:
        mock_path_instance = mock_path_class.return_value
        mock_path_instance.expanduser.return_value.exists.return_value = False
        
        res1 = parse_repo_arg("owner/repo")
        res2 = parse_repo_arg("https://github.com/owner/repo.git")
        res3 = parse_repo_arg("OWNER/repo")
        
        print(f"owner/repo -> {res1}")
        print(f"https://github.com/owner/repo.git -> {res2}")
        print(f"OWNER/repo -> {res3}")
        
        def get_source_key(parsed):
            if not parsed: return None
            owner, repo_name, path, version, is_url = parsed
            key = f"{owner}/{repo_name}"
            if path: key += f"/{path}"
            if version: key += f"@{version}"
            return key

        key1 = get_source_key(res1)
        key2 = get_source_key(res2)
        key3 = get_source_key(res3)
        
        print(f"Key 1: {key1}")
        print(f"Key 2: {key2}")
        print(f"Key 3: {key3}")
        assert key1 == key2, "Source keys should match for same repo regardless of format"
        if key1 != key3:
            print("VULNERABILITY: Case sensitivity in owner/repo leads to duplicate entries!")
        else:
            print("OK: Case insensitive match")

def test_scenario_3():
    print("\nTesting Scenario 3: @ symbols in repo names or subpaths")
    
    with patch("jup.commands.add.Path") as mock_path_class:
        mock_path_instance = mock_path_class.return_value
        mock_path_instance.expanduser.return_value.exists.return_value = False
        
        cases = [
            # @ in subpath
            ("owner/repo/path@with@at/skill", ("owner", "repo", "path@with@at/skill", None, False)),
            # @ in repo name (not allowed by GitHub but let's see how we handle it)
            ("owner/repo@name/skill", ("owner", "repo@name", "skill", None, False)),
            # URL with @ in subpath
            ("https://github.com/owner/repo/tree/main/path@at", ("owner", "repo", "path@at", "main", True)),
        ]
        
        for input_arg, expected in cases:
            actual = parse_repo_arg(input_arg)
            print(f"Input: {input_arg}")
            print(f"Expected: {expected}")
            print(f"Actual:   {actual}")
            # assert actual == expected, f"Failed for {input_arg}"
            if actual == expected:
                print("OK")
            else:
                print("FAIL")

if __name__ == "__main__":
    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
    except AssertionError as e:
        print(f"Assertion failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
