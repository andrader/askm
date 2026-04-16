import json
from unittest.mock import MagicMock, patch
import urllib.request
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
            raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

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

        raise urllib.error.HTTPError(url, 404, "Not Found", {}, None)

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
