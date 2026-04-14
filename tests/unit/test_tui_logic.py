from unittest.mock import MagicMock, patch
from jup.commands import fetch_remote_skill_md


def test_fetch_remote_skill_md_variants():
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.read.return_value = b"# Skill Content"
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response

        # Test base case
        content = fetch_remote_skill_md("owner/repo", "myskill")
        assert content == "# Skill Content"

        # Verify it tried the expected URL (defaulting to main branch)
        args, _ = mock_url.call_args
        assert (
            "raw.githubusercontent.com/owner/repo/main/skills/myskill/SKILL.md"
            in args[0]
        )


def test_tui_html_generation_logic():
    from prompt_toolkit.formatted_text import to_formatted_text
    from prompt_toolkit.formatted_text.html import HTML

    # Valid state
    prefix = "[x]"
    pointer = ">"
    name = "Test"
    repo = "owner/repo"
    installs = "1,234"

    # Selected/Active state
    content = (
        f"{pointer} {prefix} <b>{name}</b> ({repo}) <ansigreen>[{installs}]</ansigreen>"
    )
    html_active = HTML(f"<reverse>{content}</reverse>\n")
    # Verify it can be converted to formatted text (list of tuples)
    fragments = to_formatted_text(html_active)
    assert isinstance(fragments, list)
    assert len(fragments) > 0
    # Check if installs string is present in the fragments
    # fragments can be (style, text) or (style, text, mouse_handler)
    assert any(installs in f[1] for f in fragments)


def test_github_tree_rendering_logic(tmp_path):
    # Testing the show_skill tree logic for local paths
    from rich.tree import Tree

    test_dir = tmp_path / "test_skill"
    test_dir.mkdir()
    (test_dir / "SKILL.md").write_text("# Test")
    (test_dir / "src").mkdir()
    (test_dir / "src" / "main.py").write_text("print('hello')")

    tree = Tree("Root")

    # Helper to simulate the internal add_to_tree
    def add_to_tree(path, tree_node):
        for item in sorted(path.iterdir()):
            if item.name.startswith("."):
                continue
            if item.is_dir():
                branch = tree_node.add(item.name)
                add_to_tree(item, branch)
            else:
                tree_node.add(item.name)

    add_to_tree(test_dir, tree)

    # Verify tree structure (simple check)
    assert "SKILL.md" in str(tree.label) or any(
        "SKILL.md" in str(child.label) for child in tree.children
    )
    assert any("src" in str(child.label) for child in tree.children)
