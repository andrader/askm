from jup.commands.add import parse_repo_arg


def test_normalization_case_insensitivity():
    # owner/repo and OWNER/repo should result in the same parsing (lower-cased by add_skill later)
    # Actually parse_repo_arg itself doesn't lower case, add_skill does.
    # But let's check that they parse identically.
    res1 = parse_repo_arg("owner/repo")
    res2 = parse_repo_arg("OWNER/repo")

    assert res1 == ("owner", "repo", None, None, False)
    assert res2 == ("OWNER", "repo", None, None, False)


def test_normalization_redundant_slashes():
    assert parse_repo_arg("owner//repo") == ("owner", "repo", None, None, False)
    assert parse_repo_arg("owner/repo//path") == ("owner", "repo", "path", None, False)


def test_normalization_ssh_urls():
    # ssh://git@github.com/owner/repo.git should be recognized if it has userinfo/port
    assert parse_repo_arg("ssh://git@github.com/owner/repo.git") == (
        "owner",
        "repo",
        None,
        None,
        True,
    )
    assert parse_repo_arg("https://github.com:443/owner/repo") == (
        "owner",
        "repo",
        None,
        None,
        True,
    )


def test_normalization_complex_urls():
    url = "https://github.com/owner/repo/tree/main/path/to/skill?query=1#fragment"
    assert parse_repo_arg(url) == ("owner", "repo", "path/to/skill", "main", True)


def test_normalization_at_version_confusion():
    # Test @ symbol in path vs @ version suffix
    # https://github.com/owner/repo/tree/main/path@at -> version=main, subpath=path@at
    assert parse_repo_arg("https://github.com/owner/repo/tree/main/path@at") == (
        "owner",
        "repo",
        "path@at",
        "main",
        True,
    )

    # owner/repo/path@at@v1 -> owner=owner, repo=repo, path=path@at, version=v1
    assert parse_repo_arg("owner/repo/path@at@v1") == (
        "owner",
        "repo",
        "path@at",
        "v1",
        False,
    )
