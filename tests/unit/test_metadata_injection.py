from jup.commands.add import inject_metadata


def test_missing_frontmatter(tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("# My Skill\n\nSome content.")

    inject_metadata(skill_file, "https://github.com/a/b", "v1.0")

    content = skill_file.read_text()
    assert (
        content
        == "---\nsource: https://github.com/a/b\nversion: v1.0\n---\n\n# My Skill\n\nSome content."
    )


def test_malformed_yaml_frontmatter(tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("---\nbad_yaml: [\n# My Skill")

    inject_metadata(skill_file, "https://github.com/a/b", "v1.0")

    content = skill_file.read_text()
    # We assert that the metadata is injected somehow or handled gracefully.
    # Currently, the script does nothing if it doesn't find the closing '---'.
    assert "source: https://github.com/a/b" in content


def test_empty_file(tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("")

    inject_metadata(skill_file, "https://github.com/a/b", "v1.0")

    content = skill_file.read_text()
    assert content == "---\nsource: https://github.com/a/b\nversion: v1.0\n---\n"


def test_file_without_newlines(tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("---")

    inject_metadata(skill_file, "https://github.com/a/b", None)

    content = skill_file.read_text()
    assert "source: https://github.com/a/b" in content


def test_duplicate_keys(tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("---\nsource: old_url\nversion: old_version\n---\n# Content")

    inject_metadata(skill_file, "https://github.com/a/b", "new_version")

    content = skill_file.read_text()
    # It should replace the existing keys, not duplicate them.
    assert content.count("source:") == 1
    assert content.count("version:") == 1
    assert "source: https://github.com/a/b" in content
    assert "version: new_version" in content
