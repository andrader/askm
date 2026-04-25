import shutil
from pathlib import Path
from unittest.mock import patch
from rich.console import Console
from typer.testing import CliRunner
from jup.main import app
from jup.models import (
    JupConfig,
    ScopeType,
    SyncMode,
    HarnessConfig,
    SkillSource,
    SkillsLock,
)

# Set command name for help output
app.info.name = "jup"


def setup_mock_env(tmp_path):
    jup_dir = tmp_path / ".jup"
    jup_dir.mkdir(parents=True, exist_ok=True)

    # Mock config
    config = JupConfig(
        scope=ScopeType.USER,
        harnesses=["gemini", "claude", "copilot"],
        sync_mode=SyncMode.LINK,
    )
    config_file = jup_dir / "config.json"
    config_file.write_text(config.model_dump_json())

    # Mock harness directories
    harnesses = {
        "gemini": tmp_path / "gemini" / "skills",
        "claude": tmp_path / "claude" / "skills",
        "copilot": tmp_path / "copilot" / "skills",
        ".agents": tmp_path / "agents" / "skills",
    }

    for p in harnesses.values():
        p.mkdir(parents=True, exist_ok=True)

    # Mock lockfile - should be in the default harness directory (get_scope_dir)
    lock = SkillsLock(
        version="0.1.0",
        sources={
            "kepano/obsidian-skills": SkillSource(
                repo="kepano/obsidian-skills",
                source_type="github",
                category="productivity",
                skills=["obsidian-cli", "obsidian-markdown"],
                version="v1.2.3",
                last_updated="2026-04-20T10:00:00",
                source="https://github.com/kepano/obsidian-skills",
            ),
            "jup/example-skill": SkillSource(
                repo="jup/example-skill",
                source_type="github",
                category="misc",
                skills=["example-skill"],
                version="main",
                last_updated="2026-04-24T09:00:00",
                source="https://github.com/jup/example-skill",
            ),
        },
    )
    lock_file = harnesses[".agents"] / "skills.lock"
    lock_file.write_text(lock.model_dump_json())

    # Mock skill storage
    skills_storage = jup_dir / "skills"
    (
        skills_storage
        / "productivity"
        / "gh"
        / "kepano"
        / "obsidian-skills"
        / "obsidian-cli"
    ).mkdir(parents=True)
    (
        skills_storage
        / "productivity"
        / "gh"
        / "kepano"
        / "obsidian-skills"
        / "obsidian-markdown"
    ).mkdir(parents=True)
    (skills_storage / "misc" / "gh" / "jup" / "example-skill" / "example-skill").mkdir(
        parents=True
    )

    # Create symlinks for all skills in all harnesses to make them look "installed"
    for h_name, h_dir in harnesses.items():
        # obsidian-cli
        target_obsidian = (
            skills_storage
            / "productivity"
            / "gh"
            / "kepano"
            / "obsidian-skills"
            / "obsidian-cli"
        )
        (h_dir / "obsidian-cli").symlink_to(target_obsidian)

        # obsidian-markdown
        target_markdown = (
            skills_storage
            / "productivity"
            / "gh"
            / "kepano"
            / "obsidian-skills"
            / "obsidian-markdown"
        )
        (h_dir / "obsidian-markdown").symlink_to(target_markdown)

        # example-skill
        target_example = (
            skills_storage / "misc" / "gh" / "jup" / "example-skill" / "example-skill"
        )
        (h_dir / "example-skill").symlink_to(target_example)

    return jup_dir, harnesses


def generate_screenshots():
    tmp_base = Path("/tmp/jup_screenshots")
    if tmp_base.exists():
        shutil.rmtree(tmp_base)
    tmp_base.mkdir(parents=True)

    jup_dir, harnesses = setup_mock_env(tmp_base)

    mock_harnesses = {
        name: HarnessConfig(
            name=name, global_location=str(path), local_location=str(path)
        )
        for name, path in harnesses.items()
    }

    # Use a fixed width for all captures
    WIDTH = 100
    runner = CliRunner()

    # Helper to capture and save
    def capture_command(args, filename, title, show_cmd=None):
        console = Console(record=True, width=WIDTH, force_terminal=True)
        if show_cmd:
            console.print(f"[bold white]$ {show_cmd}[/bold white]")

        # Patch shutil.get_terminal_size to ensure Typer/Click/Rich use our fixed width
        with patch("shutil.get_terminal_size", return_value=(WIDTH, 24)):
            result = runner.invoke(app, args, env={"COLUMNS": str(WIDTH)})
            # Use Text.from_ansi to preserve colors and prevent double-wrapping
            from rich.text import Text

            console.print(Text.from_ansi(result.stdout))

        console.save_svg(f"docs/images/{filename}", title=title)
        print(f"Generated docs/images/{filename}")

    # 1. Help
    capture_command(["--help"], "help.svg", "jup help")

    # Define a clean rel_home for the screenshots
    def mock_rel_home(p):
        p_str = str(p)
        if "agents" in p_str:
            return "~/.agents/skills"
        if "gemini" in p_str:
            return "~/.gemini/skills"
        if "claude" in p_str:
            return "~/.claude/skills"
        if "copilot" in p_str:
            return "~/.copilot/skills"
        return p_str

    with (
        patch("pathlib.Path.home", return_value=tmp_base),
        patch("jup.config.JUP_CONFIG_DIR", jup_dir),
        patch("jup.config.DEFAULT_HARNESSES", mock_harnesses),
        patch("jup.models.DEFAULT_HARNESSES", mock_harnesses),
        patch("jup.commands.list.rel_home", side_effect=mock_rel_home),
    ):
        # 2. Config Show
        capture_command(
            ["config", "show"],
            "config_show.svg",
            "jup config show",
            show_cmd="jup config show",
        )

        # 3. List
        capture_command(["list"], "list.svg", "jup list", show_cmd="jup list")


if __name__ == "__main__":
    generate_screenshots()
