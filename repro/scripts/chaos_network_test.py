import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import urllib.error

# Add src to sys.path
sys.path.insert(0, str(Path.cwd() / "src"))

from jup.commands.show import show_skill

class ChaosNetworkTest(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_show_network_down(self, mock_urlopen):
        # Simulate network error
        mock_urlopen.side_effect = urllib.error.URLError("No internet connection")
        
        print("\n--- Testing Show with Network Down ---")
        try:
            # show_skill uses print and Console, so we might want to capture output
            show_skill("owner/repo")
            print("show_skill finished")
        except Exception as e:
            print(f"Caught crash in show_skill: {type(e).__name__}: {e}")

    @patch("urllib.request.urlopen")
    def test_show_api_rate_limit(self, mock_urlopen):
        # Simulate 403 Forbidden (often rate limit)
        mock_response = MagicMock()
        mock_response.__enter__.side_effect = urllib.error.HTTPError(
            "https://api.github.com/...", 403, "Forbidden", {}, None
        )
        mock_urlopen.side_effect = urllib.error.HTTPError(
            "https://api.github.com/...", 403, "Forbidden", {}, None
        )
        
        print("\n--- Testing Show with API Rate Limit ---")
        try:
            show_skill("owner/repo")
            print("show_skill finished")
        except Exception as e:
            print(f"Caught crash in show_skill: {type(e).__name__}: {e}")

if __name__ == "__main__":
    unittest.main()
