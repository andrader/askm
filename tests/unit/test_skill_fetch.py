import json
from unittest.mock import MagicMock, patch
import urllib.request
import urllib.error
from jup.commands import fetch_remote_skill_md


def test_fetch_remote_skill_md_recursive_search():
    def side_effect(url_or_req):
        if isinstance(url_or_req, urllib.request.Request):
            url = url_or_req.full_url
        else:
            url = url_or_req

        # Fail all standard paths
        if "raw.githubusercontent.com" in url:
            if "deep/path/myskill/SKILL.md" in url:
                mock_response = MagicMock()
                mock_response.read.return_value = b"# Found via search"
                mock_response.__enter__.return_value = mock_response
                return mock_response
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)  # type: ignore

        # Mock GitHub API tree
        if "api.github.com" in url:
            mock_response = MagicMock()
            tree_data = {
                "tree": [
                    {"path": "some/other/file.txt", "type": "blob"},
                    {"path": "deep/path/myskill/SKILL.md", "type": "blob"},
                ]
            }
            mock_response.read.return_value = json.dumps(tree_data).encode()
            mock_response.__enter__.return_value = mock_response
            return mock_response

        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)  # type: ignore

    with patch("urllib.request.urlopen", side_effect=side_effect):
        # Test recursive search
        content = fetch_remote_skill_md("owner/repo", "myskill")
        assert content == "# Found via search"


def test_fetch_remote_skill_md_priority():
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.read.return_value = b"# Priority Content"
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response

        # Test priority
        # Even with internal_path, skills/myskill/SKILL.md should be tried first
        content = fetch_remote_skill_md(
            "owner/repo", "myskill", internal_path="other/path"
        )
        assert content == "# Priority Content"

        # Check that the first call was to the standard path
        args, _ = mock_url.call_args_list[0]
        if isinstance(args[0], urllib.request.Request):
            url = args[0].full_url
        else:
            url = args[0]
        assert (
            "raw.githubusercontent.com/owner/repo/main/skills/myskill/SKILL.md" in url
        )


def test_fetch_remote_skill_md_no_skill_name():
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.read.return_value = b"# Root Content"
        mock_response.__enter__.return_value = mock_response
        mock_url.return_value = mock_response

        # Test without skill_name
        content = fetch_remote_skill_md("owner/repo")
        assert content == "# Root Content"

        # Check that it tried SKILL.md
        args, _ = mock_url.call_args_list[0]
        if isinstance(args[0], urllib.request.Request):
            url = args[0].full_url
        else:
            url = args[0]
        assert "raw.githubusercontent.com/owner/repo/main/SKILL.md" in url


def test_fetch_remote_skill_md_internal_path():
    with patch("urllib.request.urlopen") as mock_url:
        mock_response = MagicMock()
        mock_response.read.return_value = b"# Internal Content"
        mock_response.__enter__.return_value = mock_response

        # We want to fail the first few calls to see if it tries the internal path
        # 1. skills/myskill/SKILL.md -> fail
        # 2. skills/myskill/SKILL.md (master) -> fail
        # 3. internal/SKILL.md -> success

        side_effect_calls = []

        def side_effect(url_or_req):
            if isinstance(url_or_req, urllib.request.Request):
                url = url_or_req.full_url
            else:
                url = url_or_req

            side_effect_calls.append(url)
            if "internal/myskill/SKILL.md" in url:
                return mock_response
            raise Exception("Not found")

        mock_url.side_effect = side_effect

        content = fetch_remote_skill_md(
            "owner/repo", "myskill", internal_path="internal"
        )
        assert content == "# Internal Content"

        # Check tried paths
        assert any("skills/myskill/SKILL.md" in u for u in side_effect_calls)
        assert any("internal/SKILL.md" in u for u in side_effect_calls)
        assert any("internal/myskill/SKILL.md" in u for u in side_effect_calls)


def test_fetch_remote_skill_md_failure_message():
    with patch("urllib.request.urlopen") as mock_url:
        mock_url.side_effect = Exception("Not found")

        # Test failure message
        content = fetch_remote_skill_md(
            "owner/repo", "myskill", internal_path="internal"
        )

        assert "SKILL.md not found in owner/repo" in content
        assert "- skills/myskill/SKILL.md" in content
        assert "- internal/SKILL.md" in content
        assert "- internal/myskill/SKILL.md" in content
        assert "- SKILL.md" in content
